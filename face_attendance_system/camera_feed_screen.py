import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from face_recognition import detect_faces
from PyQt5.QtGui import *
class CameraFeedScreen(QWidget):
    def __init__(self, camera_name):
        super().__init__()
        self.setWindowTitle(camera_name)
        self.video_label = QLabel(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_label)
        self.setLayout(self.layout)

        self.cap = cv2.VideoCapture(0)  # Default Camera
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = detect_faces(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = channel * width
            image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.cap.release()
