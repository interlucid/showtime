import math
import random

import config
import utils
import parse_midi

song_name = "forest_fire"
bpm = 98
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)


woo_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/woo.mid", bpm
)
woo_pixel_locations = {}


def fill_applicable_woos(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]

    # find the MIDI note that we're currently at
    for woo_index, woo in enumerate(woo_notes):
        note_start_time = woo["start_time"]
        duration = woo["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            ms_since_woo_start = note_start_time + duration - ms_since_song_start
            base_color = (100, 20, 0)
            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                0,
                (1 - ms_since_woo_start / duration) * config.num_pixels,
                utils.get_fade_in_out_color(ms_since_woo_start, duration, base_color),
                hardness=0,
                add=True,
            )


piano_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/piano.mid", bpm
)
piano_pixel_locations = {}
num_piano_sectors = 20


def fill_applicable_pianos(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]

    # find the MIDI note that we're currently at
    for piano_index, piano in enumerate(piano_notes):
        note_start_time = piano["start_time"]
        duration = piano["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            # don't allow for two of the same index to be sequential
            while piano_index not in piano_pixel_locations or (
                piano_index - 1 in piano_pixel_locations
                and piano_pixel_locations[piano_index]
                == piano_pixel_locations[piano_index - 1]
            ):
                piano_pixel_locations[piano_index] = random.randint(
                    0, num_piano_sectors - 1
                )
            ms_since_piano_start = note_start_time + duration - ms_since_song_start
            base_color = (250, 170, 0)

            utils.fill_pixels_in_range(
                sequence_config["pixels"],
                utils.get_sector_starting_pixel(
                    piano_pixel_locations[piano_index], num_piano_sectors
                ),
                utils.get_sector_ending_pixel(
                    piano_pixel_locations[piano_index], num_piano_sectors
                ),
                utils.get_fade_in_out_color(ms_since_piano_start, duration, base_color),
                hardness=0,
                add=True,
            )


guitar_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/guitar.mid", bpm
)
guitar_fx_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/guitar_fx.mid", bpm
)
guitar_pixel_locations = {}
num_guitar_sectors = 10
guitar_fx_sine_scalar = 3


def fill_applicable_guitars(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]

    # find the MIDI note that we're currently at
    for guitar_index, guitar in enumerate(guitar_notes):
        note_start_time = guitar["start_time"]
        duration = guitar["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            # don't allow for two of the same index to be sequential
            while guitar_index not in guitar_pixel_locations or (
                guitar_index - 1 in guitar_pixel_locations
                and guitar_pixel_locations[guitar_index]
                == guitar_pixel_locations[guitar_index - 1]
            ):
                guitar_pixel_locations[guitar_index] = random.randint(
                    0, num_guitar_sectors - 1
                )
            ms_since_guitar_start = note_start_time + duration - ms_since_song_start
            base_color = (250, 70, 0)
            fx_are_on = any(
                map(
                    lambda fx_note: ms_since_song_start >= fx_note["start_time"]
                    and ms_since_song_start
                    <= fx_note["start_time"] + fx_note["duration"],
                    guitar_fx_notes,
                )
            )
            fx_color = (
                (
                    tuple(
                        map(
                            lambda x: x
                            * (
                                math.sin(ms_since_guitar_start / 50)
                                / guitar_fx_sine_scalar
                                + (guitar_fx_sine_scalar - 1) / guitar_fx_sine_scalar
                            ),
                            base_color,
                        )
                    )
                )
                if fx_are_on
                else base_color
            )

            utils.fill_pixels_in_range(
                sequence_config["pixels"],
                utils.get_sector_starting_pixel(
                    guitar_pixel_locations[guitar_index], num_guitar_sectors
                ),
                utils.get_sector_ending_pixel(
                    guitar_pixel_locations[guitar_index], num_guitar_sectors
                ),
                utils.get_fade_in_out_color(ms_since_guitar_start, duration, fx_color),
                hardness=0,
                add=True,
            )


pulse_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/pulse.mid", bpm
)
pulse_sectors_map = {}
pulse_note_values = map(lambda midi_note: midi_note["note"], pulse_notes)
unique_pulse_notes = list(set(pulse_note_values))
for note_index, note in enumerate(unique_pulse_notes):
    pulse_sectors_map[note] = note_index
num_pulse_sectors = len(pulse_sectors_map)


def fill_applicable_pulses(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]

    # find the MIDI note that we're currently at
    for pulse_index, pulse in enumerate(pulse_notes):
        note_start_time = pulse["start_time"]
        duration = pulse["duration"]
        note = pulse["note"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            ms_since_pulse_start = note_start_time + duration - ms_since_song_start
            base_color = (230, 90, 10)

            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                utils.get_sector_starting_pixel(
                    pulse_sectors_map[note], num_pulse_sectors
                ),
                utils.get_sector_ending_pixel(
                    pulse_sectors_map[note], num_pulse_sectors
                ),
                utils.get_fade_in_out_color(
                    ms_since_pulse_start, duration, base_color, 0.5
                ),
                hardness=0,
                add=True,
            )


def play_current_frame(sequence_config):
    fill_applicable_woos(sequence_config)
    fill_applicable_pianos(sequence_config)
    fill_applicable_guitars(sequence_config)
    fill_applicable_pulses(sequence_config)
