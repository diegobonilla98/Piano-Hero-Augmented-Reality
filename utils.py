import cv2
import numpy as np
from threading import Thread


class WebcamStream:
    def __init__(self, stream_id=0):
        self.stream_id = stream_id
        self.vcap = cv2.VideoCapture(self.stream_id)
        self.grabbed, self.frame = self.vcap.read()
        self.stopped = True
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True

    def start(self):
        self.stopped = False
        self.t.start()

    def update(self):
        while True:
            if self.stopped is True:
                break
            self.grabbed, self.frame = self.vcap.read()
            if self.grabbed is False:
                self.stopped = True
                break
        self.vcap.release()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


class Note:
    def __init__(self, pos, off_y, M, is_on, speed=2.71):
        self.pos = pos
        self.off_y = off_y
        self.M = np.linalg.inv(M)
        self.dead = False
        self.is_on = is_on
        self.speed = speed

    def update(self):
        self.off_y += self.speed
        if self.off_y >= -self.speed:
            self.dead = True

    def display(self, canvas):
        a_note_x, a_note_y, a = np.matmul(self.M, [self.pos, self.off_y, 1])
        cv2.circle(canvas, (int(a_note_x / a), int(a_note_y / a)), 3, (255, 0, 0), -1, cv2.LINE_AA)  # (186, 112, 248)
