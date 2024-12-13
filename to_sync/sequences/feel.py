import config
import parse_midi
import utils

song_name = "feel"
bpm = 112
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

doot_doot_doot_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/dootdootdoot.mid", bpm
)
doot_doot_doot_pixel_locations = {}
# 3 regular sectors for the number of notes in the motif
num_doot_doot_doot_main_sectors = 3
# 4 sub sectors for the different variations of the motif
num_doot_doot_doot_sub_sectors = 4
num_doot_doot_doot_normalized_sectors = (
    num_doot_doot_doot_main_sectors * num_doot_doot_doot_sub_sectors - 1
)

doot_doot_doot_sub_sectors_map = {}
doot_doot_doot_note_values = map(
    lambda midi_note: midi_note["note"], doot_doot_doot_notes
)
unique_doot_doot_doot_notes = sorted(list(set(doot_doot_doot_note_values)))
for note_index, note in enumerate(unique_doot_doot_doot_notes):
    doot_doot_doot_sub_sectors_map[note] = note_index
doot_doot_doot_duration_extension = 500


def fill_applicable_doot_doot_doos(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]
    for doot_doot_doot_index, doot_doot_doot in enumerate(doot_doot_doot_notes):
        note_start_time = doot_doot_doot["start_time"]
        duration = doot_doot_doot["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start
            <= note_start_time + duration + doot_doot_doot_duration_extension
        ):
            # figure out which note of the motif we're in
            doot_doot_doot_main_sector = doot_doot_doot_index % 3
            # figure out which regular sector we're in
            doot_doot_doot_sub_sector = doot_doot_doot_sub_sectors_map[
                doot_doot_doot["note"]
            ]
            doot_doot_doot_normalized_sector = (
                doot_doot_doot_main_sector * num_doot_doot_doot_main_sectors
                + doot_doot_doot_sub_sector
            )
            # get last pixel positions
            doot_doot_doot_starting_pixel = utils.get_sector_starting_pixel(
                doot_doot_doot_normalized_sector,
                num_doot_doot_doot_normalized_sectors,
            )
            doot_doot_doot_ending_pixel = utils.get_sector_ending_pixel(
                doot_doot_doot_normalized_sector,
                num_doot_doot_doot_normalized_sectors,
            )
            # print(
            #     f"dddns: {doot_doot_doot_normalized_sector}, dddsp: {doot_doot_doot_starting_pixel}, dddep: {doot_doot_doot_ending_pixel}",
            #     flush=True,
            # )
            ms_since_fade_start = ms_since_song_start - note_start_time
            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                doot_doot_doot_starting_pixel,
                doot_doot_doot_ending_pixel,
                utils.get_fade_out_color(
                    ms_since_fade_start,
                    duration + doot_doot_doot_duration_extension,
                    (100, 0, 200),
                ),
            )


def play_current_frame(sequence_config):
    fill_applicable_doot_doot_doos(sequence_config)
