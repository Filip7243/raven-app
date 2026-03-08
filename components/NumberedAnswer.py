from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from components.AnswerButton import AnswerButton


class NumberedAnswer(QWidget):
    clicked = pyqtSignal()

    def __init__(self, img_path, number, parent=None):
        super().__init__(parent)
        self.number = number

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)

        # Etykieta z numerem
        self.number_label = QLabel(str(self.number))
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.number_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: black;
            background-color: transparent;
        """)
        self.layout.addWidget(self.number_label)

        # Przycisk z odpowiedzią
        self.button = AnswerButton(img_path)
        self.button.clicked.connect(self.clicked.emit)
        self.layout.addWidget(self.button)

        # Ustawiamy politykę rozmiaru, aby komponent mógł się rozszerzać
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

    @property
    def answer_id(self):
        return self.button.answer_id

    @answer_id.setter
    def answer_id(self, value):
        self.button.answer_id = value

    def setMaximumSize(self, *args):
        # Przekazujemy limit do przycisku, ale sami też go trzymamy dla layoutu
        if len(args) == 1:
            # QSize
            self.button.setMaximumSize(args[0])
        else:
            # w, h
            self.button.setMaximumSize(args[0], args[1])
        super().setMaximumSize(*args)

    def setMaximumHeight(self, h):
        # Limitujemy wysokość przycisku, bo numerka chcemy widzieć zawsze
        self.button.setMaximumHeight(h)
        super().setMaximumHeight(h + 30) # Dodatkowy margines na numer
