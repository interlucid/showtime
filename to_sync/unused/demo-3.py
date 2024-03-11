# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple test for NeoPixels on Raspberry Pi
import board
import neopixel
import threading
import time

global should_loop
should_loop = True

class StdinThread(threading.Thread):

    def __init__(self, input_cbk = None, name='stdin-thread'):
        self.input_cbk = input_cbk
        super(StdinThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            print("hi")
            # waits to get input + Return
            try:
                self.input_cbk(input())
            except EOFError:
                continue

def handle_stdin(input):
    global should_loop
    if(input == "stop"):
        should_loop = False
        pixels.fill((0, 0, 0))
        pixels.show()
    if(input == "start"):
        should_loop = True
    print('You Entered:', input)

# start the Keyboard thread
stdinThread = StdinThread(handle_stdin)

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D21

# The number of NeoPixels
num_pixels = 60

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

# actual value
# dream_killa_measure_ms = 1463

# fudged value for TikTok
dream_killa_measure_ms = 1380
loop_time = dream_killa_measure_ms / 4
current_measure_ms = 1
old_color_value = 0

# pixels.fill((0, 0, 0))
# pixels.show()

while(True):
    if(not should_loop):
        current_measure_ms = 0
        time.sleep(.5)
        continue
    current_measure_ms = current_measure_ms - 1
    if(current_measure_ms <= 0):
        current_measure_ms = loop_time
    new_color_value = round(255 * (current_measure_ms / loop_time))
    if(new_color_value == old_color_value): continue
    pixels.fill((new_color_value, 0, 0))
    # pixels.fill((255, 0, 0, 0))
    pixels.show()
    time.sleep(.001)

    # pixels.fill((0, 0, 0))
    # # Uncomment this line if you have RGBW/GRBW NeoPixels
    # # pixels.fill((255, 0, 0, 0))
    # pixels.show()
    # time.sleep(1.463)

    # # Comment this line out if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 255, 0))
    # # Uncomment this line if you have RGBW/GRBW NeoPixels
    # # pixels.fill((0, 255, 0, 0))
    # pixels.show()
    # time.sleep(1)

    # # Comment this line out if you have RGBW/GRBW NeoPixels
    # pixels.fill((0, 0, 255))
    # # Uncomment this line if you have RGBW/GRBW NeoPixels
    # # pixels.fill((0, 0, 255, 0))
    # pixels.show()
    # time.sleep(1)

    # rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step
