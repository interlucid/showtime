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
woo_note_colors = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/woo_color.mid", bpm
)
woo_note_fades = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/woo_fade.mid", bpm
)
unique_woo_notes = []
for woo_note in woo_notes:
    if woo_note["note"] not in unique_woo_notes:
        unique_woo_notes.append(woo_note["note"])
unique_woo_notes.sort()
unique_woo_note_positions = {}
for woo_index, woo_note in enumerate(unique_woo_notes):
    unique_woo_note_positions[woo_note] = woo_index
woo_slide_ms = 800
woo_color_map = {
    60: (100, 0, 20),
    61: (100, 0, 100),
    62: (100, 0, 200),
}


def get_fade_multiplier(song, note_fades, note_start_time, duration):
    for fade_note_index, fade_note in enumerate(note_fades):
        fade_start_time = fade_note["start_time"]
        if (
            song["ms_since_song_start"] >= fade_start_time
            and song["ms_since_song_start"] <= fade_start_time + fade_note["duration"]
        ):
            return 1 - (song["ms_since_song_start"] - note_start_time) / duration
    return 1


def fill_applicable_woos(sequence_config):
    # global woo_previous_color
    song = sequence_config["song"]

    # find the MIDI note that we're currently at
    for woo_index, woo in enumerate(woo_notes):
        note_start_time = woo["start_time"]
        duration = woo["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            for woo_color_note_index, woo_color_note in enumerate(woo_note_colors):
                color_start_time = woo_color_note["start_time"]
                if (
                    song["ms_since_song_start"] >= color_start_time
                    and song["ms_since_song_start"]
                    <= color_start_time + woo_color_note["duration"]
                ):
                    # print(woo_color_note)
                    woo_current_color = woo_color_map[woo_color_note["note"]]
                    woo_previous_color = (
                        woo_color_map[woo_note_colors[woo_color_note_index - 1]["note"]]
                        if woo_color_note_index > 0
                        else woo_current_color
                    )
                    # break otherwise a later color will be used
                    break
            note_fade_multiplier = get_fade_multiplier(
                song, woo_note_fades, note_start_time, duration
            )
            # other
            starting_woo_pixel = utils.get_sector_starting_pixel(
                unique_woo_note_positions[woo["note"]], len(unique_woo_notes)
            )
            ending_woo_pixel = utils.get_sector_ending_pixel(
                unique_woo_note_positions[woo["note"]], len(unique_woo_notes)
            )
            # if we're in the first bit of time for this note, play the frame of the sliding animation
            # also animate the color change if there is one
            # otherwise hold
            if (
                woo_index > 0
                and song["ms_since_song_start"] <= note_start_time + woo_slide_ms
            ):
                # movement
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
                ) / woo_slide_ms
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

                # color
                # decide whether to use the previous color
                if song["ms_since_song_start"] - color_start_time > woo_slide_ms:
                    woo_previous_color = woo_current_color
                woo_previous_color_amount = tuple(
                    map(
                        lambda x: round((1 - linear_move_multiplier) * x),
                        woo_previous_color,
                    )
                )
                woo_current_color_amount = tuple(
                    map(
                        lambda x: round(linear_move_multiplier * x),
                        woo_current_color,
                    )
                )
                woo_transition_color = tuple(
                    [
                        int(min(sum(x), 255))
                        for x in zip(
                            *[woo_previous_color_amount, woo_current_color_amount]
                        )
                    ]
                )

                woo_transition_fade_color = tuple(
                    map(
                        lambda x: round((note_fade_multiplier) * x),
                        woo_transition_color,
                    )
                )

                utils.fill_pixels_in_center_split_mirror_range(
                    sequence_config["pixels"],
                    slide_starting_woo_pixel,
                    slide_ending_woo_pixel,
                    woo_transition_fade_color,
                )
            else:
                woo_fade_color = tuple(
                    map(
                        lambda x: round((note_fade_multiplier) * x),
                        woo_current_color,
                    )
                )
                utils.fill_pixels_in_center_split_mirror_range(
                    sequence_config["pixels"],
                    starting_woo_pixel,
                    ending_woo_pixel,
                    woo_fade_color,
                )
            break


baum_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/baum.mid", bpm
)
baum_color = (40, 40, 200)


def fill_applicable_baums(sequence_config):
    song = sequence_config["song"]

    # find the MIDI note that we're currently at
    for baum in baum_notes:
        note_start_time = baum["start_time"]
        duration = baum["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):

            ms_since_fade_start = song["ms_since_song_start"] - note_start_time
            baum_location_value = utils.get_exponential_dropoff(
                ms_since_fade_start / duration
            )
            previous_baum_location_value = utils.get_exponential_dropoff(
                max(ms_since_fade_start - config.sleep_ms, 0) / duration, 2 / 3
            )
            note_fade_multiplier = get_fade_multiplier(
                song, woo_note_fades, note_start_time, duration
            )
            baum_fade_color = tuple(
                map(
                    lambda x: round((note_fade_multiplier) * x),
                    baum_color,
                )
            )
            utils.fill_pixels_in_four_split_mirror_range(
                sequence_config["pixels"],
                baum_location_value,
                # if the previous value is more than 2 away, use that
                # otherwise make the dyoo animation at least 2 LEDs wide
                max(previous_baum_location_value, baum_location_value + 2),
                baum_fade_color,
                2,
            )


lead_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/lead.mid", bpm
)
lead_pixel_locations = {}
num_lead_sectors = 12


def play_current_frame(sequence_config):
    fill_applicable_woos(sequence_config)
    utils.fill_applicable_notes(
        sequence_config,
        lead_notes,
        lead_pixel_locations,
        num_lead_sectors,
        (220, 70, 0),
    )
    fill_applicable_baums(sequence_config)
