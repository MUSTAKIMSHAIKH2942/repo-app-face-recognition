import sys
import os
import cv2
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QMessageBox, QComboBox, QLabel
)
from PyQt5.QtCore import Qt


class AddPersonForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Add Known Person')
        self.setGeometry(0, 0, 500, 400)  # Set a medium size for the window
        self.center()  # Center the window on the screen

        # Set black background and white text for the form
        self.setStyleSheet("""
            QWidget {
                background-color: black;
                color: white;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit, QComboBox, QPushButton {
                font-size: 14px;
                padding: 5px;
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #222;
            }
        """)

        layout = QVBoxLayout()

        # Name input
        self.name_label = QLabel("Enter Person's Name:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        # Camera selection
        self.camera_label = QLabel("Select Camera:")
        self.camera_combo = QComboBox()
        self.load_cameras()
        layout.addWidget(self.camera_label)
        layout.addWidget(self.camera_combo)

        # Upload button
        self.upload_button = QPushButton("Upload Image/Video")
        self.upload_button.clicked.connect(self.upload_media)
        layout.addWidget(self.upload_button)

        # Access camera button
        self.access_camera_button = QPushButton("Access Selected Camera")
        self.access_camera_button.clicked.connect(self.access_camera)
        layout.addWidget(self.access_camera_button)

        self.setLayout(layout)

    def center(self):
        """Center the window on the screen."""
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def load_cameras(self):
        """Load cameras from camera.csv file."""
        if not os.path.exists('data/camera.csv'):
            QMessageBox.warning(self, "Error", "camera.csv file not found.")
            return

        with open('data/camera.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    self.camera_combo.addItem(row[0], row[1])  # row[0] = camera name, row[1] = IP address

    def upload_media(self):
        """Handle image/video upload."""
        person_name = self.name_input.text().strip()
        if not person_name:
            QMessageBox.warning(self, "Error", "Please enter the person's name.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image/Video", "", "Images (*.png *.jpg *.jpeg);;Videos (*.mp4 *.avi)", options=options
        )
        if not file_name:
            return

        person_folder = os.path.join("traning_images", person_name)
        os.makedirs(person_folder, exist_ok=True)

        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Handle image upload
            self.save_image(file_name, person_folder)
        else:
            # Handle video upload
            self.extract_frames_from_video(file_name, person_folder)

    def save_image(self, image_path, person_folder):
        """Save uploaded image to the person's folder."""
        image_name = os.path.basename(image_path)
        destination = os.path.join(person_folder, image_name)
        os.rename(image_path, destination)
        QMessageBox.information(self, "Success", "Image saved successfully.")

    def extract_frames_from_video(self, video_path, person_folder):
        """Extract frames from video and save them as images."""
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            frame_name = f"{os.path.basename(person_folder)}_frame_{frame_count}.jpg"
            frame_path = os.path.join(person_folder, frame_name)
            cv2.imwrite(frame_path, frame)

        cap.release()
        QMessageBox.information(self, "Success", f"Extracted {frame_count} frames from the video.")

        if frame_count < 450:
            QMessageBox.warning(self, "Warning", "Less than 450 frames extracted. Please upload more images or videos.")

    def access_camera(self):
        """Access the selected camera using its IP address."""
        selected_camera_ip = self.camera_combo.currentData()
        if not selected_camera_ip:
            QMessageBox.warning(self, "Error", "No camera selected.")
            return

        cap = cv2.VideoCapture(selected_camera_ip)
        if not cap.isOpened():
            QMessageBox.warning(self, "Error", "Unable to access the selected camera.")
            return

        QMessageBox.information(self, "Success", f"Accessing camera: {selected_camera_ip}")
        # You can add code here to capture frames from the camera and process them.


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = AddPersonForm()
    main_window.show()
    sys.exit(app.exec_())