from midi2audio import FluidSynth

fs = FluidSynth()


def midi2mp3(file_path, output_path='./output.wav'):
    fs.midi_to_audio(file_path, output_path)
