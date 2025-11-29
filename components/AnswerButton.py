from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect


class AnswerButton(QPushButton):
    def __init__(self, img_path):
        super().__init__()

        # Wczytanie obrazka
        pixmap = QPixmap(img_path)

        # ustawiamy ikonę
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(pixmap.size())

        # rozmiar przycisku = rozmiar obrazka
        self.setFixedSize(pixmap.width(), pixmap.height())

        # Przycisk ma być "przezroczysty"
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            QPushButton:pressed {
                opacity: 0.7;
            }
        """)

        # Kursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # # Cień
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)
