import random

import config
import utils
import parse_midi

song_name = "pressure"
bpm = 128
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

doo_doo_doo_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/doo_doo_doo.mid", bpm
)
doo_doo_doo_sectors_map = {}
doo_doo_doo_note_values = map(lambda midi_note: midi_note["note"], doo_doo_doo_notes)
unique_doo_doo_doo_notes = sorted(list(set(doo_doo_doo_note_values)))
for note_index, note in enumerate(unique_doo_doo_doo_notes):
    doo_doo_doo_sectors_map[note] = note_index
# print(unique_doo_doo_doo_notes)
# print(doo_doo_doo_sectors_map)
num_doo_doo_doo_sectors = len(unique_doo_doo_doo_notes)


def fill_applicable_doo_doo_doos(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]

    # find the MIDI note that we're currently at
    for index, doo_doo_doo_note in enumerate(doo_doo_doo_notes):
        note_start_time = doo_doo_doo_note["start_time"]
        duration = doo_doo_doo_note["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            ms_since_fade_start = note_start_time + duration - ms_since_song_start
            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                utils.get_sector_starting_pixel(
                    doo_doo_doo_sectors_map[doo_doo_doo_note["note"]],
                    num_doo_doo_doo_sectors,
                ),
                utils.get_sector_ending_pixel(
                    doo_doo_doo_sectors_map[doo_doo_doo_note["note"]],
                    num_doo_doo_doo_sectors,
                ),
                utils.get_fade_in_out_color(
                    ms_since_fade_start, duration, (10, 180, 150)
                ),
                hardness=0,
                add=True,
            )


# dee_dee_dee_measures = [56 + measure for measure in list(range(16))]
# dee_dee_dee_start_measures = dee_dee_dee_measures
# global current_dee_dee_dee_start_measure
# current_dee_dee_dee_start_measure = 0
# # dee_dee_dee_measures.sort()
# # print(dee_dee_dee_start_measures, flush=True)
# # print(dee_dee_dee_measures, flush=True)
# dee_dee_dee_pattern_pixel_locations = {}
# dee_dee_dee_pattern_config = utils.get_pattern_config(
#     # the pattern takes up 4 segments of 16
#     song_timing["song_half_beat_ms"],
#     2,
#     8,
#     20,
#     1,
# )
# dee_dee_dee_pattern_start_segments = list(range(16))


# def get_dee_dee_dee_pattern_timing(sequence_config, pattern_config):
#     pattern_timing = {}
#     song = sequence_config["song"]
#     # update if necessary
#     if song["current_measure"] in dee_dee_dee_start_measures:
#         global current_dee_dee_dee_start_measure
#         current_dee_dee_dee_start_measure = song["current_measure"]
#     # always set
#     pattern_timing["current_pattern_instance"] = current_dee_dee_dee_start_measure
#     pattern_timing["basic_ms_since_pattern_duration_start"] = (
#         song["ms_since_song_start"]
#         - current_dee_dee_dee_start_measure * song_timing["song_measure_ms"]
#     )
#     return pattern_timing


# def get_dee_dee_dee_pixel_key(song, pattern_timing):
#     return current_dee_dee_dee_start_measure


# def fill_applicable_dee_dee_dees(sequence_config):
#     song = sequence_config["song"]
#     pattern_timing = get_dee_dee_dee_pattern_timing(
#         sequence_config, dee_dee_dee_pattern_config
#     )
#     # pattern_timing = utils.get_pattern_timing(sequence_config, dee_dee_dee_pattern_config)
#     if song["current_measure"] in dee_dee_dee_measures:
#         utils.basic_populate_pixel_key(
#             sequence_config,
#             dee_dee_dee_pattern_config,
#             dee_dee_dee_pattern_pixel_locations,
#             dee_dee_dee_measures,
#             get_dee_dee_dee_pattern_timing,
#         )

#         base_color = (220, 230, 50)

#         # fill for all applicable starting segments
#         # for pattern_start_segment in [0]:
#         for pattern_start_segment in dee_dee_dee_pattern_start_segments:
#             utils.fill_staggered_fade_in_out(
#                 sequence_config,
#                 dee_dee_dee_pattern_config,
#                 dee_dee_dee_pattern_pixel_locations,
#                 pattern_timing["basic_ms_since_pattern_duration_start"],
#                 base_color,
#                 pattern_start_segment,
#                 get_dee_dee_dee_pixel_key,
#                 1,
#             )


dee_dee_dee_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/dee_dee_dee.mid", bpm
)
# print(str(dee_dee_dee_notes).replace(",", ",\n"), flush=True)
dee_dee_dee_pixel_locations = {}
num_dee_dee_dee_sectors = 25
dee_dee_dee_duration_extension = 300


def fill_applicable_dee_dee_dees(sequence_config):
    song = sequence_config["song"]
    for dee_dee_dee_index, dee_dee_dee in enumerate(dee_dee_dee_notes):
        ms_since_song_start = song["ms_since_song_start"]
        note_start_time = dee_dee_dee["start_time"]
        duration = dee_dee_dee["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start
            < note_start_time + duration + dee_dee_dee_duration_extension
        ):
            if dee_dee_dee_index not in dee_dee_dee_pixel_locations:
                dee_dee_dee_pixel_locations[dee_dee_dee_index] = random.randint(
                    0, num_dee_dee_dee_sectors - 1
                )
            ms_since_fade_start = (
                note_start_time
                + duration
                + dee_dee_dee_duration_extension
                - ms_since_song_start
            )
            utils.fill_pixels_in_range(
                sequence_config["pixels"],
                utils.get_sector_starting_pixel(
                    dee_dee_dee_pixel_locations[dee_dee_dee_index],
                    num_dee_dee_dee_sectors,
                ),
                utils.get_sector_ending_pixel(
                    dee_dee_dee_pixel_locations[dee_dee_dee_index],
                    num_dee_dee_dee_sectors,
                ),
                utils.get_fade_in_out_color(
                    ms_since_fade_start,
                    duration + dee_dee_dee_duration_extension,
                    (200, 210, 10),
                ),
                hardness=0,
                add=True,
            )


def play_current_frame(sequence_config):
    fill_applicable_doo_doo_doos(sequence_config)
    fill_applicable_dee_dee_dees(sequence_config)
