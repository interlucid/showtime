import config
import utils

bpm = 132
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)


# bridge swells


def get_second_swell_measures():
    return [72 + measure for measure in list(range(24))]


second_swell_measures = get_second_swell_measures()


# fill with blue/purple
def fill_applicable_second_swells(sequence_config):
    song = sequence_config["song"]
    if song["current_measure"] in second_swell_measures:
        fade_in_out_color = utils.get_fade_in_out_color(
            song["ms_since_double_measure_start"],
            sequence_config["song_timing"]["song_double_measure_ms"],
            (30, 0, 255),
        )
        sequence_config["pixels"].fill(fade_in_out_color)


def get_swell_measures():
    return [56 + measure for measure in list(range(32))]


swell_measures = get_swell_measures()
swell_pattern_start_half_beats = [measure * 8 for measure in [56, 72]]
num_swell_sectors = 8
swell_pattern = {
    0: 0,
    16: 1,
    18: 2,
    25: 1,
    26: 0,
    28: 1,
    29: 2,
    34: 1,
    36: 2,
    37: 3,
    38: 4,
    41: 3,
    42: 2,
    44: 0,
    45: 2,
    48: 1,
    50: 2,
    53: 3,
    54: 2,
    66: 1,
    68: 2,
    69: 3,
    70: 4,
    73: 3,
    74: 2,
    76: 4,
    77: 5,
    80: 6,
    82: 5,
    84: 4,
    85: 5,
    86: 7,
    90: 6,
    92: 5,
    93: 6,
    98: 5,
    100: 4,
    101: 5,
    102: 4,
    106: 3,
    108: 4,
    109: 3,
    110: 2,
    112: 1,
    114: 2,
    117: 3,
    118: 2,
}
global last_pattern_start_half_beat, last_pattern_key
last_pattern_start_half_beat = 0
last_pattern_key = 0


def get_swell_pattern_key(song):
    current_half_beat = song["current_half_beat"]
    global last_pattern_start_half_beat, last_pattern_key
    if current_half_beat in swell_pattern_start_half_beats:
        last_pattern_start_half_beat = current_half_beat
    half_beats_since_pattern_start = current_half_beat - last_pattern_start_half_beat
    if half_beats_since_pattern_start in swell_pattern:
        last_pattern_key = half_beats_since_pattern_start
    # print(
    #     f"chb: {current_half_beat}, hbsps: {half_beats_since_pattern_start}, lpk: {last_pattern_key}",
    #     flush=True,
    # )
    return last_pattern_key


def fill_applicable_swells(sequence_config):
    song = sequence_config["song"]
    pixels = sequence_config["pixels"]
    # if we're on a particular half beat we need to show something for the swell lead
    if song["current_measure"] in swell_measures:
        # we want each half beat to be the same within itself
        # light up everything in the in swell position to be a certain color
        swell_sector = swell_pattern[get_swell_pattern_key(song)]
        starting_wah_pixel = utils.get_sector_starting_pixel(
            swell_sector, num_swell_sectors
        )
        ending_wah_pixel = utils.get_sector_ending_pixel(
            swell_sector, num_swell_sectors
        )
        utils.fill_pixels_in_center_split_mirror_range(
            pixels,
            starting_wah_pixel,
            ending_wah_pixel,
            (255, 125, 0),
        )


def play_current_frame(sequence_config):
    fill_applicable_second_swells(sequence_config)
    fill_applicable_swells(sequence_config)
