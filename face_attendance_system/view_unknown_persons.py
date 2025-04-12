import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QMessageBox, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class UnknownPersonsViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unknown Persons Data")
        self.setGeometry(150, 150, 600, 500)
        self.setStyleSheet("background-color: white;")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title_label = QLabel("Unknown Persons Log")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.title_label)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.list_widget)

        self.load_unknown_persons()

        self.setLayout(layout)

    def load_unknown_persons(self):
        folder_path = "unknown_persons/"  # Adjust folder path if necessary
        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "No Data", "Unknown persons folder does not exist.")
            return

        images = sorted(os.listdir(folder_path), reverse=True)  # Latest images first
        if not images:
            QMessageBox.information(self, "No Records", "No unknown persons detected.")
            return

        for img_file in images:
            if img_file.endswith((".png", ".jpg", ".jpeg")):
                timestamp = img_file.replace("unknown_", "").replace(".jpg", "").replace(".png", "").replace(".jpeg", "")
                formatted_time = f"Timestamp: {timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:]}"
                
                item = QListWidgetItem(formatted_time)
                item.setTextAlignment(Qt.AlignCenter)

                self.list_widget.addItem(item)

    def show_viewer(self):
        self.show()


def view_unknown_persons(self):
    self.viewer = UnknownPersonsViewer()
    self.viewer.show()


# import sys
# import json
# import cv2
# import os
# import numpy as np
# import csv
# from PyQt5.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QGridLayout, QTextEdit, QComboBox
# ,QMessageBox,QDialog,QTableWidgetItem,QTableWidget,QHeaderView)
# from PyQt5.QtGui import QPixmap, QImage
# from PyQt5.QtCore import Qt, QTimer
# import pandas as pd
# from add_camera_screen import AddCameraDialog
# # Face detection model


# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# recognizer = cv2.face.LBPHFaceRecognizer_create()
# model_path = "trained_model.yml"
# data_path = "data/training_images"
# logs_file = "data/logs.csv"

# if os.path.exists(model_path):
#     recognizer.read(model_path)
# else:
#     recognizer = None  # No trained model yet

# class CameraStream(QLabel):
#     def __init__(self, ip):
#         super().__init__()
#         self.ip = ip
#         self.cap = cv2.VideoCapture(ip)
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_frame)
#         self.timer.start(30)
    
#     def update_frame(self):
#         ret, frame = self.cap.read()
#         if ret:
#             frame, face_names = self.process_frame(frame)
#             self.log_faces(face_names)
#             self.display_frame(frame)
    
#     def process_frame(self, frame):
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#         face_names = []
        
#         for (x, y, w, h) in faces:
#             face_img = gray[y:y+h, x:x+w]
#             name = "Unknown"
#             color = (0, 0, 255)  # Red for unknown
            
#             if recognizer:
#                 label, confidence = recognizer.predict(face_img)
#                 if confidence < 80:  # Confidence threshold
#                     name = f"Person {label}"
#                     color = (0, 255, 0)  # Green for known
            
#             cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
#             cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
#             face_names.append(name)
        
#         return frame, face_names
    
#     def log_faces(self, face_names):
#         if face_names:
#             with open(logs_file, 'a', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow([face_names, cv2.getTickCount()])
    
#     def display_frame(self, frame):
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         h, w, ch = rgb_frame.shape
#         bytes_per_line = ch * w
#         qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
#         self.setPixmap(QPixmap.fromImage(qimg))
    
#     def closeEvent(self, event):
#         self.cap.release()
#         event.accept()

# class UserDashboard(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Camera Dashboard")
#         self.setGeometry(100, 100, 1400, 900)
#         self.setStyleSheet("""
#                     QMainWindow {
#                         background-color: #15171c;
#                     }
#                     QPushButton {
#                         background-color: #5371ff;
#                         color: #ffffff;  /* Text color changed to white */
#                         font-size: 14px;
#                         padding: 10px;
#                         border: none;
#                         border-radius: 10px;  /* Added border radius */
#                     }
#                     QPushButton:hover {
#                         background-color: #3a5bff;  /* Slightly darker blue on hover */
#                     }
#                     QListWidget, QTextEdit, QComboBox {
#                         background-color: #15171c;
#                         color: #ffffff;  /* Text color changed to white */
#                         border: 1px solid #5371ff;
#                         font-size: 14px;
#                         border-radius: 5px;  /* Added border radius */
#                     }
#                     QLabel {
#                         color: #ffffff;  /* Text color changed to white */
#                         font-size: 16px;
#                     }
#                 """)
#         main_widget = QWidget()
#         self.setCentralWidget(main_widget)
#         main_layout = QVBoxLayout()
#         main_widget.setLayout(main_layout)

#         # Top Panel
#         top_panel = QHBoxLayout()
#         main_layout.addLayout(top_panel)
#         top_panel.addStretch()
#         top_panel.addWidget(QPushButton("Live Feed"))
#         top_panel.addWidget(QPushButton("Train Model", clicked=self.train_model))
#         top_panel.addStretch()



#         # Left Panel
#         # left_panel = QVBoxLayout()
#         # self.camera_list = QListWidget()
#         # left_panel.addWidget(QPushButton("Add Camera", clicked=self.open_add_camera_dialog))
#         # left_panel.addWidget(self.camera_list)
#         # grid_options = QComboBox()
#         # grid_options.addItems(["2X2", "4x4"])
#         # grid_options.currentTextChanged.connect(self.change_grid_view)
#         # left_panel.addWidget(QLabel("Grid View:"))
#         # left_panel.addWidget(grid_options)
#         left_panel = QVBoxLayout()
#         self.camera_list = QListWidget()

#         # Load and display cameras
#         self.load_cameras()

#         left_panel.addWidget(QPushButton("Add Camera", clicked=self.open_add_camera_dialog))
#         left_panel.addWidget(self.camera_list)

#         # Grid View Options
#         grid_options = QComboBox()
#         grid_options.addItems(["2X2", "4x4"])
#         grid_options.currentTextChanged.connect(self.change_grid_view)
#         left_panel.addWidget(QLabel("Grid View:"))
#         left_panel.addWidget(grid_options)
#         # Middle Section
#         middle_section = QHBoxLayout()
#         main_layout.addLayout(middle_section)
#         middle_section.addLayout(left_panel)

#         # Middle Grid (Video Feeds)
#         self.middle_panel = QGridLayout()
#         self.update_grid_view(2)
#         middle_section.addLayout(self.middle_panel, stretch=5)

#         # Right Panel
#         right_panel = QVBoxLayout()
#         # right_panel.addWidget(QPushButton("Load Camera"))
#         load_button = QPushButton("Load Camera")

#         load_button.clicked.connect(self.load_cameras)
#         right_panel.addWidget(load_button)

#         # right_panel.addWidget(QPushButton("Save Camera"))
#         self.activity_log = QTextEdit()
#         self.activity_log.setReadOnly(True)
#         self.activity_log.setPlaceholderText("Activity Log")
#         right_panel.addWidget(self.activity_log)
#         middle_section.addLayout(right_panel, stretch=2)
#    # Bottom options (Add Known Person, User, License Validation, Exit)
#         bottom_panel = QHBoxLayout()
#         bottom_panel.addWidget(QPushButton("Add Known Person"))
#         # bottom_panel.addWidget(QPushButton("User"))
#          # Modify the "User" button to open a dialog for user data
#         user_button = QPushButton("User")
#         user_button.clicked.connect(self.show_user_data)
#         bottom_panel.addWidget(user_button)

#         # Add a new button for daily logs
#         logs_button = QPushButton("Daily Logs")
#         logs_button.clicked.connect(self.show_daily_logs)
#         bottom_panel.addWidget(logs_button)

#         # bottom_panel.addWidget(QPushButton("License Validation"))
#         # bottom_panel.addWidget(QPushButton("Exit"))
#         self.exit_button = QPushButton("Exit")
#         self.exit_button.clicked.connect(self.exit_app)
#         bottom_panel.addWidget(self.exit_button)
#         main_layout.addLayout(bottom_panel)



#     def exit_app(self):
#         """Stops all camera threads and closes the application."""
#         self.close()

        
#     def closeEvent(self, event):
#         """Stops all camera threads when the application is closed."""
#         for thread in self.camera_threads.values():
#             thread.stop()
#         event.accept()

#     def open_add_camera_dialog(self):
#         """ Opens the Add Camera Form Dialog """
#         dialog = AddCameraDialog()
#         dialog.exec_()  # This opens the form window


#     def load_cameras(self):
#             """Load camera names and IP addresses from camera.csv into QListWidget."""
#             csv_file = "data/camera.csv"

#             if not os.path.exists(csv_file):
#                 QMessageBox.warning(None, "File Not Found", "No camera data found.")
#                 return

#             # Read CSV
#             df = pd.read_csv(csv_file)

#             # Clear the existing list
#             self.camera_list.clear()

#             # Populate the list
#             for _, row in df.iterrows():
#                 camera_name = row["Camera Name"]
#                 ip_address = row["IP Address"] if pd.notna(row["IP Address"]) else "No IP"
#                 self.camera_list.addItem(f"{camera_name} ({ip_address})")

                
#     def change_grid_view(self, text):
#         size = 2 if text == "2X2" else 4
#         self.update_grid_view(size)

#     def update_grid_view(self, size):
#         while self.middle_panel.count():
#             item = self.middle_panel.takeAt(0)
#             if item.widget():
#                 item.widget().deleteLater()
        
#         self.current_grid_size = size
#         camera_ips = [self.camera_list.item(i).text() for i in range(self.camera_list.count())]
        
#         for i in range(size):
#             for j in range(size):
#                 idx = i * size + j
#                 if idx < len(camera_ips):
#                     cam_feed = CameraStream(camera_ips[idx])
#                     self.middle_panel.addWidget(cam_feed, i, j)
#                 else:
#                     placeholder = QLabel("No Feed")
#                     placeholder.setAlignment(Qt.AlignCenter)
#                     placeholder.setStyleSheet("background-color: black; color: white;")
#                     self.middle_panel.addWidget(placeholder, i, j)

#     def train_model(self):
#             data_path = "data/training_images"
#             model_path = "model/trained_model.yml"

#             images, labels = [], []
#             label_map = {}

#             # Check if training directory exists
#             if not os.path.exists(data_path):
#                 QMessageBox.critical(self, "Error", "Training images folder not found! Please add images.")
#                 return

#             # Check if the training folder has subdirectories (persons)
#             person_folders = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
#             if not person_folders:
#                 QMessageBox.critical(self, "Error", "No person folders found in training data! Please add images.")
#                 return

#             for label, person in enumerate(person_folders):
#                 person_path = os.path.join(data_path, person)
#                 label_map[label] = person

#                 img_files = [f for f in os.listdir(person_path) if f.endswith(('.jpg', '.png', '.jpeg'))]

#                 if not img_files:
#                     QMessageBox.warning(self, "Warning", f"No images found for '{person}'. Skipping...")
#                     continue  # Skip this person

#                 for img_name in img_files:
#                     img_path = os.path.join(person_path, img_name)
#                     img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

#                     if img is None:
#                         QMessageBox.warning(self, "Warning", f"Could not read image: {img_name}. Skipping...")
#                         continue  # Skip unreadable images

#                     images.append(img)
#                     labels.append(label)

#             # Train the model if there are valid images
#             if images:
#                 recognizer = cv2.face.LBPHFaceRecognizer_create()
#                 recognizer.train(images, np.array(labels))
#                 os.makedirs(os.path.dirname(model_path), exist_ok=True)
#                 recognizer.write(model_path)
#                 self.activity_log.append("✅ Model trained successfully!")
#             else:
#                 QMessageBox.critical(self, "Error", "No valid images found for training!")
#                 self.activity_log.append("❌ No valid images found for training.")

#     def show_user_data(self):
#         """Display user data from user_data_store.csv in a table format."""
#         dialog = QDialog(self)
#         dialog.setWindowTitle("User Data")
#         dialog.setGeometry(100, 100, 800, 400)
#         dialog.setStyleSheet("background-color: #15171c; color: #ffffff;")

#         layout = QVBoxLayout()
#         dialog.setLayout(layout)

#         table = QTableWidget()
#         table.setStyleSheet("""
#             QTableWidget {
#                 background-color: #15171c;
#                 color: #ffffff;
#                 gridline-color: #5371ff;
#             }
#             QHeaderView::section {
#                 background-color: #5371ff;
#                 color: #ffffff;
#                 padding: 5px;
#                 border: none;
#             }
#         """)
#         layout.addWidget(table)

#         csv_file = "data/user_data_store.csv"
#         if not os.path.exists(csv_file):
#             QMessageBox.warning(self, "File Not Found", "User data file not found.")
#             return

#         try:
#             df = pd.read_csv(csv_file)
#             table.setRowCount(len(df))
#             table.setColumnCount(len(df.columns))
#             table.setHorizontalHeaderLabels(df.columns)

#             for i, row in df.iterrows():
#                 for j, value in enumerate(row):
#                     item = QTableWidgetItem(str(value))
#                     item.setTextAlignment(Qt.AlignCenter)
#                     table.setItem(i, j, item)

#             table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#             table.verticalHeader().setVisible(False)
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Failed to read user data: {str(e)}")

#         dialog.exec_()

#     def show_daily_logs(self):
#         """Display daily logs from logs.csv in a table format."""
#         dialog = QDialog(self)
#         dialog.setWindowTitle("Daily Logs")
#         dialog.setGeometry(100, 100, 800, 400)
#         dialog.setStyleSheet("background-color: #15171c; color: #ffffff;")

#         layout = QVBoxLayout()
#         dialog.setLayout(layout)

#         table = QTableWidget()
#         table.setStyleSheet("""
#             QTableWidget {
#                 background-color: #15171c;
#                 color: #ffffff;
#                 gridline-color: #5371ff;
#             }
#             QHeaderView::section {
#                 background-color: #5371ff;
#                 color: #ffffff;
#                 padding: 5px;
#                 border: none;
#             }
#         """)
#         layout.addWidget(table)

#         csv_file = "data/logs.csv"
#         if not os.path.exists(csv_file):
#             QMessageBox.warning(self, "File Not Found", "Logs file not found.")
#             return

#         try:
#             df = pd.read_csv(csv_file)
#             table.setRowCount(len(df))
#             table.setColumnCount(len(df.columns))
#             table.setHorizontalHeaderLabels(df.columns)

#             for i, row in df.iterrows():
#                 for j, value in enumerate(row):
#                     item = QTableWidgetItem(str(value))
#                     item.setTextAlignment(Qt.AlignCenter)
#                     table.setItem(i, j, item)

#             table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#             table.verticalHeader().setVisible(False)
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Failed to read logs: {str(e)}")

#         dialog.exec_()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     dashboard = UserDashboard()
#     dashboard.show()
#     sys.exit(app.exec_())