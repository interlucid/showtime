# SPDX-FileCopyrightText: 2023 Brandon for Interlucid
# SPDX-License-Identifier: NO LICENSE

# main controller for NeoPixels on Raspberry Pi and VLC audio
# this process must be run with non-root privileges
# it will spin up another root-privileged process to control LEDs

import adafruit_ssd1306
import asyncio
import board
import busio
import digitalio
import os

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

# from PIL import Image, ImageDraw
import pprint
import requests
import subprocess
import sys
import threading
import time
import vlc

import config
import utils

pp = pprint.PrettyPrinter(indent=4)

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = PIL.Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = PIL.ImageDraw.Draw(image)
arial_font = PIL.ImageFont.truetype(
    f"{config.working_directory}/fonts/arial.ttf", size=20
)
# test code
# draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  # Up
# disp.image(image)
# disp.show()

# set up button listeners

button_A = digitalio.DigitalInOut(board.D5)
button_A.direction = digitalio.Direction.INPUT
button_A.pull = digitalio.Pull.UP

button_B = digitalio.DigitalInOut(board.D6)
button_B.direction = digitalio.Direction.INPUT
button_B.pull = digitalio.Pull.UP

button_L = digitalio.DigitalInOut(board.D27)
button_L.direction = digitalio.Direction.INPUT
button_L.pull = digitalio.Pull.UP

button_R = digitalio.DigitalInOut(board.D23)
button_R.direction = digitalio.Direction.INPUT
button_R.pull = digitalio.Pull.UP

button_U = digitalio.DigitalInOut(board.D17)
button_U.direction = digitalio.Direction.INPUT
button_U.pull = digitalio.Pull.UP

button_D = digitalio.DigitalInOut(board.D22)
button_D.direction = digitalio.Direction.INPUT
button_D.pull = digitalio.Pull.UP

button_C = digitalio.DigitalInOut(board.D4)
button_C.direction = digitalio.Direction.INPUT
button_C.pull = digitalio.Pull.UP


global available_songs_in_order
available_songs_in_order = config.set

# song_type = "busking_songs"
song_type = "concert"
song_medias_in_order = []


def update_song_medias_in_order():
    global song_medias_in_order
    print(
        f"smio: {song_medias_in_order}, st: {song_type}, asio: {available_songs_in_order}",
        flush=True,
    )
    song_medias_in_order = list(
        map(
            lambda song: vlc.Media(
                f"{config.working_directory}/{song_type}_songs/{song}.wav"
            ),
            available_songs_in_order,
        )
    )


# run once to initialize
update_song_medias_in_order()


current_song_index = 0

global time_since_last_display_update
time_since_last_display_update = time.time()


def display_text(text, x=10, y=10):
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, y), text, fill=150, font=arial_font)
    disp.image(image)
    disp.show()
    global time_since_last_display_update
    time_since_last_display_update = time.time()


def display_current_song():
    display_text(available_songs_in_order[current_song_index].replace("_", " ").title())


def display_current_mode():
    display_text(song_type, 10, 30)


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

modules = {}
for module_name in available_songs_in_order:
    modules[module_name] = utils.get_sequence_module(module_name)

# wait for server to come online and then load all the modules
while True:
    try:
        # keep trying to request the homepage until it succeeds
        requests.get("http://localhost:5000/")
        break
    except Exception:
        time.sleep(0.5)
        pass

# load the modules beforehand since it takes like 2-3 seconds each and we don't want to do it when the song is starting
requests.post(
    "http://localhost:5000/load_modules",
    json={"module_names": available_songs_in_order},
)


def play_media():
    print("playing media")
    global media, current_song_index
    song_name = available_songs_in_order[current_song_index]
    # media = vlc.MediaPlayer(f"busking_songs/{song_name}.wav")
    media.set_media(song_medias_in_order[current_song_index])
    sequence_module = modules[song_name]
    if hasattr(sequence_module, "song_timing"):
        skip_ms = round(
            config.song_start_beat * sequence_module.song_timing["song_beat_ms"]
        )
    else:
        skip_ms = int(sequence_module.beats_to_ms(config.song_start_beat))
    print(f"skip_ms is {skip_ms}")
    media.play()
    media.set_time(skip_ms)
    print(media.get_time())


def stop_media():
    global media
    media.stop()


connection_error_message = "Unable to connect to the server. You might need to wait a few seconds if the server is still starting."


async def play_show():
    try:
        # stop show in case one is already playing
        loop = asyncio.get_event_loop()
        stop_request = loop.run_in_executor(
            None, requests.post, "http://localhost:5000/stop"
        )
        await stop_request
        show_delay_ms = 5
        # show_delay_ms = 500
        playback_start_time = utils.get_now_millis() + show_delay_ms
        threading.Timer(show_delay_ms / 1000, play_media).start()
        # send a timestamp of the show delay milliseconds from now when media.play starts to the LED server so it can match the light sequence
        requests.post(
            "http://localhost:5000/start",
            params={
                "song_name": available_songs_in_order[current_song_index],
                "playback_start_time": playback_start_time,
                "song_start_beat": int(config.song_start_beat),
            },
        )
    except requests.exceptions.ConnectionError:
        print(connection_error_message)


def stop_show():
    global media
    media.stop()
    try:
        requests.post("http://localhost:5000/stop")
    except requests.exceptions.ConnectionError:
        print(connection_error_message)


global button_A_lock, button_B_lock, button_L_lock, button_R_lock, button_U_lock, button_D_lock
button_A_lock = False
button_B_lock = False
button_L_lock = False
button_R_lock = False
button_U_lock = False
button_D_lock = False


# post update, check buttons, and sleep for 1 ms
def handle_buttons():
    global time_since_last_display_update
    if time_since_last_display_update < time.time() - 10:
        # turn off display
        disp.fill(0)
        disp.show()
    # print(button_L.value)
    # print(button_A.value)
    # print(button_R.value)
    global available_songs_in_order
    global current_song_index
    global song_type
    global button_A_lock
    global button_B_lock
    global button_L_lock
    global button_R_lock
    global button_U_lock
    global button_D_lock
    global media

    if not button_A.value and not button_A_lock:
        # only process one event per press
        button_A_lock = True
        # if a song is playing
        if media.is_playing():
            # stop for now, maybe pause eventually
            stop_show()
        # else
        else:
            # play the current song
            asyncio.run(play_show())

    if not button_B.value and not button_B_lock:
        # only process one event per press
        button_B_lock = True
        display_current_song()

    if not button_L.value and not button_L_lock:
        button_L_lock = True
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
            display_current_song()
            # if a song is playing
            if media.is_playing():
                # start playing the previous song
                asyncio.run(play_show())

    if not button_R.value and not button_R_lock:
        button_R_lock = True
        # select the next song
        current_song_index += 1
        if current_song_index >= len(available_songs_in_order):
            current_song_index = 0
        print(f"current song is {available_songs_in_order[current_song_index]}")
        display_current_song()
        # if a song is playing
        if media.is_playing():
            # start playing the next song
            asyncio.run(play_show())

    if not button_U.value and not button_U_lock:
        button_U_lock = True
        # change mode between busking and concert
        song_type = "concert" if song_type == "busking" else "busking"
        update_song_medias_in_order()
        display_current_mode()

    # allow additional events once released

    if button_A.value:
        button_A_lock = False

    if button_B.value:
        button_B_lock = False

    if button_L.value:
        button_L_lock = False

    if button_R.value:
        button_R_lock = False

    if button_U.value:
        button_U_lock = False

    if button_D.value:
        button_D_lock = False


display_current_song()

while True:
    handle_buttons()
    time.sleep(0.1)
