# import sys
# import json
# import os
# import pandas as pd
# from PyQt5.QtWidgets import (
#     QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,QComboBox,QSpinBox, QHBoxLayout
# )
# # RTSP URL patterns for common camera brands
# RTSP_PATTERNS = {
#     'Generic': 'rtsp://{username}:{password}@{ip}:{port}/live',
#     'Hikvision': 'rtsp://{username}:{password}@{ip}:{port}/ISAPI/Streaming/Channels/{channel}',
#     'Dahua': 'rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0',
#     'Axis': 'rtsp://{username}:{password}@{ip}:{port}/axis-media/media.amp',
#     'TP-Link': 'rtsp://{username}:{password}@{ip}:{port}/stream1',
#     'Reolink': 'rtsp://{username}:{password}@{ip}:554/h264Preview_01_main'
# }

# DEFAULT_PORTS = {
#     'Generic': 554,
#     'Hikvision': 554,
#     'Dahua': 554,
#     'Axis': 554,
#     'TP-Link': 554,
#     'Reolink': 554
# }

# class AddCameraDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Add Camera")
#         self.setFixedSize(400, 400)
        
#         layout = QVBoxLayout()
        
#         # Camera Type Selection
#         self.type_combo = QComboBox()
#         self.type_combo.addItems(["IP Camera", "DVR/NVR System"])
#         layout.addWidget(QLabel("Camera Type:"))
#         layout.addWidget(self.type_combo)
        
#         # Brand Selection
#         self.brand_combo = QComboBox()
#         self.brand_combo.addItems(RTSP_PATTERNS.keys())
#         layout.addWidget(QLabel("Brand:"))
#         layout.addWidget(self.brand_combo)
        
#         # Connection Details
#         self.ip_input = QLineEdit()
#         self.ip_input.setPlaceholderText("192.168.1.100")
#         layout.addWidget(QLabel("IP Address:"))
#         layout.addWidget(self.ip_input)
        
#         self.port_input = QLineEdit()
#         self.port_input.setPlaceholderText("554")
#         layout.addWidget(QLabel("Port:"))
#         layout.addWidget(self.port_input)
        
#         self.username_input = QLineEdit()
#         self.username_input.setPlaceholderText("admin")
#         layout.addWidget(QLabel("Username:"))
#         layout.addWidget(self.username_input)
        
#         self.password_input = QLineEdit()
#         self.password_input.setPlaceholderText("password")
#         self.password_input.setEchoMode(QLineEdit.Password)
#         layout.addWidget(QLabel("Password:"))
#         layout.addWidget(self.password_input)
        
#         # For DVR/NVR systems
#         self.channel_input = QSpinBox()
#         self.channel_input.setRange(1, 32)
#         self.channel_input.setValue(1)
#         self.channel_label = QLabel("Channel:")
#         layout.addWidget(self.channel_label)
#         layout.addWidget(self.channel_input)
        
#         # Camera Name
#         self.name_input = QLineEdit()
#         self.name_input.setPlaceholderText("Front Door Camera")
#         layout.addWidget(QLabel("Camera Name:"))
#         layout.addWidget(self.name_input)
        
#         # Network Scan Button
#         self.scan_button = QPushButton("Scan Network for Cameras")
#         self.scan_button.clicked.connect(self.scan_network)
#         layout.addWidget(self.scan_button)
        
#         # Buttons
#         button_layout = QHBoxLayout()
#         self.add_button = QPushButton("Add Camera")
#         self.add_button.clicked.connect(self.accept)
#         button_layout.addWidget(self.add_button)
        
#         cancel_button = QPushButton("Cancel")
#         cancel_button.clicked.connect(self.reject)
#         button_layout.addWidget(cancel_button)
        
#         layout.addLayout(button_layout)
#         self.setLayout(layout)
        
#         # Hide DVR-specific controls initially
#         self.toggle_dvr_controls(False)
#         self.type_combo.currentTextChanged.connect(lambda: self.toggle_dvr_controls(self.type_combo.currentText() == "DVR/NVR System"))
    
#     def toggle_dvr_controls(self, show):
#         self.channel_label.setVisible(show)
#         self.channel_input.setVisible(show)
    
#     def scan_network(self):
#         # This would implement network scanning in a real application
#         # For now, just demonstrate the concept
#         QMessageBox.information(self, "Network Scan", 
#                               "This would scan your network for cameras.\n\n"
#                               "In a full implementation, this would:\n"
#                               "1. Scan common IP ranges (192.168.1.*, 10.0.0.*)\n"
#                               "2. Check common ports (554, 80, 37777)\n"
#                               "3. Attempt to identify camera brands\n"
#                               "4. Return discovered cameras for selection")
    
#     def get_camera_details(self):
#         brand = self.brand_combo.currentText()
#         ip = self.ip_input.text()
#         port = self.port_input.text() or str(DEFAULT_PORTS.get(brand, 554))
#         username = self.username_input.text() or "admin"
#         password = self.password_input.text() or ""
#         channel = self.channel_input.value() if self.type_combo.currentText() == "DVR/NVR System" else 1
#         name = self.name_input.text() or f"{brand} Camera"
        
#         # Generate RTSP URL
#         rtsp_url = RTSP_PATTERNS[brand].format(
#             username=username,
#             password=password,
#             ip=ip,
#             port=port,
#             channel=channel
#         )
        
#         return {
#             'name': name,
#             'brand': brand,
#             'ip': ip,
#             'port': port,
#             'username': username,
#             'password': password,
#             'channel': channel if self.type_combo.currentText() == "DVR/NVR System" else None,
#             'rtsp_url': rtsp_url
#         }

# import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QSpinBox, QHBoxLayout, QDateTimeEdit
)
from PyQt5.QtCore import QDateTime

# RTSP URL patterns for supported camera brands
RTSP_PATTERNS = {
    'Generic': 'rtsp://{username}:{password}@{ip}:{port}/live',
    'Hikvision': 'rtsp://{username}:{password}@{ip}:{port}/ISAPI/Streaming/Channels/{channel}',
    'Dahua': 'rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0',
    'Axis': 'rtsp://{username}:{password}@{ip}:{port}/axis-media/media.amp',
    'TP-Link': 'rtsp://{username}:{password}@{ip}:{port}/stream1',
    'Reolink': 'rtsp://{username}:{password}@{ip}:554/h264Preview_01_main',
    'Amcrest': 'rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0',
    'Ezviz': 'rtsp://{username}:{password}@{ip}:{port}/h264_stream'
}

# Default RTSP port for each brand
DEFAULT_PORTS = {brand: 554 for brand in RTSP_PATTERNS.keys()}


class AddCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Camera")
        self.setFixedSize(500, 680)

        # --- StyleSheet ---
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                border-radius: 10px;
                color: #ffffff;
            }
            QLabel {
                font-weight: bold;
                font-size: 13px;
                margin-top: 8px;
                margin-bottom: 2px;
                color: #f0f0f0;
            }
            QLineEdit, QComboBox, QSpinBox, QDateTimeEdit {
                padding: 6px;
                font-size: 13px;
                border: 1px solid #444;
                border-radius: 6px;
                background-color: #1e1e1e;
                color: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateTimeEdit:focus {
                border: 1px solid #0078d7;
            }
            QPushButton {
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                color: white;
                background-color: #0078d7;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:disabled {
                background-color: #333;
                color: #777;
            }
        """)


        # --- Layout ---
        layout = QVBoxLayout()

        # Camera Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["IP Camera", "DVR/NVR System"])
        layout.addWidget(QLabel("Camera Type:"))
        layout.addWidget(self.type_combo)

        # Brand
        self.brand_combo = QComboBox()
        self.brand_combo.addItems(RTSP_PATTERNS.keys())
        layout.addWidget(QLabel("Brand:"))
        layout.addWidget(self.brand_combo)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Front Door Camera")
        layout.addWidget(QLabel("Camera Name:"))
        layout.addWidget(self.name_input)

        # IP Address
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.1.100")
        layout.addWidget(QLabel("IP Address:"))
        layout.addWidget(self.ip_input)

        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Building A - Floor 1")
        layout.addWidget(QLabel("Location:"))
        layout.addWidget(self.location_input)

        # Timestamp
        self.timestamp_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.timestamp_input.setDisplayFormat("dd-mm-yyyy HH:mm:ss")
        layout.addWidget(QLabel("Timestamp:"))
        layout.addWidget(self.timestamp_input)

        # Port
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("554")
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_input)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("admin")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        # Channel (Only for DVR)
        self.channel_input = QSpinBox()
        self.channel_input.setRange(1, 64)
        self.channel_input.setValue(1)
        self.channel_label = QLabel("Channel:")
        layout.addWidget(self.channel_label)
        layout.addWidget(self.channel_input)

        # Scan Button
        self.scan_button = QPushButton("Scan Network for Cameras")
        self.scan_button.clicked.connect(self.scan_network)
        layout.addWidget(self.scan_button)

        # Add/Cancel Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Camera")
        self.add_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Initial DVR control toggle
        self.toggle_dvr_controls(False)
        self.type_combo.currentTextChanged.connect(
            lambda: self.toggle_dvr_controls(self.type_combo.currentText() == "DVR/NVR System")
        )

    def toggle_dvr_controls(self, show):
        self.channel_label.setVisible(show)
        self.channel_input.setVisible(show)

    def scan_network(self):
        QMessageBox.information(self, "Network Scan",
            "This would scan your network for cameras.\n\n"
            "In a full implementation, this would:\n"
            "1. Scan IP ranges\n"
            "2. Identify cameras & brands\n"
            "3. Populate discovered cameras here.")

    def get_camera_details(self):
        brand = self.brand_combo.currentText()
        ip = self.ip_input.text()
        port = self.port_input.text() or str(DEFAULT_PORTS.get(brand, 554))
        username = self.username_input.text() or "admin"
        password = self.password_input.text()
        channel = self.channel_input.value() if self.type_combo.currentText() == "DVR/NVR System" else 1
        name = self.name_input.text() or f"{brand} Camera"
        location = self.location_input.text()
        timestamp = self.timestamp_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        rtsp_url = RTSP_PATTERNS[brand].format(
            username=username,
            password=password,
            ip=ip,
            port=port,
            channel=channel
        )

        return {
            'name': name,
            'brand': brand,
            'ip': ip,
            'port': port,
            'username': username,
            'password': password,
            'channel': channel if self.type_combo.currentText() == "DVR/NVR System" else None,
            'location': location,
            'timestamp': timestamp,
            'rtsp_url': rtsp_url
        }


# For testing this dialog independently
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     dialog = AddCameraDialog()
#     if dialog.exec_():
#         camera_data = dialog.get_camera_details()
#         print("Camera Added:\n", camera_data)
#     sys.exit(app.exec_())
