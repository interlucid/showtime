import math
import random

import config
import utils

# 164 bpm, 41 measures per minute, each measures is 1463 ms
bpm = 164
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

# def dream_killa():
#     # intro byoo - 1 bar; white light from the top to the bottom
#     for ms in range(0, dream_killa_bar_ms):
#         # get white light depending on how close to the main point the pixel is
#         ms

#     # intro baum - a few bars; blue light that starts from the center of the strip and radiates and fades out

# don't let me down


def get_prechorus_build_measures():
    return [106 + measure for measure in list(range(9))]


prechorus_build_measures = get_prechorus_build_measures()


def fill_applicable_prechorus_build(sequence_config):
    song = sequence_config["song"]
    current_measure = song["current_measure"]
    if current_measure in prechorus_build_measures:
        end_pixel = (
            1
            - (116 * song_measure_ms - song["ms_since_song_start"] - song_measure_ms)
            / (10 * song_measure_ms)
        ) * config.num_pixels
        utils.fill_pixels_in_center_split_mirror_range(
            sequence_config["pixels"], 0, end_pixel, (25, 0, 255), 1, 0.5
        )


# don't let me down


def get_dont_let_me_down_half_measures():
    dont_let_me_down_section_half_measures = [76, 164, 235]
    bumpy_dont_let_me_down_half_measures = [
        utils.expand_animation_pattern(
            dont_let_me_down_section_half_measure, list(range(28))
        )
        for dont_let_me_down_section_half_measure in dont_let_me_down_section_half_measures
    ]
    return utils.flatten(bumpy_dont_let_me_down_half_measures) + [
        # final chorus has an extra half chorus length and ends a little early
        263 + half_measure
        for half_measure in list(range(16))
    ]


dont_let_me_down_half_measures = get_dont_let_me_down_half_measures()
half_measure_dont_pixel_locations = {}
dont_let_me_down_pattern_config = utils.get_pattern_config(
    # the pattern takes up 8 segments of 16
    song_timing["song_half_beat_ms"],
    8,
    8,
    15,
    # need to offset the pattern by 2 since we're using half measures but it repeats every measure
    2,
)


def get_dont_let_me_down_pixel_key(song, pattern_timing):
    # this motif actually lasts a whole measure but it is offset by half a measure in the final chorus
    # so we have to find the half measure where it starts rather than the measure
    # we can't use native rounding due to Python banker's rounding so we divide and multiply by 2
    if song["current_half_measure"] < 230:
        return 2 * math.trunc(song["current_half_measure"] / 2)
    else:
        return 2 * math.trunc((song["current_half_measure"] - 1) / 2)


def fill_applicable_dont_let_me_downs(sequence_config):
    song = sequence_config["song"]
    if song["current_half_measure"] in dont_let_me_down_half_measures:
        # need to get a custom pixel key because it changes for the last chorus
        pixel_key = get_dont_let_me_down_pixel_key(
            song, dont_let_me_down_pattern_config
        )

        pattern_offset = dont_let_me_down_pattern_config["pattern_offset"]
        # only generate a new location for the light if the current beat has changed
        if pixel_key not in half_measure_dont_pixel_locations:
            half_measure_dont_pixel_locations[
                pixel_key
            ] = utils.generate_random_pattern(dont_let_me_down_pattern_config, 5)
        if (
            pixel_key - pattern_offset not in half_measure_dont_pixel_locations
            and song["current_double_measure"] - pattern_offset
            in dont_let_me_down_half_measures
        ):
            half_measure_dont_pixel_locations[
                pixel_key - pattern_offset
            ] = utils.generate_random_pattern(dont_let_me_down_pattern_config, 5)

        base_color = (250, 20, 255)

        # get the half beat of this measure (offset in the final chorus)

        if song["current_half_measure"] < 230:
            normalized_ms_since_measure_start = song["ms_since_measure_start"]
        else:
            normalized_ms_since_measure_start = (
                song["ms_since_song_start"] + song_timing["song_half_measure_ms"]
            ) % song_timing["song_measure_ms"]

        # current beat
        # for pattern_start_segment in [3]:
        for pattern_start_segment in [0, 3, 6]:
            utils.fill_staggered_fade_in_out(
                sequence_config,
                dont_let_me_down_pattern_config,
                half_measure_dont_pixel_locations,
                normalized_ms_since_measure_start,
                base_color,
                pattern_start_segment,
                get_dont_let_me_down_pixel_key,
                pattern_offset,
            )


# final chorus sparkle


def get_chorus_sparkle_intervals():
    # multiplier is 4 -> half beat
    multiplier = 4
    return [235 * multiplier + interval for interval in list(range(44 * multiplier))]


chorus_sparkle_intervals = get_chorus_sparkle_intervals()
interval_sparkle_pixel_locations = {}
sparkle_pattern_config = utils.get_pattern_config(
    song_timing["song_quarter_beat_ms"],
    2,
    2,
    # make it a little smaller than the number of pixels so that some sparkles appear bigger
    # math.trunc(config.num_pixels * 0.8),
    90,
    1,
)


def fill_applicable_chorus_sparkle(sequence_config):
    pattern_timing = utils.get_pattern_timing(sequence_config, sparkle_pattern_config)
    if pattern_timing["current_pattern_instance"] in chorus_sparkle_intervals:
        utils.basic_populate_pixel_key(
            sequence_config,
            sparkle_pattern_config,
            interval_sparkle_pixel_locations,
            chorus_sparkle_intervals,
        )
        # # we want each interval to be the same within itself
        # pixel_key = pattern_timing["current_pattern_instance"]
        # pattern_offset = sparkle_pattern_config["pattern_offset"]
        # # only generate a new location for the light if the current interval has changed
        # if pixel_key not in interval_sparkle_pixel_locations:
        #     interval_sparkle_pixel_locations[
        #         pixel_key
        #     ] = utils.generate_random_pattern(sparkle_pattern_config, 5)
        # if (
        #     pixel_key - pattern_offset not in interval_sparkle_pixel_locations
        #     # only generate the previous notes if they are also part of the loop
        #     and pattern_timing["current_pattern_instance"] - pattern_offset
        #     in chorus_sparkle_intervals
        # ):
        #     interval_sparkle_pixel_locations[
        #         pixel_key - pattern_offset
        #     ] = utils.generate_random_pattern(sparkle_pattern_config, 5)

        # print(f"hmpl: {interval_sparkle_pixel_locations}")
        base_color = (255, 255, 255)

        # fill for all applicable starting segments
        for pattern_start_segment in list(
            range(sparkle_pattern_config["num_pattern_segments"])
        ):
            # for pattern_start_segment in [14]:
            utils.fill_staggered_fade_in_out(
                sequence_config,
                sparkle_pattern_config,
                interval_sparkle_pixel_locations,
                pattern_timing["basic_ms_since_pattern_duration_start"],
                base_color,
                pattern_start_segment,
            )


# blackout shudder


def fill_applicable_blackout_shudder(sequence_config):
    song = sequence_config["song"]
    shudder_half_measure = 229
    if song["current_quarter_beat"] in [
        shudder_half_measure * 8 + quarter_beat for quarter_beat in [1, 3, 5, 7]
    ] or song["current_beat"] in [536, 552]:
        sequence_config["pixels"].fill((0, 0, 0))


# wah uh ooh uh


def get_wah_uh_ooh_uh_half_measures():
    wah_uh_ooh_uh_section_half_measures = [7, 25, 43, 113, 131]
    bumpy_wah_uh_ooh_uh_half_measures = [
        utils.expand_animation_pattern(wah_uh_ooh_uh_section_half_measure, [0, 4, 12])
        for wah_uh_ooh_uh_section_half_measure in wah_uh_ooh_uh_section_half_measures
    ]
    return utils.flatten(bumpy_wah_uh_ooh_uh_half_measures)


def get_wah_half_beats():
    wah_uh_ooh_uh_half_measures = get_wah_uh_ooh_uh_half_measures() + [107, 195, 276]
    wah_uh_ooh_uh_block_half_beats = map(
        lambda half_measure: half_measure * 4, wah_uh_ooh_uh_half_measures
    )
    # get the half beats for the 4 hit long wah uh ooh uhs
    wah_uh_ooh_uh_half_beats = [
        utils.expand_animation_pattern(wah_uh_ooh_uh_block_half_beat, [0, 1, 2, 3])
        for wah_uh_ooh_uh_block_half_beat in wah_uh_ooh_uh_block_half_beats
    ]
    wah_uh_half_measures = [13, 15, 31, 33, 49, 51, 119, 121, 137, 139]
    wah_uh_block_half_beats = map(lambda measure: measure * 4, wah_uh_half_measures)
    # get the half beats for the 2 hit long wah uhs
    wah_uh_half_beats = [
        utils.expand_animation_pattern(wah_uh_block_half_beat, [0, 1])
        for wah_uh_block_half_beat in wah_uh_block_half_beats
    ]
    wah_half_beats = wah_uh_ooh_uh_half_beats + wah_uh_half_beats
    return utils.flatten(wah_half_beats)


num_wah_sectors = 8
wah_half_beats = get_wah_half_beats()
half_beat_wah_pixel_sectors = {}


def fill_applicable_wah_uh_ooh_uhs(sequence_config):
    song = sequence_config["song"]
    pixels = sequence_config["pixels"]
    # if we're on a particular half beat we need to show something for wah uh ooh uh
    if song["current_half_beat"] in wah_half_beats:
        # we want each half beat to be the same within itself
        # only generate a new location for the light if the current half beat has changed
        while (
            # run it at least once to get a value for the current half beat
            song["current_half_beat"] not in half_beat_wah_pixel_sectors
            # run it again if needed so each sector is different from the last
            or (
                song["current_half_beat"] - 1 in half_beat_wah_pixel_sectors
                and half_beat_wah_pixel_sectors[song["current_half_beat"]]
                == half_beat_wah_pixel_sectors[song["current_half_beat"] - 1]
            )
        ):
            half_beat_wah_pixel_sectors[song["current_half_beat"]] = random.randint(
                0, (num_wah_sectors - 1)
            )
        # light up everything in the in wah-uh-ooh-uh position to be a certain color
        wah_sector = half_beat_wah_pixel_sectors[song["current_half_beat"]]
        starting_wah_pixel = utils.get_sector_starting_pixel(
            wah_sector, num_wah_sectors
        )
        ending_wah_pixel = utils.get_sector_ending_pixel(wah_sector, num_wah_sectors)
        utils.fill_pixels_in_center_split_mirror_range(
            pixels,
            starting_wah_pixel,
            ending_wah_pixel,
            (255, 25, 0),
        )


# horns


def get_horn_start_half_measures():
    # there aren't too many and the second prechorus starts a verse late but then catches up so just list them
    return [
        half_measure * 2
        for half_measure in [28, 30, 32, 34, 36, 74, 76, 78, 80]
        # there is one odd one outs for the second prechorus that's on a half measure
    ] + [145]


horn_start_half_measures = get_horn_start_half_measures()
global current_horn_start
current_horn_start = 0


def fill_applicable_horns(sequence_config):
    song = sequence_config["song"]
    current_half_measure = song["current_half_measure"]
    if (
        # the animation should play for a whole measure
        current_half_measure in horn_start_half_measures
        or current_half_measure - 1 in horn_start_half_measures
    ):
        if current_half_measure in horn_start_half_measures:
            global current_horn_start
            current_horn_start = current_half_measure
        # get the new color value by using the range of the light and how close we are to the start of the measure
        base_color = (255, 0, 0)
        # we want to calculate from an arbitrary half measure to a full measure away
        time_since_last_horn_start = (
            song["ms_since_song_start"]
            - current_horn_start * song_timing["song_half_measure_ms"]
        )
        new_color_value = [
            round(
                color_part
                * (1 - time_since_last_horn_start / song_timing["song_measure_ms"])
            )
            for color_part in base_color
        ]
        sequence_config["pixels"].fill(new_color_value)


# baums


def get_baum_half_measures():
    baum_section_measures = [1, 10, 19, 54, 63]
    baum_section_half_measures = [measure * 2 for measure in baum_section_measures]
    return utils.flatten(
        [
            utils.expand_animation_pattern(
                baum_section_half_measure, [0, 2, 3, 4, 6, 7, 8, 10, 12, 14, 15, 16]
            )
            for baum_section_half_measure in baum_section_half_measures
        ]
        # this last bit is for the baums in the bridge which start at measure 98
    ) + [half_measure + 98 * 2 for half_measure in [0, 2, 4, 5, 6, 8, 10, 12, 13, 14]]


baum_half_measures = get_baum_half_measures()


def fill_applicable_baums(sequence_config):
    song = sequence_config["song"]
    if song["current_half_measure"] in baum_half_measures:
        # get the new color value by using the range of the light and how close we are to the start of the measure
        base_color = (255, 0, 120)
        # new_color_value = [
        #     round(
        #         color_part
        #         * (
        #             1
        #             - song["ms_since_half_measure_start"]
        #             / song_timing["song_half_measure_ms"]
        #         )
        #     )
        #     for color_part in base_color
        # ]
        # sequence_config["pixels"].fill(new_color_value)
        sequence_config["pixels"].fill(
            utils.get_fade_out_color(
                song["ms_since_half_measure_start"],
                song_timing["song_half_measure_ms"],
                base_color,
            )
        )
        # print(f"current_half_beat is {current_half_beat}", flush=True)


# dyoos


def get_dyoo_measures():
    dyoo_section_measures = [9, 53]
    return sorted(
        utils.flatten(
            [
                utils.expand_animation_pattern(dyoo_section_measure, [0, 9, 18, 27])
                for dyoo_section_measure in dyoo_section_measures
            ]
            # add additional dyoos that are not part of a pattern
        )
        + [0, 97, 105]
    )


dyoo_measures = get_dyoo_measures()


# def get_dyoo_location_value(dyoo_y_value):
#     return round((config.num_pixels - 1) * (-(dyoo_y_value ** (2 / 5)) + 1))


def fill_applicable_dyoos(sequence_config):
    song = sequence_config["song"]
    if song["current_measure"] in dyoo_measures:
        dyoo_location_value = utils.get_exponential_dropoff(
            song["ms_since_measure_start"] / song_measure_ms
        )
        previous_dyoo_location_value = utils.get_exponential_dropoff(
            max(song["ms_since_measure_start"] - config.sleep_ms, 0) / song_measure_ms
        )
        utils.fill_pixels_in_center_split_mirror_range(
            sequence_config["pixels"],
            dyoo_location_value,
            # if the previous value is more than 2 away, use that
            # otherwise make the dyoo animation at least 2 LEDs wide
            max(previous_dyoo_location_value, dyoo_location_value + 2),
            (255, 255, 255),
            2,
        )


def play_current_frame(sequence_config):
    fill_applicable_prechorus_build(sequence_config)
    fill_applicable_dont_let_me_downs(sequence_config)
    fill_applicable_chorus_sparkle(sequence_config)
    fill_applicable_blackout_shudder(sequence_config)
    fill_applicable_wah_uh_ooh_uhs(sequence_config)
    fill_applicable_horns(sequence_config)
    fill_applicable_baums(sequence_config)
    fill_applicable_dyoos(sequence_config)
