from PyQt6.QtCore import Qt, QRectF, QRect
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy


class Question(QWidget):
    def __init__(self, img_path, parent=None):
        super().__init__(parent)
        self.img_path = img_path
        self.renderer = None
        if img_path.endswith('.svg'):
            self.renderer = QSvgRenderer(img_path)

        self.pixmap = QPixmap(img_path) if not self.renderer else None

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.update_pixmap()

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.setMinimumHeight(400) # Zwiększono z 200

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmap()

    def update_pixmap(self):
        label_size = self.image_label.size()
        if label_size.width() <= 0 or label_size.height() <= 0:
            return

        if self.renderer:
            # Renderowanie SVG do pixmapy o odpowiednim rozmiarze z zachowaniem proporcji
            pixmap = QPixmap(label_size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)

            # Obliczanie proporcji
            svg_size = self.renderer.defaultSize()
            aspect_ratio = svg_size.width() / svg_size.height()

            target_w = label_size.width()
            target_h = label_size.height()

            if target_w / target_h > aspect_ratio:
                # Etykieta jest szersza niż SVG
                render_w = int(target_h * aspect_ratio)
                render_h = target_h
            else:
                # Etykieta jest wyższa niż SVG
                render_w = target_w
                render_h = int(target_w / aspect_ratio)

            # Centrowanie wewnątrz pixmapy
            x = (target_w - render_w) // 2
            y = (target_h - render_h) // 2
            self.renderer.render(painter, QRectF(x, y, render_w, render_h))
            painter.end()
            self.image_label.setPixmap(pixmap)
        else:
            if self.pixmap and not self.pixmap.isNull():
                scaled_pixmap = self.pixmap.scaled(
                    label_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)

    def sizeHint(self):
        if self.renderer:
            return self.renderer.defaultSize()
        if self.pixmap:
            return self.pixmap.size()
        return super().sizeHint()
