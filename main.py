import time
from utils import cv2, np, WebcamStream, Note
from read_midi import convert_midi_to_notes
from playsound import playsound
from midi_to_mp3 import midi2mp3
import simpleaudio as sa


MIDI_FILE = './midis/Ludovico Einaudi - Le Onde.mid'

# midi2mp3(MIDI_FILE)
music = sa.WaveObject.from_wave_file('output.wav')

N_NOTES = 70
FPS = 30

video = WebcamStream(1)
video.start()

PLAY_SONG = True

piano_4_points = np.array([[134, 376], [521, 169], [571, 185], [187, 423]], np.float32)
new_w = 122.5 * 2
new_h = 15 * 2
new_points = np.array([[0, 0], [new_w, 0], [new_w, new_h], [0, new_h]], np.float32)
M = cv2.getPerspectiveTransform(piano_4_points, new_points)

if PLAY_SONG:
    only_notes_tracks = convert_midi_to_notes(file_path=MIDI_FILE, piano_track_name="piano")
    only_notes_tracks = [list(filter(lambda l: 108 >= l.note >= 21, only_notes_track)) for only_notes_track in only_notes_tracks]
    notes = []
    for only_notes_track in only_notes_tracks:
        for n in only_notes_track:
            notes.append(Note(new_w / N_NOTES * (n.note - 26), (-n.time * FPS * 5) - 500, M, n.is_on, 4.8))
    notes = list(filter(lambda l: l.is_on, notes))

infinity_point = -500
notes_plane = []
for x, y in [[0, infinity_point], [new_w, infinity_point], [new_w, 0], [0, 0]]:
    a_notes_x, a_notes_y, a = np.matmul(np.linalg.inv(M), [x, y, 1])
    notes_plane.append([int(a_notes_x / a), int(a_notes_y / a)])
notes_plane_x = np.linspace(0, new_w, num=N_NOTES)
notes_lines = []
for x in notes_plane_x:
    a_notes_x1, a_notes_y1, a1 = np.matmul(np.linalg.inv(M), [x, 0, 1])
    a_notes_x2, a_notes_y2, a2 = np.matmul(np.linalg.inv(M), [x, infinity_point, 1])
    notes_lines.append([int(a_notes_x1 / a1), int(a_notes_y1 / a1), int(a_notes_x2 / a2), int(a_notes_y2 / a2)])

music_started = False

while True:
    frame = video.read()
    init_t = time.time()

    canvas = frame.copy()
    canvas_piano_persp = frame.copy()
    cv2.drawContours(canvas_piano_persp, [np.expand_dims(np.int32(piano_4_points), axis=1)], 0, (170, 210, 170), -1, cv2.LINE_AA)
    cv2.drawContours(canvas_piano_persp, [np.expand_dims(np.array(notes_plane, np.int32), axis=1)], 0, (200, 200, 200), -1, cv2.LINE_AA)
    for x1, y1, x2, y2 in notes_lines:
        cv2.line(canvas_piano_persp, (x1, y1), (x2, y2), (255, 255, 255), 1, cv2.LINE_AA)
    canvas = cv2.addWeighted(canvas, 0.6, canvas_piano_persp, 0.4, 1)

    if PLAY_SONG:
        for note in reversed(notes):
            note.update()
            note.display(canvas)
            if note.dead:
                notes.remove(note)
                if not music_started:
                    music.play()
                    music_started = True

    cv2.imshow("Video Stream", cv2.pyrUp(canvas))
    time_spent = int((1. / FPS - (time.time() - init_t)) * 1000)
    key = cv2.waitKey(time_spent if time_spent > 1 else 1)
    # print("FPS:", 1 / (time.time() - init_t))
    if key == ord('q'):
        break

cv2.destroyAllWindows()
video.stop()
