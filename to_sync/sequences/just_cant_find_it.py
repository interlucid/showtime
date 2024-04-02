import math

import config
import utils
import parse_midi

song_name = "just_cant_find_it"
bpm = 90
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)


off_beat_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/off_beat.mid", bpm
)
off_beat_sectors_map = {}
off_beat_note_values = map(lambda midi_note: midi_note["note"], off_beat_notes)
unique_off_beat_notes = list(set(off_beat_note_values))
for note_index, note in enumerate(unique_off_beat_notes):
    off_beat_sectors_map[note] = note_index
num_off_beat_sectors = len(off_beat_sectors_map)
off_beat_slide_ms = 1000
off_beat_color = (100, 0, 200)


def fill_applicable_off_beats(sequence_config):
    song = sequence_config["song"]

    # find the MIDI note that we're currently at
    for off_beat_index, off_beat in enumerate(off_beat_notes):
        note_start_time = off_beat["start_time"]
        duration = off_beat["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            ms_since_fade_start = song["ms_since_song_start"] - note_start_time
            starting_off_beat_pixel = utils.get_sector_starting_pixel(
                off_beat_sectors_map[off_beat["note"]],
                len(unique_off_beat_notes),
            )
            ending_off_beat_pixel = utils.get_sector_ending_pixel(
                off_beat_sectors_map[off_beat["note"]],
                len(unique_off_beat_notes),
            )
            # if we're in the first bit of time for this note, play the frame of the sliding animation
            # otherwise hold
            if (
                off_beat_index > 0
                and song["ms_since_song_start"] <= note_start_time + off_beat_slide_ms
            ):
                # get last pixel positions
                last_starting_off_beat_pixel = utils.get_sector_starting_pixel(
                    off_beat_sectors_map[off_beat_notes[off_beat_index - 1]["note"]],
                    len(unique_off_beat_notes),
                )
                last_ending_off_beat_pixel = utils.get_sector_ending_pixel(
                    off_beat_sectors_map[off_beat_notes[off_beat_index - 1]["note"]],
                    len(unique_off_beat_notes),
                )
                starting_off_beat_pixel_diff = (
                    starting_off_beat_pixel - last_starting_off_beat_pixel
                )
                ending_off_beat_pixel_diff = (
                    ending_off_beat_pixel - last_ending_off_beat_pixel
                )
                linear_move_multiplier = (
                    song["ms_since_song_start"] - note_start_time
                ) / off_beat_slide_ms
                move_multiplier = utils.get_parametric_blend(linear_move_multiplier)
                # print(
                #     f"lmm: {linear_move_multiplier}, mm: {move_multiplier}", flush=True
                # )
                slide_starting_off_beat_pixel = (
                    last_starting_off_beat_pixel
                    + move_multiplier * starting_off_beat_pixel_diff
                )
                slide_ending_off_beat_pixel = (
                    last_ending_off_beat_pixel
                    + move_multiplier * ending_off_beat_pixel_diff
                )
                utils.fill_pixels_in_center_split_mirror_range(
                    sequence_config["pixels"],
                    slide_starting_off_beat_pixel,
                    slide_ending_off_beat_pixel,
                    off_beat_color,
                    2.5,
                    0,
                )
            else:
                utils.fill_pixels_in_center_split_mirror_range(
                    sequence_config["pixels"],
                    starting_off_beat_pixel,
                    ending_off_beat_pixel,
                    off_beat_color,
                    2.5,
                    0,
                )
            break


piano_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/piano.mid", bpm
)
piano_pixel_locations = {}
num_piano_sectors = 12


organ_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/organ.mid", bpm
)
organ_color = (100, 0, 10)
organ_size = config.num_pixels / 15


def fill_applicable_organs(sequence_config):
    song = sequence_config["song"]

    # find the MIDI note that we're currently at
    for organ in organ_notes:
        note_start_time = organ["start_time"]
        duration = organ["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                0,
                organ_size,
                organ_color,
                1,
                1,
                True,
            )
            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                config.num_pixels - organ_size,
                config.num_pixels,
                organ_color,
                1,
                1,
                True,
            )
            break


def play_current_frame(sequence_config):
    fill_applicable_off_beats(sequence_config)
    utils.fill_applicable_notes(
        sequence_config,
        piano_notes,
        piano_pixel_locations,
        num_piano_sectors,
        (0, 70, 250),
    )
    fill_applicable_organs(sequence_config)
