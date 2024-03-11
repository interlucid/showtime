import config
import utils
import parse_midi

import random

song_name = "fog_in_the_trees"
bpm = 169
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

hook_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/hook.mid", bpm
)

# there are 12 notes in the longest pattern
# I want the slots to be small, like raindrops
num_sectors = 40
hook_note_slot_assignments = utils.flatten(
    [
        # this one-liner returns a list that is num_sectors long with unique values
        random.sample(list(range(num_sectors)), num_sectors)
        # TODO: replace with the utils function once it's more generic
        for repeat in list(range(5))
    ]
)


def fill_applicable_hook_notes(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]
    for hook_index, hook_note in enumerate(hook_notes):
        note_start_time = hook_note["start_time"]
        duration = hook_note["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            # fade out
            multiplier = 1 - (ms_since_song_start - note_start_time) / duration
            color = tuple(int(multiplier * x) for x in (50, 70, 150))
            starting_hook_pixel = utils.get_sector_starting_pixel(
                hook_note_slot_assignments[hook_index],
                num_sectors,
            )
            ending_hook_pixel = utils.get_sector_ending_pixel(
                hook_note_slot_assignments[hook_index],
                num_sectors,
            )
            # print(
            #     f"fading out msss: {ms_since_song_start}, nst: {note_start_time}, d: {duration}, m: {multiplier}, c:{color}",
            #     flush=True,
            # )
            utils.fill_pixels_in_range(
                sequence_config["pixels"],
                starting_hook_pixel,
                ending_hook_pixel,
                color,
            )


def play_current_frame(sequence_config):
    fill_applicable_hook_notes(sequence_config)
