from PyQt6.QtCore import QDir, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from components.AnswerButton import AnswerButton
from components.AprilTagsComponent import AprilTagsComponent
from components.Question import Question


class AnswerPage(QWidget):
    finished = pyqtSignal()
    is_answer_page = True  # Flaga dla FlowController

    def __init__(self, parent=None, audio=None, question_path=None, answer_paths=None, is_tutorial=True):
        super().__init__(parent)
        self.setWindowTitle("Draw Figure Page")

        self.audio = audio
        self.is_tutorial = is_tutorial
        self.question_path = question_path
        self.answer_paths = answer_paths or []
        self.exporter = self.get_answer
        self.selected_answer = None  # Tutaj przechowujemy odpowiedź dla danej karty

        self.setStyleSheet("background-color: white;")
        self.setAutoFillBackground(True)

        # -----------------------
        # AUDIO
        # -----------------------
        self.player = None
        if self.audio is not None:
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(1.0)

            dir_assets = QDir("assets:/audio")
            audio_path = dir_assets.absoluteFilePath(self.audio)
            self.player.setSource(QUrl.fromLocalFile(audio_path))

            self.player.stop()
            self.player.play()

        # ============================================
        # APRIL TAGS – pełnoekranowe tło
        # ============================================
        self.april = AprilTagsComponent(self, num_tags=4)
        self.april.setGeometry(0, 0, self.width(), self.height())
        self.april.lower()  # <- jest POD layoutem

        # -----------------------
        # UI LAYOUT
        # -----------------------
        root = QVBoxLayout()
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(5)

        # 1) QUESTION na górze
        if self.question_path:
            self.question_widget = Question(self.question_path)
            root.addWidget(self.question_widget)

        # 2) ANSWER BUTTONS w 2 rzędach
        # liczba = 6 lub 8
        num = len(self.answer_paths)
        assert num in (6, 8), "answer_paths musi mieć 6 lub 8 elementów"

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()

        half = num // 2  # 3 lub 4

        index = 1  # index odpowiedzi (od 1 do 6 lub 8)

        # pierwszy rząd
        for i in range(half):
            btn = AnswerButton(self.answer_paths[i])
            btn.answer_id = index
            btn.clicked.connect(self.handle_answer_click)
            row1.addWidget(btn)
            index += 1

        # drugi rząd
        for i in range(half, num):
            btn = AnswerButton(self.answer_paths[i])
            btn.answer_id = index
            btn.clicked.connect(self.handle_answer_click)
            row2.addWidget(btn)
            index += 1

        root.addLayout(row1)
        root.addLayout(row2)

        self.setLayout(root)

    def handle_answer_click(self):
        btn = self.sender()
        self.selected_answer = btn.answer_id
        self.finished.emit()

    def get_answer(self):
        return self.selected_answer

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.setStyleSheet("background-color: white;")
        self.setAutoFillBackground(True)
        self.april.setGeometry(0, 0, self.width(), self.height())
        self.april.lower()
