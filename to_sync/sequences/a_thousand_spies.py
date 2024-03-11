import random

import config
import utils
import parse_midi

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


doo_dee_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/doo_dee.mid", bpm
)
doo_dee_pixel_locations = {}
num_doo_dee_sectors = 10


def fill_applicable_doo_dees(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]
    # if we're where a note should be played
    # print(
    #     f"msss: {song['ms_since_song_start']}, nst: {note_start_time}, d: {duration}",
    #     flush=True,
    # )

    # find the MIDI note that we're currently at
    for doo_dee_index, doo_dee in enumerate(doo_dee_notes):
        note_start_time = doo_dee["start_time"]
        duration = doo_dee["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            if doo_dee_index not in doo_dee_pixel_locations:
                doo_dee_pixel_locations[doo_dee_index] = random.randint(
                    0, num_doo_dee_sectors - 1
                )
            ms_since_fade_start = note_start_time + duration - ms_since_song_start
            utils.fill_pixels_in_range(
                sequence_config["pixels"],
                utils.get_sector_starting_pixel(
                    doo_dee_pixel_locations[doo_dee_index], num_doo_dee_sectors
                ),
                utils.get_sector_ending_pixel(
                    doo_dee_pixel_locations[doo_dee_index], num_doo_dee_sectors
                ),
                utils.get_fade_in_out_color(
                    ms_since_fade_start, duration, (250, 170, 0)
                ),
                hardness=0,
                add=True,
            )


bwah_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/bwah.mid", bpm
)


def fill_applicable_bwahs(sequence_config):
    song = sequence_config["song"]

    for bwah in bwah_notes:
        note_start_time = bwah["start_time"]
        duration = bwah["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            ms_since_bwah_start = song["ms_since_song_start"] - note_start_time
            bwah_multiplier = (ms_since_bwah_start - note_start_time) / duration
            bwah_position = config.num_pixels * bwah_multiplier
            bwah_size = config.num_pixels / 30 * bwah_multiplier
            # print(
            #     f"bm: {bwah_multiplier}, bp: {bwah_position}, bs: {bwah_size}",
            #     flush=True,
            # )
            # start at the bottom and go to the top
            # start small and get bigger
            # pulse slowly (sine wave?)
            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                bwah_position,
                bwah_position + 8,
                (255, 0, 0),
                # bwah_size,
                1,
                0,
                True,
            )
            break


kick_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/kick.mid", bpm
)


def fill_applicable_kicks(sequence_config):
    song = sequence_config["song"]

    for kick in kick_notes:
        note_start_time = kick["start_time"]
        duration = kick["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            ms_since_fade_start = (
                note_start_time + duration - song["ms_since_song_start"]
            )
            sequence_config["pixels"].fill(
                utils.get_fade_in_color(
                    ms_since_fade_start,
                    duration,
                    (100, 100, 100),
                )
            )
            break


def play_current_frame(sequence_config):
    fill_applicable_baums(sequence_config)
    fill_applicable_doo_dees(sequence_config)
    fill_applicable_bwahs(sequence_config)
    fill_applicable_kicks(sequence_config)
