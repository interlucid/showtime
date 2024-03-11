import utils

bpm = 98
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)


def get_guitar_double_measures():
    guitar_section_double_measures = [6, 17]
    bumpy_guitar_double_measures = [
        utils.expand_animation_pattern(guitar_section_double_measure, list(range(4)))
        for guitar_section_double_measure in guitar_section_double_measures
    ]
    return utils.flatten(bumpy_guitar_double_measures)


guitar_double_measures = get_guitar_double_measures()
measure_guitar_pixel_locations = {}
guitar_pattern_config = utils.get_pattern_config(
    song_timing["song_quarter_beat_ms"],
    8,
    32,
    10,
    1,
)


def fill_applicable_guitars(sequence_config):
    pattern_timing = utils.get_pattern_timing(sequence_config, guitar_pattern_config)
    if pattern_timing["current_pattern_instance"] in guitar_double_measures:
        utils.basic_populate_pixel_key(
            sequence_config,
            guitar_pattern_config,
            measure_guitar_pixel_locations,
            guitar_double_measures,
        )

        base_color = (250, 70, 0)

        # fill for all applicable starting segments
        for pattern_start_segment in [2, 4, 5, 6, 7]:
            # for pattern_start_segment in [14]:
            utils.fill_staggered_fade_in_out(
                sequence_config,
                guitar_pattern_config,
                measure_guitar_pixel_locations,
                pattern_timing["basic_ms_since_pattern_duration_start"],
                base_color,
                pattern_start_segment,
            )


def play_current_frame(sequence_config):
    fill_applicable_guitars(sequence_config)
