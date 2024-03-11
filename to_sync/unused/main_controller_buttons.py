# SPDX-FileCopyrightText: 2023 Brandon for Interlucid
# SPDX-License-Identifier: NO LICENSE

# main controller for NeoPixels on Raspberry Pi and VLC audio
# this process must be run with non-root privileges
# it will spin up another root-privileged process to control LEDs

import asyncio
import board
import digitalio
import os
import pprint
import requests
import subprocess
import sys
import threading
import time
import vlc

import utils

pp = pprint.PrettyPrinter(indent=4)

# set up button listeners

button_back = digitalio.DigitalInOut(board.D25)
button_back.direction = digitalio.Direction.INPUT
button_back.pull = digitalio.Pull.UP

button_play = digitalio.DigitalInOut(board.D24)
button_play.direction = digitalio.Direction.INPUT
button_play.pull = digitalio.Pull.UP

button_forward = digitalio.DigitalInOut(board.D12)
button_forward.direction = digitalio.Direction.INPUT
button_forward.pull = digitalio.Pull.UP

global available_songs_in_order
available_songs_in_order = [
    "a_thousand_spies",
    "forest_fire",
    "just_cant_find_it",
    "prison_wall",
    "tell_me_no",
    "falling_in_love",
    "your_dream",
    "feel",
    "pressure",
    "who_you_are",
    "unlimited",
    "keys",
    "now_that_youre_gone",
    "sail_above",
    "fog_in_the_trees",
    "dream_killa",
]
song_medias_in_order = list(
    map(lambda song: vlc.Media(f"backing_songs/{song}.wav"), available_songs_in_order)
)
current_song_index = 0

# i1 = vlc.Instance("--verbose=2")

global media
media = vlc.MediaPlayer()


# start the LED server in a thread so we can print the output to this process's stdout without blocking
class LEDServerThread(threading.Thread):
    def __init__(self, name="led_thread"):
        super(LEDServerThread, self).__init__(name=name)
        self.start()

    def run(self):
        led_server_process = subprocess.Popen(
            ["sudo", "flask", "--app", "led_server", "run", "--debug"],
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )
        print(f"sequence process spawned with PID: {led_server_process.pid}")
        while led_server_process.poll() is None:
            # this blocks until it receives a newline
            print("SERVER > ", led_server_process.stdout.readline())


ledServerThread = LEDServerThread()

# fog in the trees practice
# song_start_measure = 60
# forest fire
song_start_measure = 11
# dream killa
# song_start_measure = 37
# song_start_measure = 0
song_start_beat = song_start_measure * 4
# song_start_beat = 250

import importlib


def play_media():
    global media, current_song_index
    song_name = available_songs_in_order[current_song_index]
    # media = vlc.MediaPlayer(f"backing_songs/{song_name}.wav")
    media.set_media(song_medias_in_order[current_song_index])
    sequence_module = utils.get_sequence_module(song_name)
    skip_ms = round(song_start_beat * sequence_module.song_timing["song_beat_ms"])
    media.play()
    media.set_time(skip_ms)


def stop_media():
    global media
    media.stop()


async def play_show():
    # stop show in case one is already playing
    loop = asyncio.get_event_loop()
    stop_request = loop.run_in_executor(
        None, requests.post, "http://localhost:5000/stop"
    )
    await stop_request
    show_delay_ms = 500
    playback_start_time = utils.get_now_millis() + show_delay_ms
    threading.Timer(show_delay_ms / 1000, play_media).start()
    # send a timestamp of the show delay milliseconds from now when media.play starts to the LED server so it can match the light sequence
    requests.post(
        "http://localhost:5000/start",
        params={
            "song_name": available_songs_in_order[current_song_index],
            "playback_start_time": playback_start_time,
            "song_start_beat": song_start_beat,
        },
    )


def stop_show():
    global media
    media.stop()
    requests.post("http://localhost:5000/stop")


global button_back_lock, button_play_lock, button_forward_lock
button_play_lock = False
button_back_lock = False
button_forward_lock = False


# post update, check buttons, and sleep for 1 ms
def handle_buttons():
    # print(button_back.value)
    # print(button_play.value)
    # print(button_forward.value)
    global available_songs_in_order, current_song_index, button_back_lock, button_play_lock, button_forward_lock, media
    if not button_back.value and not button_back_lock:
        button_back_lock = True
        # if a song has been playing for more than 3 seconds
        if media.get_time() > 3000:
            # restart the song
            media.set_time(0)
        else:
            # select the previous song
            current_song_index -= 1
            if current_song_index < 0:
                current_song_index = len(available_songs_in_order) - 1
            print(f"current song is {available_songs_in_order[current_song_index]}")
            # if a song is playing
            if media.is_playing():
                # start playing the previous song
                asyncio.run(play_show())

    if not button_play.value and not button_play_lock:
        # only process one event per press
        button_play_lock = True
        # if a song is playing
        if media.is_playing():
            # stop for now, maybe pause eventually
            stop_show()
        # else
        else:
            # play the current song
            asyncio.run(play_show())

    if not button_forward.value and not button_forward_lock:
        button_forward_lock = True
        # select the next song
        current_song_index += 1
        if current_song_index >= len(available_songs_in_order):
            current_song_index = 0
        print(f"current song is {available_songs_in_order[current_song_index]}")
        # if a song is playing
        if media.is_playing():
            # start playing the next song
            asyncio.run(play_show())

    # allow additional events once released

    if button_back.value:
        button_back_lock = False

    if button_play.value:
        button_play_lock = False

    if button_forward.value:
        button_forward_lock = False


while True:
    handle_buttons()
    time.sleep(0.1)
