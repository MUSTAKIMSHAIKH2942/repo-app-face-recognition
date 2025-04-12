from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout, QCheckBox, QLineEdit
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPropertyAnimation, QRect
import csv
from utils.constants import MAX_CAMERAS, MAX_USERS
from utils.file_utils import load_cameras, save_cameras, load_users, save_limits
from add_user_screen import AddUserScreen
from view_unknown_persons import UnknownPersonsViewer
from mount import count_users

class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")
        self.init_ui()
        self.load_addons_state()  # Load add-ons state from CSV

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header = QLabel("Admin Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #1db954;")
        layout.addWidget(header)
         # Log Out Button
        self.logout_button = QPushButton("Log Out")
        self.logout_button.setStyleSheet("background-color: #f39c12; padding: 5px 10px; font-size: 14px; border-radius: 5px;")
        self.logout_button.clicked.connect(self.logout)
 # Header Layout
        header_layout = QHBoxLayout()
        # Exit Button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: #ff4c4c; padding: 5px 10px; font-size: 14px; border-radius: 5px;")
        self.exit_button.clicked.connect(self.close)


        # Adding elements to header layout
        header_layout.addWidget(header)
        header_layout.addStretch()  # Pushes buttons to the right
        header_layout.addWidget(self.logout_button)
        header_layout.addWidget(self.exit_button)
        
        # Buttons Layout
        layout.addLayout(header_layout)
        button_layout = QHBoxLayout()

        self.add_user_button = QPushButton("Add New User")
        self.add_user_button.setIcon(QIcon("icons/add_user.png"))
        # self.add_user_button.setStyleSheet("background-color: #1db954; padding: 10px; font-size: 14px; border-radius: 5px;")
        self.add_user_button.setStyleSheet(
            "background-color: #1db954; padding: 10px; font-size: 14px; border-radius: 5px;"
        )
        self.add_user_button.clicked.connect(self.add_user)
        button_layout.addWidget(self.add_user_button)

        layout.addLayout(button_layout)

        self.user_count_label = QLabel(f"Users: {count_users()}/{MAX_USERS}")
        self.user_count_label.setStyleSheet("font-size: 16px; margin-top: 20px;")
        layout.addWidget(self.user_count_label)

        self.camera_count_label = QLabel(f"Cameras: {len(load_cameras())}/{MAX_CAMERAS}")
        self.camera_count_label.setStyleSheet("font-size: 16px; margin-top: 10px;")
        layout.addWidget(self.camera_count_label)

        # Add-ons Toggle Section
        self.addons_label = QLabel("Add-ons Settings")
        self.addons_label.setStyleSheet("font-size: 18px; margin-top: 20px; font-weight: bold;")
        layout.addWidget(self.addons_label)

        # Add-ons Toggles
        self.addons = {
            "Unknown Person Tracking": QCheckBox("Enable Unknown Person Tracking"),
            "Facial Recognition": QCheckBox("Enable Facial Recognition"),
            "Motion Detection": QCheckBox("Enable Motion Detection")
        }

        for addon_name, toggle in self.addons.items():
            toggle.setStyleSheet("font-size: 16px;")
            toggle.stateChanged.connect(lambda state, name=addon_name: self.save_addons_state(name, state))
            layout.addWidget(toggle)

        # View Unknown Persons Button
        self.view_unknowns_button = QPushButton("View Unknown Person Data")
        self.view_unknowns_button.setStyleSheet("background-color: #1db954; padding: 10px; font-size: 16px; border-radius: 5px;")
        self.view_unknowns_button.clicked.connect(self.view_unknown_persons)
        layout.addWidget(self.view_unknowns_button)

        # Limits Section
        self.limits_label = QLabel("Set User & Camera Limits")
        self.limits_label.setStyleSheet("font-size: 18px; margin-top: 20px; font-weight: bold;")
        layout.addWidget(self.limits_label)

        limits_layout = QHBoxLayout()
        self.user_limit_input = QLineEdit()
        self.user_limit_input.setPlaceholderText("Max Users")
        self.user_limit_input.setStyleSheet("padding: 5px; font-size: 14px;")
        limits_layout.addWidget(self.user_limit_input)

        self.camera_limit_input = QLineEdit()
        self.camera_limit_input.setPlaceholderText("Max Cameras")
        self.camera_limit_input.setStyleSheet("padding: 5px; font-size: 14px;")
        limits_layout.addWidget(self.camera_limit_input)

        self.update_limits_button = QPushButton("Update Limits")
        self.update_limits_button.setStyleSheet("background-color: #1db954; padding: 10px; border-radius: 5px;")
        self.update_limits_button.clicked.connect(self.update_limits)
        limits_layout.addWidget(self.update_limits_button)

        layout.addLayout(limits_layout)

        self.setLayout(layout)

    def animate_form_open(self, form):
        form.setGeometry(QRect(300, 200, 0, 0))
        form.show()
        animation = QPropertyAnimation(form, b"geometry")
        animation.setDuration(300)
        animation.setStartValue(QRect(300, 200, 0, 0))
        animation.setEndValue(QRect(300, 200, 400, 300))
        animation.start()

    def update_user_count_label(self):
        """Update the user count label dynamically."""
        self.user_count_label.setText(f"Users: {count_users()}/{MAX_USERS}")

    def add_user(self):
        print("Button clicked! Opening AddUserScreen...")  # Debugging print statement
        
        if hasattr(self, "add_user_screen") and self.add_user_screen.isVisible():
            print("AddUserScreen already open.")  # Prevent multiple windows
            return
        
        self.add_user_screen = AddUserScreen(self)
        self.add_user_screen.show()

        # Debugging: Check if it's visible
        if self.add_user_screen.isVisible():
            print("AddUserScreen is visible.")  # ✅ Should print if window opens
        else:
            print("AddUserScreen failed to open.")  # ❌ If you see this, something is wrong

    def view_unknown_persons(self):
        self.viewer = UnknownPersonsViewer()
        self.viewer.show()

    def update_limits(self):
        try:
            new_max_users = int(self.user_limit_input.text())
            new_max_cameras = int(self.camera_limit_input.text())

            if new_max_users < 1 or new_max_cameras < 1:
                QMessageBox.warning(self, "Invalid Input", "Limits must be greater than 0.")
                return

            save_limits(new_max_users, new_max_cameras)

            # Update UI labels to reflect new limits
            self.user_count_label.setText(f"Users: {len(load_users())}/{new_max_users}")
            self.camera_count_label.setText(f"Cameras: {len(load_cameras())}/{new_max_cameras}")

            QMessageBox.information(self, "Success", "Limits updated successfully.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for limits.")

    def save_addons_state(self, addon_name, state):
        # Save the state of the add-on to a CSV file
        with open("data/addons_state.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            for name, toggle in self.addons.items():
                writer.writerow([name, toggle.isChecked()])

    def load_addons_state(self):
        # Load the state of the add-ons from the CSV file
        try:
            with open("data/addons_state.csv", mode="r") as file:
                reader = csv.reader(file)
                for row in reader:
                    addon_name, state = row
                    if addon_name in self.addons:
                        self.addons[addon_name].setChecked(state == "True")
        except FileNotFoundError:
            # If the file doesn't exist, initialize with default values
            self.save_addons_state("Unknown Person Tracking", False)
            self.save_addons_state("Facial Recognition", False)
            self.save_addons_state("Motion Detection", False)

    def logout(self):
        """Redirect to login page."""
        from login import LoginPage  # Import here to avoid circular dependency
        self.login_screen = LoginPage()
        self.login_screen.show()
        self.close()