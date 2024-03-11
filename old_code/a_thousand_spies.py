import config
import utils
import parse_midi

import pprint

pp = pprint.PrettyPrinter(indent=4)

song_name = "a_thousand_spies"
bpm = 118
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)


baum_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/baum.mid", bpm
)


def fill_applicable_baums(sequence_config):
    song = sequence_config["song"]
    # if we're where a note should be played
    # print(
    #     f"msss: {song['ms_since_song_start']}, nst: {note_start_time}, d: {duration}",
    #     flush=True,
    # )

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


# original backing track without 1 measure lead in
def get_doo_dee_double_measures():
    doo_dee_section_double_measures = [2, 16]
    bumpy_doo_dee_double_measures = [
        utils.expand_animation_pattern(doo_dee_section_double_measure, [1, 3, 5, 7])
        for doo_dee_section_double_measure in doo_dee_section_double_measures
    ]
    return utils.flatten(bumpy_doo_dee_double_measures) + [0, 1, 14, 15, 28, 29]


doo_dee_double_measures = get_doo_dee_double_measures()
global current_doo_dee_start_measure
current_doo_dee_start_measure = 0
# modified set track with 1 measure lead in
doo_dee_start_measures = [
    double_measure * 2 + 1 for double_measure in doo_dee_double_measures
]
doo_dee_measures = doo_dee_start_measures + [
    start_measure + 1 for start_measure in doo_dee_start_measures
]
doo_dee_start_measures.sort()
doo_dee_measures.sort()
# print(doo_dee_start_measures, flush=True)
# print(doo_dee_measures, flush=True)
doo_dee_pattern_pixel_locations = {}
doo_dee_pattern_config = utils.get_pattern_config(
    # the pattern takes up 4 segments of 16
    song_timing["song_half_beat_ms"],
    2,
    16,
    20,
    2,
)


def get_doo_dee_pattern_timing(sequence_config, pattern_config):
    pattern_timing = {}
    song = sequence_config["song"]
    # update if necessary
    if song["current_measure"] in doo_dee_start_measures:
        global current_doo_dee_start_measure
        current_doo_dee_start_measure = song["current_measure"]
    # always set
    pattern_timing["current_pattern_instance"] = current_doo_dee_start_measure
    pattern_timing["basic_ms_since_pattern_duration_start"] = (
        song["ms_since_song_start"]
        - current_doo_dee_start_measure * song_timing["song_measure_ms"]
    )
    return pattern_timing


def get_doo_dee_pixel_key(song, pattern_timing):
    return current_doo_dee_start_measure


def fill_applicable_doo_dees(sequence_config):
    song = sequence_config["song"]
    pattern_timing = get_doo_dee_pattern_timing(sequence_config, doo_dee_pattern_config)
    # pattern_timing = utils.get_pattern_timing(sequence_config, doo_dee_pattern_config)
    if song["current_measure"] in doo_dee_measures:
        utils.basic_populate_pixel_key(
            sequence_config,
            doo_dee_pattern_config,
            doo_dee_pattern_pixel_locations,
            doo_dee_measures,
            get_doo_dee_pattern_timing,
        )

        # print(f"ddppl: {doo_dee_pattern_pixel_locations}", flush=True)
        for key in doo_dee_pattern_pixel_locations:
            print(f"{key}, {doo_dee_pattern_pixel_locations[key]}", flush=True)

        base_color = (250, 170, 0)

        # fill for all applicable starting segments
        # for pattern_start_segment in [0]:
        for pattern_start_segment in [0, 1, 4, 5, 8, 9, 11, 13, 14, 15]:
            utils.fill_staggered_fade_in_out(
                sequence_config,
                doo_dee_pattern_config,
                doo_dee_pattern_pixel_locations,
                pattern_timing["basic_ms_since_pattern_duration_start"],
                base_color,
                pattern_start_segment,
                get_doo_dee_pixel_key,
                2,
            )


def play_current_frame(sequence_config):
    fill_applicable_baums(sequence_config)
    fill_applicable_doo_dees(sequence_config)
