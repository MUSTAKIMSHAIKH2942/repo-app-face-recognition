import sys
import cv2
import os
import numpy as np
import csv
import logging
import socket
import threading
import ipaddress
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QGridLayout, QTextEdit, QComboBox, QMessageBox,
    QDialog, QTableWidgetItem, QTableWidget, QHeaderView, QLineEdit, QInputDialog
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
import pandas as pd
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
MODEL_PATH = "models/trained_model.yml"
DATA_PATH = "data/training_images"
LOGS_FILE = "data/logs.csv"
CAMERA_CSV = "data/camera.csv"
NVR_PORTS = [8000, 34567, 37777, 554]  # Common NVR/DVR ports
MAX_THREADS = 50  # Limit concurrent scanning threads
LOCAL_NETWORKS = ["192.168.1.0/24", "192.168.0.0/24", "10.0.0.0/24"]  # Common local networks
DEFAULT_WINDOW_SIZE = (1280, 720)  # Standard HD resolution
MIN_CAMERA_SIZE = (320, 240)  # Minimum camera display size

# Face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

if os.path.exists(MODEL_PATH):
    recognizer.read(MODEL_PATH)
else:
    recognizer = None

class CameraDiscoveryWorker(QObject):
    camera_found = pyqtSignal(dict)
    discovery_complete = pyqtSignal()
    progress_update = pyqtSignal(int, int)  # current, total
    
    def __init__(self):
        super().__init__()
        self.stop_flag = False
    
    def discover_cameras(self):
        """Scan network for NVR/DVR devices"""
        try:
            total_ips = sum(len(list(ipaddress.ip_network(net).hosts())) for net in LOCAL_NETWORKS)
            scanned_ips = 0
            
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                futures = []
                for network in LOCAL_NETWORKS:
                    if self.stop_flag:
                        break
                    
                    for ip in ipaddress.ip_network(network).hosts():
                        if self.stop_flag:
                            break
                        futures.append(executor.submit(self.scan_device, str(ip)))
                
                for future in futures:
                    if self.stop_flag:
                        break
                    result = future.result()
                    scanned_ips += 1
                    self.progress_update.emit(scanned_ips, total_ips)
                    if result:
                        self.camera_found.emit(result)
        
        except Exception as e:
            logging.error(f"Discovery error: {str(e)}")
        finally:
            self.discovery_complete.emit()
    
    def scan_device(self, ip):
        """Check if device is a camera"""
        try:
            for port in NVR_PORTS:
                if self.stop_flag:
                    return None
                if self.check_port_fast(ip, port):
                    brand = self.identify_brand(port)
                    return {'ip': ip, 'port': port, 'brand': brand, 'status': 'Discovered'}
            return None
        except:
            return None
    
    def check_port_fast(self, ip, port, timeout=0.3):
        """Quick port check with timeout"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex((ip, port)) == 0
    
    def identify_brand(self, port):
        """Identify camera brand by port"""
        port_brands = {
            8000: 'Hikvision',
            34567: 'Dahua',
            37777: 'Dahua NVR',
            554: 'Generic RTSP'
        }
        return port_brands.get(port, 'Unknown')
    
    def stop(self):
        self.stop_flag = True

class CameraStream(QLabel):
    def __init__(self, camera_info):
        super().__init__()
        self.camera_info = camera_info
        self.ip = camera_info.get('ip', '')
        self.rtsp_url = self.generate_rtsp_url()
        self.is_connected = False
        self.frame_counter = 0
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(*MIN_CAMERA_SIZE)
        self.setText("Initializing stream...")
        
        self.connect_camera()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(60)  # ~30 FPS
    
    def generate_rtsp_url(self):
        """Generate proper RTSP URL based on camera info"""
        ip = self.camera_info.get('ip', '')
        port = self.camera_info.get('port', 554)
        user = self.camera_info.get('username', 'admin')
        password = self.camera_info.get('password', '')
        brand = self.camera_info.get('brand', 'Generic')
        
        if brand == 'Hikvision':
            return f"rtsp://{user}:{password}@{ip}:{port}/Streaming/Channels/1"
        elif brand == 'Dahua':
            return f"rtsp://{user}:{password}@{ip}:{port}/cam/realmonitor?channel=1&subtype=0"
        return f"rtsp://{user}:{password}@{ip}:{port}/stream1"
    
    def connect_camera(self):
        """Establish camera connection with optimized settings"""
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            if not self.cap.isOpened():
                raise ConnectionError("Failed to open stream")
            
            # Optimize video capture settings
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            
            self.is_connected = True
            self.setText("Connected")
        except Exception as e:
            self.is_connected = False
            self.setText(f"Connection Error\n{str(e)}")
            logging.error(f"Connection error: {str(e)}")
    
    def update_frame(self):
        if not self.is_connected:
            return
            
        try:
            ret, frame = self.cap.read()
            if not ret:
                self.reconnect()
                return
                
            self.frame_counter += 1
            if self.frame_counter % 2 == 0:  # Process every other frame
                frame = self.process_frame(frame)
            self.display_frame(frame)
        except Exception as e:
            logging.error(f"Frame update error: {str(e)}")
            self.reconnect()
    
    def process_frame(self, frame):
        """Perform face detection on frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                if recognizer:
                    label, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                    if confidence < 80:
                        cv2.putText(frame, f"ID:{label}", (x, y-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            return frame
        except:
            return frame
    
    def reconnect(self):
        """Attempt to reconnect to camera"""
        self.is_connected = False
        self.setText("Reconnecting...")
        threading.Thread(target=self.connect_camera, daemon=True).start()
    
    def display_frame(self, frame):
        """Display frame in the QLabel"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(qimg).scaled(
                self.width(), self.height(), Qt.KeepAspectRatio))
        except:
            pass
    
    def closeEvent(self, event):
        """Clean up resources"""
        try:
            if hasattr(self, 'cap'):
                self.cap.release()
            self.timer.stop()
        except:
            pass
        event.accept()

class AddCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Camera")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        self.fields = {
            "Camera Name": QLineEdit(),
            "IP Address": QLineEdit(),
            "Port": QLineEdit("554"),
            "Username": QLineEdit("admin"),
            "Password": QLineEdit(),
            "Brand": QComboBox(),
            "Channel": QLineEdit("1")
        }
        
        self.fields["Brand"].addItems(["Generic", "Hikvision", "Dahua", "Axis"])
        
        for label, widget in self.fields.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{label}:"))
            row.addWidget(widget)
            layout.addLayout(row)
        
        button_box = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        button_box.addWidget(btn_ok)
        button_box.addWidget(btn_cancel)
        
        layout.addLayout(button_box)
        self.setLayout(layout)
    
    def get_camera_details(self):
        return {
            'Camera Name': self.fields["Camera Name"].text(),
            'IP Address': self.fields["IP Address"].text(),
            'Port': self.fields["Port"].text(),
            'Username': self.fields["Username"].text(),
            'Password': self.fields["Password"].text(),
            'Brand': self.fields["Brand"].currentText(),
            'Channel': self.fields["Channel"].text(),
            'RTSP URL': ""
        }

class AddPersonForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Person to Database")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        self.name_field = QLineEdit()
        self.id_field = QLineEdit()
        
        layout.addWidget(QLabel("Person Name:"))
        layout.addWidget(self.name_field)
        layout.addWidget(QLabel("Person ID:"))
        layout.addWidget(self.id_field)
        
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        
        layout.addLayout(btn_box)
        self.setLayout(layout)
    
    def get_person_data(self):
        return {
            'name': self.name_field.text(),
            'id': self.id_field.text()
        }

class UserDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NVR/DVR Surveillance System")
        self.resize(*DEFAULT_WINDOW_SIZE)
        self.cameras = []
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the user interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Top control panel
        top_panel = QHBoxLayout()
        top_panel.setSpacing(10)
        
        self.btn_discover = QPushButton("Discover Cameras")
        self.btn_discover.setFixedHeight(40)
        self.btn_discover.clicked.connect(self.discover_cameras)
        top_panel.addWidget(self.btn_discover)
        
        self.btn_train = QPushButton("Train Model")
        self.btn_train.setFixedHeight(40)
        self.btn_train.clicked.connect(self.train_model)
        top_panel.addWidget(self.btn_train)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setFixedHeight(40)
        self.btn_refresh.clicked.connect(self.load_cameras)
        top_panel.addWidget(self.btn_refresh)
        
        top_panel.addStretch()
        main_layout.addLayout(top_panel)
        
        # Center content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        # Left sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        
        self.camera_list = QListWidget()
        self.camera_list.setFixedWidth(250)
        self.load_cameras()
        
        sidebar.addWidget(QLabel("Connected Devices:"))
        sidebar.addWidget(self.camera_list)
        
        self.btn_add_camera = QPushButton("Add Camera Manually")
        self.btn_add_camera.clicked.connect(self.open_add_camera_dialog)
        sidebar.addWidget(self.btn_add_camera)
        
        sidebar.addWidget(QLabel("Display Layout:"))
        self.grid_combo = QComboBox()
        self.grid_combo.addItems(["1x1", "2x2", "3x3"])
        self.grid_combo.currentTextChanged.connect(self.change_grid_view)
        sidebar.addWidget(self.grid_combo)
        
        sidebar.addStretch()
        content_layout.addLayout(sidebar)
        
        # Video grid area
        self.video_grid = QGridLayout()
        self.video_grid.setSpacing(5)
        self.update_grid_view(2)  # Default 2x2 grid
        
        content_layout.addLayout(self.video_grid, stretch=1)
        
        # Right log panel
        log_panel = QVBoxLayout()
        log_panel.setSpacing(10)
        
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setPlaceholderText("System activity log...")
        self.activity_log.setFixedWidth(300)
        
        log_panel.addWidget(QLabel("Activity Log:"))
        log_panel.addWidget(self.activity_log, stretch=1)
        
        self.status_label = QLabel("Ready")
        log_panel.addWidget(self.status_label)
        
        content_layout.addLayout(log_panel)
        main_layout.addLayout(content_layout, stretch=1)
        
        # Bottom panel
        bottom_panel = QHBoxLayout()
        bottom_panel.setSpacing(10)
        
        self.btn_add_person = QPushButton("Add Person")
        self.btn_add_person.setFixedHeight(35)
        self.btn_add_person.clicked.connect(self.open_add_person_form)
        bottom_panel.addWidget(self.btn_add_person)
        
        self.btn_users = QPushButton("User Management")
        self.btn_users.setFixedHeight(35)
        self.btn_users.clicked.connect(self.show_user_data)
        bottom_panel.addWidget(self.btn_users)
        
        self.btn_logs = QPushButton("View Logs")
        self.btn_logs.setFixedHeight(35)
        self.btn_logs.clicked.connect(self.show_daily_logs)
        bottom_panel.addWidget(self.btn_logs)
        
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setFixedHeight(35)
        self.btn_exit.clicked.connect(self.close)
        bottom_panel.addWidget(self.btn_exit)
        
        bottom_panel.addStretch()
        main_layout.addLayout(bottom_panel)
    
    def discover_cameras(self):
        """Start camera discovery process"""
        if hasattr(self, 'discovery_thread') and self.discovery_thread.isRunning():
            QMessageBox.information(self, "Scan Running", "Discovery already in progress.")
            return
            
        self.btn_discover.setEnabled(False)
        self.status_label.setText("Scanning network...")
        self.activity_log.append("🚀 Starting NVR/DVR discovery...")
        
        self.discovery_worker = CameraDiscoveryWorker()
        self.discovery_thread = threading.Thread(target=self.discovery_worker.discover_cameras)
        
        self.discovery_worker.camera_found.connect(self.handle_nvr_device)
        self.discovery_worker.progress_update.connect(self.update_scan_progress)
        self.discovery_worker.discovery_complete.connect(self.discovery_finished)
        
        self.discovery_thread.start()
    
    def handle_nvr_device(self, device_info):
        """Handle discovered NVR/DVR device"""
        ip = device_info['ip']
        
        # Skip if already exists
        if os.path.exists(CAMERA_CSV):
            df = pd.read_csv(CAMERA_CSV)
            if not df[df['IP Address'] == ip].empty:
                self.activity_log.append(f"ℹ️ Device exists: {ip}")
                return
        
        # Prompt for credentials
        name = f"{device_info['brand']} NVR ({ip})"
        user, ok1 = QInputDialog.getText(
            self, "NVR Credentials", 
            f"Enter username for {ip}:", 
            QLineEdit.Normal, 
            "admin"
        )
        
        if not ok1:
            return
            
        password, ok2 = QInputDialog.getText(
            self, "NVR Credentials",
            f"Enter password for {ip}:",
            QLineEdit.Password,
            "12345"
        )
        
        if not ok2:
            return
            
        # Save camera configuration
        camera_data = {
            'Camera Name': name,
            'IP Address': ip,
            'Port': device_info['port'],
            'Username': user,
            'Password': password,
            'Brand': device_info['brand'],
            'Channel': 1,
            'RTSP URL': f"rtsp://{user}:{password}@{ip}:{device_info['port']}/main"
        }
        
        self.save_camera(camera_data)
        self.activity_log.append(f"✅ Added NVR: {name}")
    
    def update_scan_progress(self, current, total):
        """Update scan progress in status bar"""
        percent = int((current / total) * 100)
        self.status_label.setText(f"Scanning... {percent}% ({current}/{total} IPs)")
    
    def discovery_finished(self):
        """Clean up after discovery completes"""
        self.btn_discover.setEnabled(True)
        self.status_label.setText("Scan completed")
        self.activity_log.append("✅ NVR/DVR discovery finished")
        
        if hasattr(self, 'discovery_thread'):
            self.discovery_thread.join()
            self.discovery_thread = None
    
    def save_camera(self, camera_data):
        """Save camera configuration to CSV"""
        try:
            df = pd.DataFrame([camera_data])
            if os.path.exists(CAMERA_CSV):
                existing_df = pd.read_csv(CAMERA_CSV)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            df.to_csv(CAMERA_CSV, index=False)
            self.load_cameras()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save camera: {str(e)}")
    
    def load_cameras(self):
        """Load cameras from CSV file"""
        try:
            if not os.path.exists(CAMERA_CSV):
                QMessageBox.warning(self, "File Not Found", "No camera data found. Please add cameras first.")
                return

            df = pd.read_csv(CAMERA_CSV)
            self.camera_list.clear()
            self.cameras = []

            for _, row in df.iterrows():
                camera_info = {
                    'name': row.get("Camera Name", "Unnamed Camera"),
                    'ip': row["IP Address"],
                    'port': row.get("Port", 554),
                    'username': row.get("Username", "admin"),
                    'password': row.get("Password", ""),
                    'brand': row.get("Brand", "Generic"),
                    'channel': row.get("Channel", 1),
                    'rtsp_url': row.get("RTSP URL", "")
                }
                self.cameras.append(camera_info)
                self.camera_list.addItem(f"{camera_info['name']} ({camera_info['ip']})")
            
            self.update_grid_view(int(self.grid_combo.currentText()[0]))  # Update grid with current layout
        except Exception as e:
            logging.error(f"Error loading cameras: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load cameras: {str(e)}")
    
    def open_add_camera_dialog(self):
        """Open dialog to add camera manually"""
        dialog = AddCameraDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            camera_info = dialog.get_camera_details()
            self.save_camera(camera_info)
            self.activity_log.append(f"✅ Added camera: {camera_info['Camera Name']}")
    
    def change_grid_view(self, text):
        """Change the grid layout of camera views"""
        size = int(text[0])  # Extract number from "1x1", "2x2", etc.
        self.update_grid_view(size)
    
    def update_grid_view(self, size):
        """Update the video grid layout"""
        try:
            # Clear existing widgets
            while self.video_grid.count():
                item = self.video_grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Add camera feeds to grid
            for i in range(size):
                for j in range(size):
                    idx = i * size + j
                    if idx < len(self.cameras):
                        try:
                            cam_feed = CameraStream(self.cameras[idx])
                            self.video_grid.addWidget(cam_feed, i, j)
                        except Exception as e:
                            logging.error(f"Error creating stream: {str(e)}")
                            placeholder = QLabel(f"Error: {str(e)}")
                            placeholder.setAlignment(Qt.AlignCenter)
                            placeholder.setStyleSheet("color: red;")
                            self.video_grid.addWidget(placeholder, i, j)
                    else:
                        placeholder = QLabel("No Feed")
                        placeholder.setAlignment(Qt.AlignCenter)
                        placeholder.setStyleSheet("background-color: black; color: white;")
                        self.video_grid.addWidget(placeholder, i, j)
        except Exception as e:
            logging.error(f"Error updating grid: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to update grid: {str(e)}")
    
    def train_model(self):
        """Train the face recognition model"""
        try:
            images, labels = [], []
            label_map = {}

            if not os.path.exists(DATA_PATH):
                QMessageBox.critical(self, "Error", "Training images folder not found!")
                return

            person_folders = [d for d in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, d))]
            if not person_folders:
                QMessageBox.critical(self, "Error", "No person folders found!")
                return

            for label, person in enumerate(person_folders):
                person_path = os.path.join(DATA_PATH, person)
                label_map[label] = person

                for img_name in [f for f in os.listdir(person_path) if f.endswith(('.jpg', '.png', '.jpeg'))]:
                    img_path = os.path.join(person_path, img_name)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        images.append(img)
                        labels.append(label)

            if images:
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                recognizer.train(images, np.array(labels))
                os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
                recognizer.write(MODEL_PATH)
                self.activity_log.append("✅ Model trained successfully!")
                QMessageBox.information(self, "Success", "Model trained successfully!")
            else:
                QMessageBox.critical(self, "Error", "No valid images found for training!")
        except Exception as e:
            logging.error(f"Training error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Training failed: {str(e)}")
    
    def open_add_person_form(self):
        """Open dialog to add new person to database"""
        dialog = AddPersonForm(self)
        if dialog.exec_() == QDialog.Accepted:
            person_data = dialog.get_person_data()
            self.activity_log.append(f"Added person: {person_data['name']} (ID: {person_data['id']})")
            # Here you would add code to actually save the person to your database
    
    def show_user_data(self):
        """Show user data in a table view"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("User Data")
            dialog.resize(800, 600)
            
            table = QTableWidget()
            layout = QVBoxLayout()
            layout.addWidget(table)
            dialog.setLayout(layout)
            
            csv_file = "data/user_data_store.csv"
            if not os.path.exists(csv_file):
                QMessageBox.warning(self, "File Not Found", "User data file not found!")
                return
            
            df = pd.read_csv(csv_file)
            table.setRowCount(len(df))
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels(df.columns)
            
            for i, row in df.iterrows():
                for j, value in enumerate(row):
                    table.setItem(i, j, QTableWidgetItem(str(value)))
            
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            dialog.exec_()
        except Exception as e:
            logging.error(f"Error showing user data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to show user data: {str(e)}")
    
    def show_daily_logs(self):
        """Show system logs in a table view"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("System Logs")
            dialog.resize(800, 600)
            
            table = QTableWidget()
            layout = QVBoxLayout()
            layout.addWidget(table)
            dialog.setLayout(layout)
            
            csv_file = "data/logs.csv"
            if not os.path.exists(csv_file):
                QMessageBox.warning(self, "File Not Found", "Logs file not found!")
                return
            
            df = pd.read_csv(csv_file)
            table.setRowCount(len(df))
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels(df.columns)
            
            for i, row in df.iterrows():
                for j, value in enumerate(row):
                    table.setItem(i, j, QTableWidgetItem(str(value)))
            
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            dialog.exec_()
        except Exception as e:
            logging.error(f"Error showing logs: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to show logs: {str(e)}")
    
    def closeEvent(self, event):
        """Clean up resources when closing"""
        try:
            # Stop all camera streams
            for i in range(self.video_grid.count()):
                widget = self.video_grid.itemAt(i).widget()
                if isinstance(widget, CameraStream):
                    widget.close()
        except Exception as e:
            logging.error(f"Error during close: {str(e)}")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern, consistent style
    
    # Set application font for consistency
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    window = UserDashboard()
    window.show()
    sys.exit(app.exec_())