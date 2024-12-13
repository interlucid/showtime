# number of NeoPixels in the strip
num_pixels = 99
dark_pixels_size = 2
dark_pixels_start = num_pixels / 2 - dark_pixels_size / 2
dark_pixels_end = num_pixels / 2 + dark_pixels_size / 2

# led brightness
led_brightness = 1

# number of milliseconds between each animation frame
sleep_ms = 5

working_directory = "/home/interlucid/Music/neopixels"
sequences_directory = f"{working_directory}/sequences"

song_start_measure = 0
# song_start_measure = 20
song_start_beat = song_start_measure * 4
# song_start_beat = 250


set_30_min = [
    # "keys",
    #
    "a_thousand_spies",
    # "forest_fire",
    "just_cant_find_it",
    # "prison_wall",
    # "tell_me_no",
    # "falling_in_love",
    "your_dream",
    # "feel",
    # "pressure",
    # "who_you_are",
    "unlimited",
    "keys",
    # "now_that_youre_gone",
    "sail_above",
    "fog_in_the_trees",
    "dream_killa",
]

set_60_min = [
    "a_thousand_spies",
    "forest_fire",
    "just_cant_find_it",
    "fog_in_the_trees",
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
    # "bullet_train",
    "sail_above",
    "dream_killa",
]

set = set_60_min
