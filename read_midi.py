from mido import MidiFile, tick2second


class MIDINote:
    def __init__(self, is_on, note, time):
        self.is_on = '_on' in is_on
        self.note = note
        self.time = time

    def __repr__(self):
        return f"Note {'on' if self.is_on else 'off'} in {self.note} at {self.time}"


def convert_midi_to_notes(file_path, piano_track_name='piano'):
    mid = MidiFile(file_path)
    ticks_per_beat = mid.ticks_per_beat
    total_length = mid.length
    tempo = 500_000

    print(f"Found {len(mid.tracks)} tracks named {[l.name.lower() for l in mid.tracks]}.")
    piano_tracks = list(filter(lambda l: piano_track_name.lower() in l.name.lower(), mid.tracks))
    if len(piano_tracks) == 0:
        raise LookupError(f"No {piano_track_name} track found! Try another MIDI file.")
    piano_tracks = sorted(piano_tracks, key=lambda l: len(l))[-2:]
    if len(piano_tracks) not in [1, 2]:
        raise ProcessLookupError("Error parsing data... Try another MIDI file.")

    try:
        only_notes_tracks = []
        for piano_track in piano_tracks:
            only_notes = list(filter(lambda l: 'note' in l.type, piano_track))
            only_notes = [MIDINote(l.type, l.note, tick2second(l.time, ticks_per_beat, tempo)) for l in only_notes]  # tempo * l.time / ticks_per_beat
            for i in range(1, len(only_notes)):
                only_notes[i].time += only_notes[i - 1].time
            only_notes_tracks.append(only_notes)
    except Exception:
        raise Exception("Error parsing data... Try another MIDI file.")
    return only_notes_tracks


if __name__ == '__main__':
    file_path = '/media/bonilla/My Book/MIDI/mz_311_1.mid'
    only_notes = convert_midi_to_notes(file_path)
    print()
