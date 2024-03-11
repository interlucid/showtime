# import pretty_midi

# red_fade = pretty_midi.PrettyMIDI("sequences/red_fade.mid")
# print(red_fade.estimate_tempi())
# print(red_fade.get_onsets())

import mido


ticks_per_beat = 96


def get_previous_note(note, notes):
    for list_note in reversed(notes):
        if list_note["note"] == note:
            return list_note


def get_first_track_notes_and_durations(path, bpm=None, ticks_to_ms=None):
    midi = mido.MidiFile(path)
    # print(midi)
    track_notes = midi.tracks[0]
    notes = []
    running_ticks = 0
    running_ms = 0
    # print(f"ticks_to_ms is {ticks_to_ms}")
    for message in track_notes:
        if bpm:
            tempo = mido.bpm2tempo(bpm)
        # print(f"\n==MSG: {message}")
        running_ticks += message.time
        # print(f"running ticks: {running_ticks}")
        if ticks_to_ms:
            # print("about to run ticks_to_ms")
            running_ms = ticks_to_ms(running_ticks, ticks_per_beat)
        else:
            # note this is += but the previous line is just =
            running_ms += 1000 * mido.tick2second(message.time, ticks_per_beat, tempo)
        # print(message, message.__dict__)
        if message.type == "note_on":
            # if ticks_to_ms:
            #     start_time = running_ms + ticks_to_ms(message.time, ticks_per_beat)
            # else:
            #     start_time = running_ms + 1000 * mido.tick2second(
            #         message.time, ticks_per_beat, tempo
            #     )
            notes.append(
                {
                    "start_time": running_ms,
                    "note": message.note,
                    "velocity": message.velocity,
                }
            )
        if message.type == "note_off":
            # if ticks_to_ms:
            #     end_time = running_ms + ticks_to_ms(message.time, ticks_per_beat)
            # else:
            #     end_time = running_ms + 1000 * mido.tick2second(
            #         message.time, ticks_per_beat, tempo
            #     )
            last_note = get_previous_note(message.note, notes)
            last_note["duration"] = (
                running_ms
                # running_ms
                # + 1000 * mido.tick2second(message.time, ticks_per_beat, tempo)
                - last_note["start_time"]
            )
    # print(notes, flush=True)
    # print(str(notes).replace("},", "},\n"))
    # print("done importing MIDI, about to return", flush=True)
    # return notes[:10]
    return notes


# def get_measure_ms(bpm):
#     return 60 * 1000 / (bpm / 4)


# def ticks_to_ms(ticks_since_song_start, ticks_per_beat):
#     beats_since_song_start = ticks_since_song_start / ticks_per_beat
#     return beats_to_ms(beats_since_song_start)


# def beats_to_ms(beats_since_song_start):
#     # this is 1 less than what it says in Live because their numbering starts at 1, not 0
#     time_signature_change_measure = 10.5
#     time_signature_change_beats = time_signature_change_measure * 4
#     measures_since_song_start = beats_since_song_start / 4
#     # print(f"beats: {beats_since_song_start}, measure: {measures_since_song_start}")
#     # if we are in the first 10.5 measures just return that
#     if measures_since_song_start < time_signature_change_measure:
#         # print("in the first {time_signature_change_measure} measures")
#         return measures_since_song_start * get_measure_ms(120)
#     # otherwise add the ms for the full first 12 measures plus whatever's left
#     else:
#         # print("NOT in the first {time_signature_change_measure} measures")
#         # print(
#         #     f"(measures_since_song_start - time_signature_change_measure) * get_measure_ms(160): {(measures_since_song_start - time_signature_change_measure) * get_measure_ms(160)}"
#         # )
#         return (time_signature_change_measure * get_measure_ms(120)) + (
#             measures_since_song_start - time_signature_change_measure
#         ) * get_measure_ms(160)


# get_first_track_notes_and_durations("sequences/keys/bwah.mid", ticks_to_ms=ticks_to_ms)
