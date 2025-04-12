import cv2
from PyQt5.QtCore import QThread, pyqtSignal,Qt
from PyQt5.QtGui import QImage, QPixmap
from face_recognition import FaceRecognition

class VideoStream(QThread):
    update_frame_signal = pyqtSignal(QPixmap)

    def __init__(self, camera_index, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.running = True
        self.face_recognition = FaceRecognition()

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Apply face recognition
                frame = self.face_recognition.update_frame_with_recognition(frame)

                # Convert frame to QPixmap for display
                height, width, channels = frame.shape
                bytes_per_line = channels * width
                qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
                pixmap = QPixmap.fromImage(qt_image)

                # Emit the updated frame
                self.update_frame_signal.emit(pixmap.scaled(640, 480, Qt.KeepAspectRatio))
            else:
                break
        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
        

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QGridLayout, QTextEdit, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import add_camera_screen

class UserDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Dashboard")
        self.setGeometry(100, 100, 1400, 900)

        # Set black and green color theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #15171c;
            }
            QPushButton {
                background-color: #5371ff;
                color: #ffffff;  /* Text color changed to white */
                font-size: 14px;
                padding: 10px;
                border: none;
                border-radius: 10px;  /* Added border radius */
            }
            QPushButton:hover {
                background-color: #3a5bff;  /* Slightly darker blue on hover */
            }
            QListWidget, QTextEdit, QComboBox {
                background-color: #15171c;
                color: #ffffff;  /* Text color changed to white */
                border: 1px solid #5371ff;
                font-size: 14px;
                border-radius: 5px;  /* Added border radius */
            }
            QLabel {
                color: #ffffff;  /* Text color changed to white */
                font-size: 16px;
            }
        """)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Top horizontal plane (centered options)
        top_panel = QHBoxLayout()
        main_layout.addLayout(top_panel)

        # Add stretch to center the buttons
        top_panel.addStretch()
        top_panel.addWidget(QPushButton("Live Feed"))
        top_panel.addWidget(QPushButton("Replay"))
        top_panel.addWidget(QPushButton("Export"))
        top_panel.addStretch()

        # User section (photo and name)
        user_section = QVBoxLayout()
        user_photo = QLabel()
        user_photo.setPixmap(QPixmap("user_photo.png").scaled(50, 50, Qt.KeepAspectRatio))  # Replace with actual photo path
        user_section.addWidget(user_photo)
        user_section.addWidget(QLabel("User Name"))
        top_panel.addLayout(user_section)

        # Middle section (left, middle, right panels)
        middle_section = QHBoxLayout()
        main_layout.addLayout(middle_section)

        # Left panel (Add Camera, Camera List, and Grid View Options)
        left_panel = QVBoxLayout()
        left_panel.addWidget(QPushButton("Add Camera"))
        camera_list = QListWidget()
        camera_list.addItems([f"Camera O{i}" for i in range(1, 10)] + ["Camera IO"])
        left_panel.addWidget(camera_list)

        # Grid View Options (Combo Box)
        grid_options = QComboBox()
        grid_options.addItems(["2X2","4x4"])
        grid_options.currentTextChanged.connect(self.change_grid_view)
        left_panel.addWidget(QLabel("Grid View:"))
        left_panel.addWidget(grid_options)

        middle_section.addLayout(left_panel)

        # Middle panel (Grid View for Video Feeds)
        self.middle_panel = QGridLayout()
        self.current_grid_size = 2  # Default grid size
        self.update_grid_view(2)  # Initialize with 3x3 grid
        middle_section.addLayout(self.middle_panel, stretch=5)  # Middle panel is bigger

        # Right panel (Camera Management and Activity Log)
        right_panel = QVBoxLayout()
        right_panel.addWidget(QPushButton("Load Camera"))
        right_panel.addWidget(QPushButton("Save Camera"))
        right_panel.addWidget(QPushButton("Add IP Camera"))
        activity_log = QTextEdit()
        activity_log.setReadOnly(True)
        activity_log.setPlaceholderText("Activity Log: Person Detected: John Doe")
        right_panel.addWidget(activity_log)
        middle_section.addLayout(right_panel, stretch=2)  # Right panel is narrower

        # Bottom options (Add Known Person, User, License Validation, Exit)
        bottom_panel = QHBoxLayout()
        bottom_panel.addWidget(QPushButton("Add Known Person"))
        bottom_panel.addWidget(QPushButton("User"))
        bottom_panel.addWidget(QPushButton("License Validation"))
        bottom_panel.addWidget(QPushButton("Exit"))
        main_layout.addLayout(bottom_panel)

    def open_add_camera_screen(self):
        """Open the Add Camera screen."""
        self.add_camera_screen = add_camera_screen()
        self.add_camera_screen.show()

    def change_grid_view(self, text):
        """Change the grid view based on the selected option."""
        if text == "2X2":
            self.update_grid_view(2)
        elif text == "4x4":
            self.update_grid_view(4)
        # elif text == "6x6":
        #     self.update_grid_view(6)
        # elif text == "8x8":
        #     self.update_grid_view(8)

  
    def update_grid_view(self, size):
        """Update the video feed grid layout dynamically with rounded borders."""
        # Remove existing widgets
        while self.middle_panel.count():
            item = self.middle_panel.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.current_grid_size = size  # Update grid size
        
        for i in range(size):
            for j in range(size):
                feed_widget = QLabel(f"Feed {i * size + j + 1}")  # Placeholder for camera feeds
                # feed_label.setStyleSheet("border: 2px solid #5371ff; color: #ffffff;")  
                feed_widget.setAlignment(Qt.AlignCenter)
                
                # Apply rounded corners and border styling
                feed_widget.setStyleSheet("""
                    background-color: black;
                    min-height: 150px;
                    border-radius: 15px; /* Rounded corners */
                    border: 2px solid #555; /* Optional border */
                    color: white;
                    border: 2px solid #5371ff; color: #ffffff;
                """)
                
                self.middle_panel.addWidget(feed_widget, i, j)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = UserDashboard()
    dashboard.show()
    sys.exit(app.exec_())