from PyQt6.QtCore import QDir, QUrl, pyqtSignal, Qt, QRect
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy

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

        self.setStyleSheet("background-color: black;")
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
        # KARTA A4 (Centralny kontener)
        # ============================================
        self.card = QFrame(self)
        self.card.setStyleSheet("background-color: white; border-radius: 5px;")
        self.card.setObjectName("A4Card")

        self.april = AprilTagsComponent(self.card, num_tags=4)
        # AprilTagsComponent będzie pozycjonowany w resizeEvent

        # -----------------------
        # UI LAYOUT (Wewnątrz karty)
        # -----------------------
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(100, 100, 100, 100)  # Większe marginesy na April Tagi
        self.card_layout.setSpacing(0)  # Brak odstępu między elementami w layoutcie pionowym
        # self.card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Usunięto, dodamy stretch
        
        self.card_layout.addStretch()

        # 1) QUESTION na górze
        if self.question_path:
            self.question_widget = Question(self.question_path)
            self.card_layout.addWidget(self.question_widget)
        
        self.card_layout.addSpacing(5) # Mniejszy odstęp między pytaniem a odpowiedziami

        # 2) ANSWER BUTTONS w 2 rzędach
        num = len(self.answer_paths)
        assert num in (6, 8), "answer_paths musi mieć 6 lub 8 elementów"

        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(2) # Mniejszy odstęp między przyciskami
        row1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(2) # Mniejszy odstęp między przyciskami
        row2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        half = num // 2
        index = 1

        for i in range(half):
            btn = AnswerButton(self.answer_paths[i])
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            # btn.setFixedSize(120, 100) # Opcjonalnie: wymuszenie rozmiaru dla zacieśnienia
            btn.setMaximumSize(250, 200)  # Zwiększono limit rozmiaru, aby przyciski były wyraźniejsze
            btn.answer_id = index
            btn.clicked.connect(self.handle_answer_click)
            row1.addWidget(btn)
            index += 1

        for i in range(half, num):
            btn = AnswerButton(self.answer_paths[i])
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            btn.setMaximumSize(250, 200)  # Zwiększono limit rozmiaru, aby przyciski były wyraźniejsze
            btn.answer_id = index
            btn.clicked.connect(self.handle_answer_click)
            row2.addWidget(btn)
            index += 1

        self.card_layout.addLayout(row1)
        # self.card_layout.addSpacing(1) # Usunięto nadmiarowy odstęp między rzędami
        self.card_layout.addLayout(row2)
        
        self.card_layout.addStretch()

        # Główny layout strony (nie używamy go do karty, bo pozycjonujemy ją ręcznie)
        # ale zostawiamy self.setLayout, żeby tło było wypełnione czernią
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def handle_answer_click(self):
        btn = self.sender()
        self.selected_answer = btn.answer_id
        self.finished.emit()

    def get_answer(self):
        return self.selected_answer

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Zachowanie proporcji A4 dla karty (np. 1:1.41)
        w, h = self.width(), self.height()
        target_aspect = 0.7  # Przybliżenie dla A4 pionowo (szerokość / wysokość)

        # Obliczamy maksymalne wymiary karty zachowując margines 5%
        max_card_w = int(w * 0.95)
        max_card_h = int(h * 0.95)

        # Próbujemy dopasować do wysokości
        card_h = max_card_h
        card_w = int(card_h * target_aspect)

        # Jeśli szerokość przekracza dostępną przestrzeń, dopasowujemy do szerokości
        if card_w > max_card_w:
            card_w = max_card_w
            card_h = int(card_w / target_aspect)

        x = (w - card_w) // 2
        y = (h - card_h) // 2
        self.card.setGeometry(x, y, card_w, card_h)

        tag_size = min(card_w, card_h) // 12
        self.card_layout.setContentsMargins(tag_size, tag_size, tag_size, tag_size)
        self.card_layout.setSpacing(0)  # Utrzymanie braku odstępu przy zmianie rozmiaru

        self.april.setGeometry(0, 0, self.card.width(), self.card.height())
        self.april.raise_()  # Tagi na wierzchu, ale nie blokują myszy (WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        # Wymuszenie czarnego tła za pomocą paintEvent, aby upewnić się, że styl jest stosowany
        import PyQt6.QtGui as QtGui
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("black"))
