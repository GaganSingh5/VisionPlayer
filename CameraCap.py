import argparse
import time

from cv2 import CASCADE_SCALE_IMAGE, equalizeHist, cvtColor, COLOR_BGR2GRAY, CascadeClassifier, VideoCapture, cv2
import numpy


class CameraCap:
    def __init__(self):
        self.play = False
        self.pause = False
        self.fist_captured = True
        self.palm_captured = True
        self.cam_capture = False
        # self.parser = argparse.ArgumentParser(description='Code for Cascade Classifier')
        # self.parser.add_argument('--fist_cascade', help='Path to fist cascade.',
        #                          default='C:\\Users\\THING007\\PycharmProjects\\Whatever\\fist')
        # self.args = self.parser.parse_args()
        # self.fist_cascade_name = self.args.fist_cascade
        self.fist_cascade = CascadeClassifier('fist')
        self.palm_cascade = CascadeClassifier('palm')


    def camera(self):
        self.camera = cv2.VideoCapture(0)

    def capture_frame(self):
        ret, frame = self.camera.read()
        cv2.waitKey(1)
        return frame

    def detect(self):
            while self.camera.isOpened() and self.cam_capture:
                frame = self.capture_frame()
                frame_gray = cvtColor(frame, COLOR_BGR2GRAY)
                frame_gray = equalizeHist(frame_gray)
                fist = self.fist_cascade.detectMultiScale(frame_gray, 1.3, 2, flags=CASCADE_SCALE_IMAGE)
                palm = self.palm_cascade.detectMultiScale(frame_gray, 1.3, 2, flags=CASCADE_SCALE_IMAGE)
                for (x, y, w, h) in palm:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, ' palm detected (song playing) ', (2*x - w, 2*y - h), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
                if type(fist) == numpy.ndarray and type(palm) == tuple and self.fist_captured:
                    self.pause = True
                    self.fist_captured = False
                    self.palm_captured = True
                elif type(palm) == numpy.ndarray and type(fist) == tuple and self.palm_captured:
                    self.play = True
                    self.fist_captured = True
                    self.palm_captured = False

                cv2.imshow('frame', frame)

    def cam_close(self):
        self.camera.release()

# if __name__ == '__main__':
#     cap = CameraCap()
#     cap.detect()
