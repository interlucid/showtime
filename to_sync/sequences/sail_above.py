import config
import utils
import parse_midi

song_name = "sail_above"
bpm = 140
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
            ms_since_fade_start = song["ms_since_song_start"] - note_start_time
            sequence_config["pixels"].fill(
                utils.get_fade_out_color(
                    ms_since_fade_start,
                    duration,
                    tuple(
                        round(x * (flash["velocity"] / 127)) for x in (150, 150, 150)
                    ),
                )
            )
            break


def play_current_frame(sequence_config):
    fill_applicable_flashes(sequence_config)
