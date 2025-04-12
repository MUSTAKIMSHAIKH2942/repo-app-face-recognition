from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2
import time
from face_recognition import FaceRecognition

class VideoCaptureThread(QThread):
    update_frame_signal = pyqtSignal(QPixmap)
    error_signal = pyqtSignal(str)

    def __init__(self, camera_url):
        super().__init__()
        self.camera_url = camera_url
        self.face_recognition = FaceRecognition()
        self.running = True

    def run(self):
        try:
            cap = cv2.VideoCapture(self.camera_url)
            if not cap.isOpened():
                raise ConnectionError(f"Failed to open camera: {self.camera_url}")

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    self.error_signal.emit(f"Lost connection to camera: {self.camera_url}")
                    break

                frame = self.face_recognition.update_frame(frame)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                qt_image = QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)
                self.update_frame_signal.emit(QPixmap.fromImage(qt_image))

                time.sleep(0.03)  # Reduce CPU load

        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            cap.release()

    def stop(self):
        self.running = False
        self.requestInterruption()
        self.quit()
        self.wait()
