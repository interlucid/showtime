import random

import config
import utils
import parse_midi

song_name = "who_you_are"
bpm = 90
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

e_piano_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/e_piano.mid", bpm
)
e_piano_pixel_locations = {}
num_e_piano_sectors = 26
e_piano_duration_extension = 800


def fill_applicable_e_pianos(sequence_config):
    song = sequence_config["song"]
    for e_piano_index, e_piano in enumerate(e_piano_notes):
        ms_since_song_start = song["ms_since_song_start"]
        note_start_time = e_piano["start_time"]
        duration = e_piano["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start
            < note_start_time + duration + e_piano_duration_extension
        ):
            # don't let two consecutive locations be the same
            if e_piano_index not in e_piano_pixel_locations:
                e_piano_pixel_locations[e_piano_index] = random.randint(
                    0, num_e_piano_sectors - 1
                )
            ms_since_fade_start = ms_since_song_start - note_start_time
            utils.fill_pixels_in_range(
                sequence_config["pixels"],
                utils.get_sector_starting_pixel(
                    e_piano_pixel_locations[e_piano_index], num_e_piano_sectors
                ),
                utils.get_sector_ending_pixel(
                    e_piano_pixel_locations[e_piano_index], num_e_piano_sectors
                ),
                utils.get_fade_in_out_color(
                    ms_since_fade_start,
                    duration + e_piano_duration_extension,
                    (20, 225, 100),
                ),
                hardness=0,
                add=True,
            )


def play_current_frame(sequence_config):
    fill_applicable_e_pianos(sequence_config)
