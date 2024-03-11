import config
import utils
import parse_midi

song_name = "your_dream"
bpm = 120
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

woo_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/woo.mid", bpm
)

unique_woo_notes = []
for woo_note in woo_notes:
    if woo_note["note"] not in unique_woo_notes:
        unique_woo_notes.append(woo_note["note"])
unique_woo_notes.sort()
unique_woo_note_positions = {}
for woo_index, woo_note in enumerate(unique_woo_notes):
    unique_woo_note_positions[woo_note] = woo_index
# print(unique_woo_note_positions)

# print(woo_notes)

slide_ms = 600


def fill_applicable_woos(sequence_config):
    song = sequence_config["song"]
    # if we're where a note should be played
    # print(
    #     f"msss: {song['ms_since_song_start']}, nst: {note_start_time}, d: {duration}",
    #     flush=True,
    # )

    # find the MIDI note that we're currently at
    for woo_index, woo in enumerate(woo_notes):
        note_start_time = woo["start_time"]
        duration = woo["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            ms_since_fade_start = song["ms_since_song_start"] - note_start_time
            starting_woo_pixel = utils.get_sector_starting_pixel(
                unique_woo_note_positions[woo["note"]], len(unique_woo_notes)
            )
            ending_woo_pixel = utils.get_sector_ending_pixel(
                unique_woo_note_positions[woo["note"]], len(unique_woo_notes)
            )
            # if we're in the first bit of time for this note, play the frame of the sliding animation
            # otherwise hold
            if (
                woo_index > 0
                and song["ms_since_song_start"] <= note_start_time + slide_ms
            ):
                # get last pixel positions
                last_starting_woo_pixel = utils.get_sector_starting_pixel(
                    unique_woo_note_positions[woo_notes[woo_index - 1]["note"]],
                    len(unique_woo_notes),
                )
                last_ending_woo_pixel = utils.get_sector_ending_pixel(
                    unique_woo_note_positions[woo_notes[woo_index - 1]["note"]],
                    len(unique_woo_notes),
                )
                starting_woo_pixel_diff = starting_woo_pixel - last_starting_woo_pixel
                ending_woo_pixel_diff = ending_woo_pixel - last_ending_woo_pixel
                linear_move_multiplier = (
                    song["ms_since_song_start"] - note_start_time
                ) / slide_ms
                move_multiplier = utils.get_parametric_blend(linear_move_multiplier)
                # print(
                #     f"lmm: {linear_move_multiplier}, mm: {move_multiplier}", flush=True
                # )
                slide_starting_woo_pixel = (
                    last_starting_woo_pixel + move_multiplier * starting_woo_pixel_diff
                )
                slide_ending_woo_pixel = (
                    last_ending_woo_pixel + move_multiplier * ending_woo_pixel_diff
                )
                utils.fill_pixels_in_center_split_mirror_range(
                    sequence_config["pixels"],
                    slide_starting_woo_pixel,
                    slide_ending_woo_pixel,
                    (200, 0, 50),
                )
            else:
                utils.fill_pixels_in_center_split_mirror_range(
                    sequence_config["pixels"],
                    starting_woo_pixel,
                    ending_woo_pixel,
                    (200, 0, 50),
                )
            # sequence_config["pixels"].fill(
            #     utils.get_fade_out_color(
            #         ms_since_fade_start,
            #         duration,
            #         tuple(round(x * (woo["velocity"] / 127)) for x in (200, 0, 50)),
            #     )
            # )
            break


def play_current_frame(sequence_config):
    fill_applicable_woos(sequence_config)
