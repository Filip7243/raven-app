from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect, QSizePolicy


class AnswerButton(QPushButton):
    def __init__(self, img_path):
        super().__init__()
        self.pixmap = QPixmap(img_path)
        self.setIcon(QIcon(self.pixmap))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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

        self.setMinimumSize(30, 30)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = self.size()
        # Zmniejszono margines ikony, aby lepiej wypełniała przycisk
        icon_size = size - QSize(10, 10)
        if icon_size.width() > 0 and icon_size.height() > 0:
            self.setIconSize(icon_size)

