# SPDX-FileCopyrightText: 2023 Brandon for Interlucid
# SPDX-License-Identifier: NO LICENSE

# LED controller for NeoPixels on Raspberry Pi

import board
import flask
import math
import neopixel
import random
import threading
import time
import traceback

import config
import utils

app = flask.Flask(__name__)
app.debug = True

global should_loop, ledThread, song_name, sequence_module, song, playback_start_time, song_start_beat
should_loop = False

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D21


# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, config.num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER
)


class LEDThread(threading.Thread):
    # params:
    # song_measure_ms: how many milliseconds are in each measure of this particular song
    # playback_start_time: when we should start the light sequence
    # song_start_beat: the beat of the song where playback should start
    def __init__(self):
        super(LEDThread, self).__init__()
        self.start()

    def run(self):
        global should_loop, song_name, sequence_module, song_skip_ms, playback_start_time, song_start_beat

        print("about to start light sequence loop")

        while True:
            # wait to see if we should loop later if not now
            if not should_loop:
                # pixels.fill((0, 0, 0))
                # pixels.show()
                # time.sleep(0.01)
                continue
                # print("stopping light sequence")
                # return
            # don't start the light sequence until playback has started
            if utils.get_now_millis() < playback_start_time:
                time.sleep(0.001)
                continue

            # start blank by default
            # this takes care of turning off pixels so we don't have to do that all the time otherwise
            pixels.fill((0, 0, 0))

            if hasattr(sequence_module, "song_measure_ms"):
                song_measure_ms = sequence_module.song_measure_ms
            else:
                song_measure_ms = None
            song = utils.get_current_song_playback_timing(
                playback_start_time - song_skip_ms, song_measure_ms
            )
            if hasattr(sequence_module, "song_timing"):
                song_timing = sequence_module.song_timing
            else:
                song_timing = None
            sequence_config = utils.get_sequence_config(song, pixels, song_timing)

            # play the current frame of the sequence
            try:
                sequence_module.play_current_frame(sequence_config)
            except Exception:
                traceback.print_exc()
                should_loop = False
                pass

            pixels.show()

            # sleep because humans can only track changes to a few hundred Hz anyway
            # time.sleep(0.1)
            time.sleep(config.sleep_ms / 1000)

            # rainbow_cycle(0.01)  # rainbow cycle with 1ms delay per step

            # time.sleep(0.25)

    def stop(self):
        global should_loop
        should_loop = False
        pixels.fill((0, 0, 0))
        pixels.show()


# start the thread; it will wait for commands
ledThread = LEDThread()

modules = {}


@app.get("/")
def hello_world():
    return "Flask LED server is running"


@app.post("/load_modules")
def load_modules():
    module_names = flask.request.json["module_names"]
    for module_name in module_names:
        modules[module_name] = utils.get_sequence_module(module_name)
    return "successfully loaded modules"


@app.post("/start")
def start_sequence():
    global should_loop, song_name, sequence_module, song_skip_ms, playback_start_time, song_start_beat
    song_name = flask.request.args.get("song_name")
    playback_start_time = int(flask.request.args.get("playback_start_time"))
    song_start_beat = int(flask.request.args.get("song_start_beat"))
    sequence_module = modules[song_name]
    if hasattr(sequence_module, "song_timing"):
        song_skip_ms = song_start_beat * sequence_module.song_timing["song_beat_ms"]
    else:
        song_skip_ms = sequence_module.beats_to_ms(song_start_beat)
    # reset if needed
    if hasattr(sequence_module, "init"):
        sequence_module.init()
    # start the LED thread
    should_loop = True
    return "Successfully started the LED sequence"


@app.post("/stop")
def stop_sequence():
    global should_loop
    should_loop = False
    pixels.fill((0, 0, 0))
    pixels.show()
    return "Successfully stopped the LED sequence"
