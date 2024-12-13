import random

import config
import parse_midi
import utils

song_name = "falling_in_love"
bpm = 90
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

doo_doo_doo_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/doo_doo_doo.mid", bpm
)
# each note will be like a raindrop and the locations are just the top
doo_doo_doo_pixel_locations = {}
num_doo_doo_doo_sectors = 16


def fill_applicable_doo_doo_doos(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]
    for doo_doo_doo_index, doo_doo_doo in enumerate(doo_doo_doo_notes):
        note_start_time = doo_doo_doo["start_time"]
        duration = doo_doo_doo["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            # don't allow two sequential notes to start in the same sector
            while doo_doo_doo_index not in doo_doo_doo_pixel_locations or (
                doo_doo_doo_index - 1 in doo_doo_doo_pixel_locations
                and doo_doo_doo_pixel_locations[doo_doo_doo_index]["sector"]
                == doo_doo_doo_pixel_locations[doo_doo_doo_index - 1]["sector"]
            ):
                sector = random.randint(
                    num_doo_doo_doo_sectors / 4,
                    num_doo_doo_doo_sectors - 1 - num_doo_doo_doo_sectors / 4,
                )
                doo_doo_doo_color = (
                    random.randint(5, 15),
                    random.randint(5, 145),
                    random.randint(170, 240),
                )
                doo_doo_doo_pixel_locations[doo_doo_doo_index] = {
                    "sector": sector,
                    "base_color": doo_doo_doo_color,
                }
            sector_starting_pixel = utils.get_sector_starting_pixel(
                doo_doo_doo_pixel_locations[doo_doo_doo_index]["sector"],
                num_doo_doo_doo_sectors,
            )
            doo_doo_doo_in_higher_half = sector_starting_pixel > config.num_pixels / 2
            doo_doo_doo_distance = utils.get_exponential_dropoff(
                (ms_since_song_start - note_start_time) / duration,
                invert_speed=True,
                invert_direction=doo_doo_doo_in_higher_half,
            ) / 2 + (config.num_pixels / 2 if doo_doo_doo_in_higher_half else 0)
            previous_doo_doo_doo_distance = utils.get_exponential_dropoff(
                (ms_since_song_start - 200 - note_start_time) / duration,
                invert_speed=True,
                invert_direction=doo_doo_doo_in_higher_half,
            ) / 2 + (config.num_pixels / 2 if doo_doo_doo_in_higher_half else 0)
            starting_pixel = sector_starting_pixel - (
                config.num_pixels / 2 - doo_doo_doo_distance
            )
            ending_pixel = sector_starting_pixel - (
                config.num_pixels / 2 - previous_doo_doo_doo_distance
            )
            # print(
            #     f"ssp: {sector_starting_pixel}, sp: {starting_pixel}, ep: {ending_pixel}, dddd: {doo_doo_doo_distance}",
            #     flush=True,
            # )
            base_color = doo_doo_doo_pixel_locations[doo_doo_doo_index]["base_color"]
            utils.fill_pixels_in_range(
                sequence_config["pixels"],
                starting_pixel,
                ending_pixel,
                utils.get_fade_in_out_color(
                    ms_since_song_start - note_start_time, duration, base_color
                ),
                hardness=0.5,
            )


def play_current_frame(sequence_config):
    fill_applicable_doo_doo_doos(sequence_config)
