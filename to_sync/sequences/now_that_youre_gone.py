import config
import utils
import parse_midi

song_name = "now_that_youre_gone"
bpm = 115
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

doo_doo_doowee_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/doo_doo_doowee.mid", bpm
)

colors = [
    (50, 200, 100),
    (0, 50, 200),
]

unique_doo_doo_doowee_notes = {}
current_color_index = 0
starting_note = doo_doo_doowee_notes[0]["note"]
for doo_doo_doowee_note in doo_doo_doowee_notes:
    if doo_doo_doowee_note["note"] not in unique_doo_doo_doowee_notes:
        unique_doo_doo_doowee_notes[doo_doo_doowee_note["note"]] = {}
    if doo_doo_doowee_note["note"] == starting_note:
        current_color_index += 1
        if current_color_index >= len(colors):
            current_color_index = 0
    doo_doo_doowee_note["color_index"] = current_color_index
# get ordered list of notes from the keys
ordered_unique_doo_doo_doowee_notes = sorted(unique_doo_doo_doowee_notes.keys())
unique_doo_doo_doowee_note_positions = {}
for doo_doo_doowee_index, doo_doo_doowee_note in enumerate(
    ordered_unique_doo_doo_doowee_notes
):
    unique_doo_doo_doowee_note_positions[doo_doo_doowee_note] = doo_doo_doowee_index

fade_in_ms = 1000


def fill_applicable_doo_doo_doowees(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]
    for doo_doo_doowee_index, doo_doo_doowee_note in enumerate(doo_doo_doowee_notes):
        note_start_time = doo_doo_doowee_note["start_time"]
        duration = doo_doo_doowee_note["duration"]
        # if doo_doo_doowee_note["note"] != ordered_unique_doo_doo_doowee_notes[1]:
        #     continue
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            # fade during the beginning and end
            # otherwise hold
            prev_base_color = (0, 0, 0)
            if doo_doo_doowee_index > 0:
                prev_base_color = colors[
                    doo_doo_doowee_notes[doo_doo_doowee_index - 1]["color_index"]
                ]
            cur_base_color = colors[doo_doo_doowee_note["color_index"]]
            if ms_since_song_start <= note_start_time + fade_in_ms:
                multiplier = (
                    note_start_time + fade_in_ms - ms_since_song_start
                ) / fade_in_ms
                # print(
                #     f"msss is {ms_since_song_start}, nst is {note_start_time}, m is {multiplier}",
                #     flush=True,
                # )
                prev_color = tuple(int(multiplier * x) for x in prev_base_color)
                cur_color = tuple(int((1 - multiplier) * x) for x in cur_base_color)
                color = tuple(map(sum, zip(prev_color, cur_color)))
                # print(f"color is {color}", flush=True)
            # elif ms_since_song_start >= note_start_time + duration:
            else:
                multiplier = (note_start_time + duration - ms_since_song_start) / (
                    duration - fade_in_ms
                )
                print(
                    f"msss is {ms_since_song_start}, nst is {note_start_time}, m is {multiplier}",
                    flush=True,
                )
                # prev_color = tuple(int((1 - multiplier) * x) for x in prev_base_color)
                color = tuple(int(multiplier * x) for x in cur_base_color)
                print(f"color is {color}", flush=True)
            # else:
            #     color = cur_base_color

            starting_doo_doo_doowee_pixel = utils.get_sector_starting_pixel(
                unique_doo_doo_doowee_note_positions[doo_doo_doowee_note["note"]],
                len(unique_doo_doo_doowee_notes),
            )
            ending_doo_doo_doowee_pixel = utils.get_sector_ending_pixel(
                unique_doo_doo_doowee_note_positions[doo_doo_doowee_note["note"]],
                len(unique_doo_doo_doowee_notes),
            )
            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                starting_doo_doo_doowee_pixel,
                ending_doo_doo_doowee_pixel,
                color,
            )


def play_current_frame(sequence_config):
    fill_applicable_doo_doo_doowees(sequence_config)
