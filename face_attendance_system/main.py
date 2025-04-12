import sys
from login import LoginPage
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_page = LoginPage()
    login_page.show()  # Standard windowed mode
    sys.exit(app.exec_())
