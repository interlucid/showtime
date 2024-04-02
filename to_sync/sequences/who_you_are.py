import config
import utils

# not in set as of 03/2024!

bpm = 90
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)


def play_current_frame(sequence_config):
    pass
    # utils.fill_pixels_in_center_split_mirror_range(
    #     sequence_config["pixels"],
    #     20,
    #     30,
    #     (255, 0, 155),
    #     2,
    # )

    # fill_applicable_dyoos(song)
