import math

import utils

bpm = 90
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)


def get_piano_measures():
    piano_section_measures = [17, 34, 42]
    bumpy_piano_measures = [
        utils.expand_animation_pattern(piano_section_double_measure, list(range(8)))
        for piano_section_double_measure in piano_section_measures
    ]
    return utils.flatten(bumpy_piano_measures) + [
        # last chorus is one measure short
        50 + measure
        for measure in list(range(7))
    ]


piano_measures = get_piano_measures()
piano_start_measures = [17, 21, 34, 38, 42, 46, 50, 54]
global current_piano_start_measure
current_piano_start_measure = 0
# indexed by the measure where the pattern starts
# however the pattern is four measures long
piano_pattern_pixel_locations = {}
piano_pattern_config = utils.get_pattern_config(
    song_timing["song_quarter_beat_ms"],
    4,
    64,
    20,
    1,
)
piano_pattern_start_segments = (
    # for every measure, add the starting motif plus the appropriate offset
    [(measure * 16) + note for note in [0, 3, 4, 5, 6] for measure in [0, 1, 2, 3]]
    # first measure extra note
    + [14]
    # third measure extra notes
    + [note + 2 * 16 for note in [12, 14]]
)


def get_piano_pattern_timing(sequence_config, pattern_config):
    pattern_timing = {}
    song = sequence_config["song"]
    # update if necessary
    if song["current_measure"] in piano_start_measures:
        global current_piano_start_measure
        current_piano_start_measure = song["current_measure"]
    # always set
    pattern_timing["current_pattern_instance"] = current_piano_start_measure
    pattern_timing["basic_ms_since_pattern_duration_start"] = (
        song["ms_since_song_start"]
        - current_piano_start_measure * song_timing["song_measure_ms"]
    )
    return pattern_timing


def get_piano_pixel_key(song, pattern_timing):
    return current_piano_start_measure


def fill_applicable_pianos(sequence_config):
    song = sequence_config["song"]
    pattern_timing = get_piano_pattern_timing(sequence_config, piano_pattern_config)
    if song["current_measure"] in piano_measures:
        utils.basic_populate_pixel_key(
            sequence_config,
            piano_pattern_config,
            piano_pattern_pixel_locations,
            piano_measures,
            get_piano_pattern_timing,
        )

        base_color = (0, 70, 250)

        # fill for all applicable starting segments
        # for pattern_start_segment in [0, 16, 32, 48]:
        for pattern_start_segment in piano_pattern_start_segments:
            utils.fill_staggered_fade_in_out(
                sequence_config,
                piano_pattern_config,
                piano_pattern_pixel_locations,
                pattern_timing["basic_ms_since_pattern_duration_start"],
                base_color,
                pattern_start_segment,
                get_piano_pixel_key,
                4,
            )


def play_current_frame(sequence_config):
    fill_applicable_pianos(sequence_config)
