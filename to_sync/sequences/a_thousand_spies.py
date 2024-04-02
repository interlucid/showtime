import math
import random

import config
import utils
import parse_midi

song_name = "a_thousand_spies"
bpm = 118
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)


baum_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/baum.mid", bpm
)


def fill_applicable_baums(sequence_config):
    song = sequence_config["song"]

    # find the MIDI note that we're currently at
    for baum in baum_notes:
        note_start_time = baum["start_time"]
        duration = baum["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            ms_since_fade_start = (
                note_start_time + duration - song["ms_since_song_start"]
            )
            sequence_config["pixels"].fill(
                utils.get_fade_out_color(
                    ms_since_fade_start,
                    duration,
                    (255, 20, 0),
                )
            )
            break


doo_dee_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/doo_dee.mid", bpm
)
doo_dee_pixel_locations = {}
num_doo_dee_sectors = 10


bwah_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/bwah.mid", bpm
)
# higher values mean less fluctuation
bwah_sine_scalar = 3
bwah_start_color = (255, 0, 0)
bwah_end_color = (200, 130, 0)


def fill_applicable_bwahs(sequence_config):
    song = sequence_config["song"]

    for bwah in bwah_notes:
        note_start_time = bwah["start_time"]
        duration = bwah["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            ms_since_bwah_start = song["ms_since_song_start"] - note_start_time
            bwah_multiplier = (ms_since_bwah_start - note_start_time) / duration
            bwah_position = config.num_pixels * bwah_multiplier
            bwah_size = config.num_pixels / 10 * bwah_multiplier
            # start at the bottom and go to the top
            # start red and become yellow
            # start small and get bigger
            # pulse slowly (sine wave?)
            start_color_amount = tuple(
                map(lambda x: x * (1 - bwah_multiplier), bwah_start_color)
            )
            end_color_amount = tuple(map(lambda x: x * bwah_multiplier, bwah_end_color))
            bwah_color = tuple(
                [
                    int(min(sum(x), 255))
                    for x in zip(*[start_color_amount, end_color_amount])
                ]
            )

            # use a sine wave to make it pulse. the top of the sine wave should reach max brightness
            # but the bottom should not reach fully off
            bwah_pulse_color = tuple(
                map(
                    lambda x: x
                    * (
                        math.sin(ms_since_bwah_start / 300) / bwah_sine_scalar
                        + (bwah_sine_scalar - 1) / bwah_sine_scalar
                    ),
                    bwah_color,
                )
            )
            # print(
            #     f"msbs: {ms_since_bwah_start}, sca: {start_color_amount}, eca: {end_color_amount}, bc: {bwah_pulse_color}",
            #     flush=True,
            # )
            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                bwah_position,
                bwah_position,
                bwah_pulse_color,
                bwah_size,
                0,
                True,
            )
            break


kick_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/kick.mid", bpm
)


def fill_applicable_kicks(sequence_config):
    song = sequence_config["song"]

    for kick in kick_notes:
        note_start_time = kick["start_time"]
        duration = kick["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            ms_since_fade_start = (
                note_start_time + duration - song["ms_since_song_start"]
            )
            sequence_config["pixels"].fill(
                utils.get_fade_in_color(
                    ms_since_fade_start,
                    duration,
                    (100, 100, 100),
                )
            )
            break


def play_current_frame(sequence_config):
    fill_applicable_baums(sequence_config)
    utils.fill_applicable_notes(
        sequence_config,
        doo_dee_notes,
        doo_dee_pixel_locations,
        num_doo_dee_sectors,
        (250, 170, 0),
    )
    fill_applicable_bwahs(sequence_config)
    fill_applicable_kicks(sequence_config)
