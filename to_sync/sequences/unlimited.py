import config
import utils
import parse_midi

song_name = "unlimited"
bpm = 125
song_measure_ms = utils.get_measure_ms(bpm)
song_timing = utils.get_song_timing_constants(song_measure_ms)

flash_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/flash.mid", bpm
)


def fill_applicable_flashes(sequence_config):
    song = sequence_config["song"]
    # if we're where a note should be played
    # print(
    #     f"msss: {song['ms_since_song_start']}, nst: {note_start_time}, d: {duration}",
    #     flush=True,
    # )

    # find the MIDI note that we're currently at
    for flash in flash_notes:
        note_start_time = flash["start_time"]
        duration = flash["duration"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            utils.fill_average(
                sequence_config["pixels"],
                tuple(round(x * (flash["velocity"] / 127)) for x in (150, 150, 150)),
            )
            # sequence_config["pixels"].fill(
            #     utils.get_fade_out_color(
            #         ms_since_fade_start,
            #         duration,
            #         tuple(
            #             round(x * (flash["velocity"] / 127))
            #             for x in (0, 0, 0)
            #             # round(x * (flash["velocity"] / 127)) for x in (150, 150, 150)
            #         ),
            #     )
            # )
            break


pluck_notes = parse_midi.get_first_track_notes_and_durations(
    f"{config.sequences_directory}/{song_name}/pluck.mid", bpm
)
unique_pluck_notes = []
for pluck_note in pluck_notes:
    if pluck_note["note"] not in unique_pluck_notes:
        unique_pluck_notes.append(pluck_note["note"])
unique_pluck_notes.sort()
unique_pluck_note_positions = {}
colors = [(155, 0, 155), (55, 0, 225), (230, 20, 40), "rainbow"]
for pluck_index, pluck_note in enumerate(unique_pluck_notes):
    unique_pluck_note_positions[pluck_note] = colors[pluck_index]


def fill_applicable_plucks(sequence_config):
    song = sequence_config["song"]
    # if we're where a note should be played
    # print(
    #     f"msss: {song['ms_since_song_start']}, nst: {note_start_time}, d: {duration}",
    #     flush=True,
    # )

    # find the MIDI note that we're currently at
    for pluck in pluck_notes:
        note_start_time = pluck["start_time"]
        duration = song_timing["song_half_measure_ms"]
        if (
            song["ms_since_song_start"] >= note_start_time
            and song["ms_since_song_start"] <= note_start_time + duration
        ):
            if unique_pluck_note_positions[pluck["note"]] == "rainbow":
                if "color" not in pluck:
                    multiplier = 4
                    position = (
                        (
                            song["ms_since_song_start"]
                            % (song_timing["song_measure_ms"] * multiplier)
                        )
                        / (song_timing["song_measure_ms"] * multiplier)
                        * 255
                    )
                    pluck["color"] = utils.get_rainbow_loop_color(position)
                color = pluck["color"]
            else:
                color = unique_pluck_note_positions[pluck["note"]]

            ms_since_fade_start = song["ms_since_song_start"] - note_start_time
            pluck_location_value = utils.get_exponential_dropoff(
                ms_since_fade_start / duration
            )
            previous_pluck_location_value = utils.get_exponential_dropoff(
                max(ms_since_fade_start - config.sleep_ms, 0) / duration
            )
            utils.fill_pixels_in_center_split_mirror_range(
                sequence_config["pixels"],
                pluck_location_value,
                # if the previous value is more than 2 away, use that
                # otherwise make the dyoo animation at least 2 LEDs wide
                max(previous_pluck_location_value, pluck_location_value + 2),
                color,
                2,
            )
            # sequence_config["pixels"].fill(
            #     utils.get_fade_out_color(
            #         ms_since_fade_start,
            #         duration,
            #         tuple(
            #             round(x * (pluck["velocity"] / 127)) for x in (150, 150, 150)
            #         ),
            #     )
            # )
            # break


def play_current_frame(sequence_config):
    fill_applicable_plucks(sequence_config)
    fill_applicable_flashes(sequence_config)
