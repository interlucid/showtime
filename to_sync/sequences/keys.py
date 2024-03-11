import random

import config
import utils
import parse_midi

# starts at 120, becomes 160
# have fun with that future Brandon
# update: <3 you past Brandon

# the tempo changes right at the beginning of measure 12
# converting the MIDI notes will also be hard; gonna have to supply an option "get BPM at time" function
# bpm = 160
# song_measure_ms = utils.get_measure_ms(bpm)
# song_timing = utils.get_song_timing_constants(song_measure_ms)
song_name = "keys"


def ticks_to_ms(ticks_since_song_start, ticks_per_beat):
    beats_since_song_start = ticks_since_song_start / ticks_per_beat
    return beats_to_ms(beats_since_song_start)


def beats_to_ms(beats_since_song_start):
    # this is 1 less than what it says in Live because their numbering starts at 1, not 0
    time_signature_change_measure = 10.5
    time_signature_change_beats = time_signature_change_measure * 4
    measures_since_song_start = beats_since_song_start / 4
    # print(f"beats: {beats_since_song_start}, measure: {measures_since_song_start}")
    # if we are in the first 10.5 measures just return that
    if measures_since_song_start < time_signature_change_measure:
        # print("in the first {time_signature_change_measure} measures")
        return measures_since_song_start * utils.get_measure_ms(120)
    # otherwise add the ms for the full first 12 measures plus whatever's left
    else:
        # print("NOT in the first {time_signature_change_measure} measures")
        # print(
        #     f"(measures_since_song_start - time_signature_change_measure) * get_measure_ms(160): {(measures_since_song_start - time_signature_change_measure) * get_measure_ms(160)}"
        # )
        return (time_signature_change_measure * utils.get_measure_ms(120)) + (
            measures_since_song_start - time_signature_change_measure
        ) * utils.get_measure_ms(160)


bwah_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/bwah.mid",
    ticks_to_ms=ticks_to_ms,
    # bpm=bpm,
)
unique_bwah_notes = []
for bwah_note in bwah_notes:
    if bwah_note["note"] not in unique_bwah_notes:
        unique_bwah_notes.append(bwah_note["note"])
unique_bwah_notes.sort()
unique_bwah_note_positions = {}
colors = [(0, 200, 50), (0, 150, 100), (0, 100, 150), (0, 50, 200)]
# colors = [(0, 50, 200), (0, 100, 150), (0, 150, 100), (0, 200, 50)]
for bwah_index, bwah_note in enumerate(unique_bwah_notes):
    unique_bwah_note_positions[bwah_note] = colors[bwah_index]

# print(bwah_notes, flush=True)


def fill_applicable_bwahs(sequence_config):
    song = sequence_config["song"]
    # find the MIDI note that we're currently at
    ms_since_song_start = song["ms_since_song_start"]
    for bwah in bwah_notes:
        note_start_time = bwah["start_time"]
        duration = bwah["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            color = unique_bwah_note_positions[bwah["note"]]
            ms_since_fade_start = note_start_time + duration - ms_since_song_start
            sequence_config["pixels"].fill(
                utils.get_fade_out_color(
                    ms_since_fade_start,
                    duration,
                    color,
                    # tuple(
                    #     round(x * (1 - (bwah["velocity"] / 127))) for x in (0, 50, 200)
                    # ),
                )
            )
            break


tinkle_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/tinkle.mid",
    ticks_to_ms=ticks_to_ms,
    # bpm=bpm,
)
# print(str(tinkle_notes).replace(",", ",\n"), flush=True)
tinkle_pixel_locations = {}
num_tinkle_sectors = 40


def fill_applicable_tinkles(sequence_config):
    song = sequence_config["song"]
    for tinkle_index, tinkle in enumerate(tinkle_notes):
        ms_since_song_start = song["ms_since_song_start"]
        note_start_time = tinkle["start_time"]
        duration = tinkle["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start < note_start_time + duration
        ):
            # if ms_since_song_start % 10 == 0:
            #     print(
            #         f"ti: {tinkle_index}, msss: {ms_since_song_start}, nst: {note_start_time}, d: {duration}",
            #         flush=True,
            #     )
            #     # print(f"ms_since_song_start is {ms_since_song_start}", flush=True)
            if tinkle_index not in tinkle_pixel_locations:
                tinkle_pixel_locations[tinkle_index] = random.randint(
                    0, num_tinkle_sectors - 1
                )
            ms_since_fade_start = note_start_time + duration - ms_since_song_start
            utils.fill_pixels_in_range(
                sequence_config["pixels"],
                utils.get_sector_starting_pixel(
                    tinkle_pixel_locations[tinkle_index], num_tinkle_sectors
                ),
                utils.get_sector_ending_pixel(
                    tinkle_pixel_locations[tinkle_index], num_tinkle_sectors
                ),
                utils.get_fade_in_out_color(
                    ms_since_fade_start, duration, (125, 125, 50)
                ),
                hardness=0,
                add=True,
            )


def play_current_frame(sequence_config):
    fill_applicable_bwahs(sequence_config)
    fill_applicable_tinkles(sequence_config)
