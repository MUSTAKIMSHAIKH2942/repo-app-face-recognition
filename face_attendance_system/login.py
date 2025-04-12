import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt
from admin_dashboard import AdminDashboard
from user_dashboard import UserDashboard
from utils.file_utils import load_users

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera App - Login")
        self.default_width = 600
        self.default_height = 400
        self.is_fullscreen = False  # Track fullscreen mode
        
        self.setGeometry(400, 200, self.default_width, self.default_height)
        self.setFixedSize(self.default_width, self.default_height)  # Fixed size initially
        self.setStyleSheet("background-color: #1C1C1C; color: white;")  # Dark theme
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Login Box Container
        form_container = QFrame(self)
        form_container.setStyleSheet("""
            QFrame {
                background-color: #2E2E2E;
                border-radius: 10px;
                border: 2px solid #4CAF50;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout()

        # Title
        title_label = QLabel("Camera System Login")
        # title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-bottom: 15px; padding")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-bottom: 15px; padding: 32px;")
        title_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setStyleSheet("""
            padding: 12px; font-size: 16px; border-radius: 5px; 
            border: 1px solid #555; background-color: white; color: black;
        """)
        form_layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            padding: 12px; font-size: 16px; border-radius: 5px; 
            border: 1px solid #555; background-color: white; color: black;
        """)
        form_layout.addWidget(self.password_input)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 14px; margin-bottom: 10px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self.error_label)

        # Button Layout
        button_layout = QHBoxLayout()

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            background-color: #4CAF50; color: white; padding: 12px; 
            font-size: 16px; border-radius: 5px;
        """)
        self.login_button.clicked.connect(self.login)
        button_layout.addWidget(self.login_button)

        # # Fullscreen Toggle Button
        # self.toggle_button = QPushButton("click for size")
        # self.toggle_button.setStyleSheet("""
        #     background-color: #2196F3; color: white; padding: 12px; 
        #     font-size: 16px; border-radius: 5px;
        # """)
        # self.toggle_button.clicked.connect(self.toggle_fullscreen)
        # button_layout.addWidget(self.toggle_button)

        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("""
            background-color: #D32F2F; color: white; padding: 12px; 
            font-size: 16px; border-radius: 5px;
        """)
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

        form_layout.addLayout(button_layout)

        # Apply layout to form container
        form_container.setLayout(form_layout)
        form_container.setFixedSize(400, 300)  # Fixed form size

        # Centering logic
        main_layout.addStretch()
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.is_fullscreen:
            self.setFixedSize(self.default_width, self.default_height)  # Restore default size
            self.showNormal()  # Exit fullscreen
        else:
            self.showFullScreen()  # Enter fullscreen
        self.is_fullscreen = not self.is_fullscreen  # Toggle state

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        users = load_users()
        for user in users:
            if user["username"] == username and user["password"] == password:
                if user["role"] == "admin":
                    self.admin_dashboard = AdminDashboard()
                    self.admin_dashboard.show()
                    self.close()
                elif user["role"] == "user":
                    self.user_dashboard = UserDashboard()
                    self.user_dashboard.show()
                    self.close()
                return

        self.error_label.setText("Invalid credentials. Please try again.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_page = LoginPage()
    login_page.show()
    sys.exit(app.exec_())
