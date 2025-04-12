# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox, QHBoxLayout
# from PyQt5.QtGui import QIcon
# from utils.file_utils import load_users, save_users
# from utils.constants import MAX_USERS

# class AddUserScreen(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Add User")
#         self.setGeometry(300, 200, 400, 320)
#         self.setStyleSheet("background-color: black; color: white; font-size: 14px;")
#         self.parent = parent
#         self.init_ui()

#     def init_ui(self):
#         layout = QVBoxLayout()

#         # Username input
#         self.username_input = QLineEdit(self)
#         self.username_input.setPlaceholderText("Enter Username")
#         self.username_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 5px;")
#         layout.addWidget(self.username_input)

#         # Password input with toggle
#         password_layout = QHBoxLayout()
#         self.password_input = QLineEdit(self)
#         self.password_input.setPlaceholderText("Enter Password")
#         self.password_input.setEchoMode(QLineEdit.Password)
#         self.password_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 5px;")

#         self.toggle_password_button = QPushButton("👁")
#         self.toggle_password_button.setFixedSize(40, 30)
#         self.toggle_password_button.setStyleSheet("background: #333; border-radius: 5px; color: white; font-size: 12px;")
#         self.toggle_password_button.clicked.connect(self.toggle_password)

#         password_layout.addWidget(self.password_input)
#         password_layout.addWidget(self.toggle_password_button)
#         layout.addLayout(password_layout)

#         # Role selection dropdown
#         self.role_input = QComboBox(self)
#         self.role_input.addItems(["admin", "user"])
#         self.role_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 5px;")
#         layout.addWidget(self.role_input)

#         # Add user button
#         self.add_button = QPushButton("Add User")
#         self.add_button.setIcon(QIcon("icons/add_user.png"))
#         self.add_button.setStyleSheet("""
#             QPushButton {
#                 background-color: #1db954;
#                 padding: 10px;
#                 font-size: 16px;
#                 border-radius: 5px;
#             }
#             QPushButton:hover {
#                 background-color: #17a44b;
#             }
#             QPushButton:pressed {
#                 background-color: #128a3d;
#             }
#         """)
#         self.add_button.clicked.connect(self.add_user)
#         layout.addWidget(self.add_button)

#         # Error label
#         self.error_label = QLabel("")
#         self.error_label.setStyleSheet("color: red; font-size: 14px;")
#         layout.addWidget(self.error_label)

#         self.setLayout(layout)

#     def toggle_password(self):
#         """Toggle password visibility."""
#         if self.password_input.echoMode() == QLineEdit.Password:
#             self.password_input.setEchoMode(QLineEdit.Normal)
#         else:
#             self.password_input.setEchoMode(QLineEdit.Password)

#     def add_user(self):
#         username = self.username_input.text().strip()
#         password = self.password_input.text().strip()
#         role = self.role_input.currentText().strip().lower()

#         if not username or not password:
#             self.error_label.setText("All fields are required.")
#             return

#         users = load_users()
#         if len(users) >= MAX_USERS:
#             QMessageBox.warning(self, "Limit Exceeded", f"Cannot add more than {MAX_USERS} users.")
#             return

#         # Check for duplicate username
#         if any(user["username"] == username for user in users):
#             self.error_label.setText("Username already exists.")
#             return

#         # Add new user
#         users.append({"username": username, "password": password, "role": role})
#         save_users(users)

#         # Update parent dashboard
#         if self.parent:
#             self.parent.user_count_label.setText(f"Users: {len(users)}/{MAX_USERS}")

#         QMessageBox.information(self, "Success", "User added successfully!")
#         self.close()
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox
from PyQt5.QtGui import QIcon
from utils.file_utils import load_users, save_users
from utils.constants import MAX_USERS

class AddUserScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add User")
        self.setGeometry(200, 200, 400, 300)
        self.setStyleSheet("background-color: black; color: white;")
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Username input
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(self.password_input)

        # Role dropdown (ComboBox)
        self.role_dropdown = QComboBox(self)
        self.role_dropdown.addItems(["Admin", "User" , "Staff"])
        self.role_dropdown.setStyleSheet("padding: 10px; font-size: 14px;")
        layout.addWidget(self.role_dropdown)

        # Add user button
        self.add_button = QPushButton("Add User")
        self.add_button.setIcon(QIcon("icons/add_user.png"))
        self.add_button.setStyleSheet("padding: 15px; font-size: 16px; background-color: #1db954; color: white;")
        self.add_button.clicked.connect(self.add_user)
        layout.addWidget(self.add_button)

        # Close Button
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("padding: 15px; font-size: 16px; background-color: #ff3333; color: white;")
        self.close_button.clicked.connect(self.close_form)
        layout.addWidget(self.close_button)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 14px;")
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def add_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_dropdown.currentText().lower()  # Get selected role

        if not username or not password:
            self.error_label.setText("All fields are required.")
            return

        users = load_users()
        if len(users) >= MAX_USERS:
            QMessageBox.warning(self, "Limit Exceeded", f"Cannot add more than {MAX_USERS} users.")
            return

        for user in users:
            if user["username"] == username:
                self.error_label.setText("Username already exists.")
                return

        users.append({"username": username, "password": password, "role": role})
        save_users(users)

        if self.parent:
            self.parent.user_count_label.setText(f"Users: {len(users)}/{MAX_USERS}")

        QMessageBox.information(self, "Success", "User added successfully!")
        self.close()

    def close_form(self):
        """Close the form when the user doesn't want to add a new user."""
        self.close()
