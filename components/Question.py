from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class Question(QWidget):
    def __init__(self, img_path, parent=None):
        super().__init__(parent)

        # Layout z centrowaniem
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Etykieta z obrazkiem
        self.image_label = QLabel()
        pixmap = QPixmap(img_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.image_label)
        self.setLayout(layout)
