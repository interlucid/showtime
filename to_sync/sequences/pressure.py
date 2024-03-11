import config
import utils

bpm = 128
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)


dee_dee_dee_measures = [56 + measure for measure in list(range(16))]
dee_dee_dee_start_measures = dee_dee_dee_measures
global current_dee_dee_dee_start_measure
current_dee_dee_dee_start_measure = 0
# dee_dee_dee_measures.sort()
# print(dee_dee_dee_start_measures, flush=True)
# print(dee_dee_dee_measures, flush=True)
dee_dee_dee_pattern_pixel_locations = {}
dee_dee_dee_pattern_config = utils.get_pattern_config(
    # the pattern takes up 4 segments of 16
    song_timing["song_half_beat_ms"],
    2,
    8,
    20,
    1,
)
dee_dee_dee_pattern_start_segments = list(range(8))


def get_dee_dee_dee_pattern_timing(sequence_config, pattern_config):
    pattern_timing = {}
    song = sequence_config["song"]
    # update if necessary
    if song["current_measure"] in dee_dee_dee_start_measures:
        global current_dee_dee_dee_start_measure
        current_dee_dee_dee_start_measure = song["current_measure"]
    # always set
    pattern_timing["current_pattern_instance"] = current_dee_dee_dee_start_measure
    pattern_timing["basic_ms_since_pattern_duration_start"] = (
        song["ms_since_song_start"]
        - current_dee_dee_dee_start_measure * song_timing["song_measure_ms"]
    )
    return pattern_timing


def get_dee_dee_dee_pixel_key(song, pattern_timing):
    return current_dee_dee_dee_start_measure


def fill_applicable_dee_dee_dees(sequence_config):
    song = sequence_config["song"]
    pattern_timing = get_dee_dee_dee_pattern_timing(
        sequence_config, dee_dee_dee_pattern_config
    )
    # pattern_timing = utils.get_pattern_timing(sequence_config, dee_dee_dee_pattern_config)
    if song["current_measure"] in dee_dee_dee_measures:
        utils.basic_populate_pixel_key(
            sequence_config,
            dee_dee_dee_pattern_config,
            dee_dee_dee_pattern_pixel_locations,
            dee_dee_dee_measures,
            get_dee_dee_dee_pattern_timing,
        )

        base_color = (20, 70, 250)

        # fill for all applicable starting segments
        # for pattern_start_segment in [0]:
        for pattern_start_segment in dee_dee_dee_pattern_start_segments:
            utils.fill_staggered_fade_in_out(
                sequence_config,
                dee_dee_dee_pattern_config,
                dee_dee_dee_pattern_pixel_locations,
                pattern_timing["basic_ms_since_pattern_duration_start"],
                base_color,
                pattern_start_segment,
                get_dee_dee_dee_pixel_key,
                1,
            )


def play_current_frame(sequence_config):
    fill_applicable_dee_dee_dees(sequence_config)
