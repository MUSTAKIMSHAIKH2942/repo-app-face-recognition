from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QMessageBox
from face_recognition import train_faces

class TrainModelScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Train Model")
        layout = QVBoxLayout()

        self.train_btn = QPushButton("Start Training")
        self.train_btn.clicked.connect(self.train_model)
        layout.addWidget(self.train_btn)

        self.setLayout(layout)

    def train_model(self):
        train_faces()
        QMessageBox.information(self, "Training Complete", "Face Recognition Model Trained Successfully")
