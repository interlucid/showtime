import config
import utils
import parse_midi

song_name = "tell_me_no"
bpm = 93
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

piano_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/piano.mid", bpm
)
piano_colors = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/piano_color.mid", bpm
)
piano_color_map = {
    63: (0, 0, 0),
    64: (0, 150, 20),
    65: (100, 200, 0),
}


# fill in a gradient color from the top
def fill_applicable_pianos(sequence_config):
    song = sequence_config["song"]
    ms_since_song_start = song["ms_since_song_start"]
    # find the MIDI note that we're currently at
    for piano_index, piano in enumerate(piano_notes):
        note_start_time = piano["start_time"]
        duration = piano["duration"]
        if (
            ms_since_song_start >= note_start_time
            and ms_since_song_start <= note_start_time + duration
        ):
            for piano_color_index, current_piano_color_note in enumerate(piano_colors):
                color_start_time = current_piano_color_note["start_time"]
                color_duration = current_piano_color_note["duration"]
                if (
                    ms_since_song_start >= color_start_time
                    and ms_since_song_start <= color_start_time + color_duration
                ):
                    ms_since_note_start = ms_since_song_start - note_start_time
                    # use previous color note if start is more than color start
                    piano_color_note = (
                        piano_colors[piano_color_index - 1]
                        if note_start_time < (color_start_time - 50)
                        else current_piano_color_note
                    )
                    piano_color = (
                        piano_color_map[current_piano_color_note["note"]]
                        if current_piano_color_note["note"] == 63
                        else utils.get_fade_out_color(
                            ms_since_note_start,
                            duration,
                            piano_color_map[piano_color_note["note"]],
                        )
                    )
                    note_percentage = ms_since_note_start / duration
                    # fill in the current amount with the current note color
                    utils.fill_pixels_in_center_split_mirror_range(
                        sequence_config["pixels"],
                        config.num_pixels - config.num_pixels * note_percentage,
                        config.num_pixels
                        - (config.num_pixels * note_percentage - config.num_pixels / 2),
                        piano_color,
                    )
                    # fill in the remaining amount with the previous color if exists
                    # if piano_index > 0:
                    #     prev_piano_base_color = piano_color_map[
                    #         piano_color_notes[piano_color_index - 1]["note"]
                    #     ]
                    #     # prev_piano_color = utils.get_fade_out_color(
                    #     #     duration - ms_since_note_start,
                    #     #     duration,
                    #     #     prev_piano_base_color,
                    #     # )
                    #     prev_piano_color = (
                    #         base_color
                    #         if piano["note"] == 63
                    #         else [color_part / 30 for color_part in prev_piano_base_color]
                    #     )
                    #     utils.fill_pixels_in_center_split_mirror_range(
                    #         sequence_config["pixels"],
                    #         0,
                    #         config.num_pixels - config.num_pixels * note_percentage,
                    #         prev_piano_color,
                    #     )


def fill_applicable_guitars(sequence_config):
    pass


def play_current_frame(sequence_config):
    fill_applicable_pianos(sequence_config)
    fill_applicable_guitars(sequence_config)
