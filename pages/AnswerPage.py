from PyQt6.QtCore import QDir, QUrl, pyqtSignal, Qt, QRect
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy

from components.AnswerButton import AnswerButton
from components.AprilTagsComponent import AprilTagsComponent
from components.NumberedAnswer import NumberedAnswer
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
        self.card_layout.setSpacing(10)  # Odstęp między elementami

        # 1) QUESTION na górze
        if self.question_path:
            self.question_row = QHBoxLayout()
            self.question_row.setContentsMargins(0, 0, 0, 0)
            self.question_widget = Question(self.question_path)
            self.question_row.addWidget(self.question_widget)
            self.card_layout.addLayout(self.question_row, 12)  # Zwiększono z 9, aby pytanie było jeszcze większe

        self.card_layout.addSpacing(10)  # Odstęp między pytaniem a odpowiedziami

        # 2) ANSWER BUTTONS w 2 rzędach
        num = len(self.answer_paths)
        assert num in (6, 8), "answer_paths musi mieć 6 lub 8 elementów"

        self.row1 = QHBoxLayout()
        self.row1.setContentsMargins(0, 0, 0, 0)
        self.row1.setSpacing(2)  # Mniejszy odstęp między przyciskami
        self.row1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.row2 = QHBoxLayout()
        self.row2.setContentsMargins(0, 0, 0, 0)
        self.row2.setSpacing(2)  # Mniejszy odstęp między przyciskami
        self.row2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        half = num // 2
        index = 1

        for i in range(half):
            btn = NumberedAnswer(self.answer_paths[i], index)
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            # btn.setFixedSize(120, 100) # Opcjonalnie: wymuszenie rozmiaru dla zacieśnienia
            btn.setMaximumSize(800, 600)  # Znacznie zwiększono limit rozmiaru
            btn.answer_id = index
            btn.clicked.connect(self.handle_answer_click)
            self.row1.addWidget(btn, 1)
            index += 1

        for i in range(half, num):
            btn = NumberedAnswer(self.answer_paths[i], index)
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            btn.setMaximumSize(800, 600)  # Znacznie zwiększono limit rozmiaru
            btn.answer_id = index
            btn.clicked.connect(self.handle_answer_click)
            self.row2.addWidget(btn, 1)
            index += 1

        self.card_layout.addLayout(self.row1, 6)
        # self.card_layout.addSpacing(1) # Usunięto nadmiarowy odstęp między rzędami
        self.card_layout.addLayout(self.row2, 6)

        self.card_layout.addStretch(0) # Zredukowano stretch na dole do 0

        # Główny layout strony (nie używamy go do karty, bo pozycjonujemy ją ręcznie)
        # ale zostawiamy self.setLayout, żeby tło było wypełnione czernią
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def handle_answer_click(self):
        # Pobieramy obiekt wysyłający sygnał
        sender = self.sender()
        if hasattr(sender, 'answer_id'):
            self.selected_answer = sender.answer_id
        else:
            # Dla pewności, jeśli sygnał pochodził bezpośrednio z AnswerButton (wewnątrz NumberedAnswer)
            # Ale NumberedAnswer reemituje sygnał clicked, więc senderem będzie NumberedAnswer
            self.selected_answer = getattr(sender, 'answer_id', None)
        
        self.finished.emit()

    def get_answer(self):
        return self.selected_answer

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # ---------------------------
        # Wymiary karty A4
        # ---------------------------
        w, h = self.width(), self.height()
        target_aspect = 0.7  # szerokość / wysokość A4 pionowo

        max_card_w = int(w * 0.98)
        max_card_h = int(h * 0.98)

        card_h = max_card_h
        card_w = int(card_h * target_aspect)
        if card_w > max_card_w:
            card_w = max_card_w
            card_h = int(card_w / target_aspect)

        x = (w - card_w) // 2
        y = (h - card_h) // 2
        self.card.setGeometry(x, y, card_w, card_h)

        # ---------------------------
        # AprilTags i marginesy
        # ---------------------------
        tag_size = (min(card_w, card_h) // 4) - 20
        margin = tag_size + 10
        self.card_layout.setContentsMargins(0, margin - 10, 0, margin)
        self.card_layout.setSpacing(10)

        question_side_margin = margin // 2
        buttons_side_margin = 20
        if hasattr(self, 'question_row'):
            self.question_row.setContentsMargins(question_side_margin, 0, question_side_margin, 0)
        if hasattr(self, 'row1'):
            self.row1.setContentsMargins(buttons_side_margin, 0, buttons_side_margin, 0)
        if hasattr(self, 'row2'):
            self.row2.setContentsMargins(buttons_side_margin, 0, buttons_side_margin, 0)

        # ---------------------------
        # Ustalona proporcja Question vs Buttons
        # ---------------------------
        max_question_h = int(card_h * 0.35)  # Question max 25% wysokości karty
        min_question_h = 150  # minimalna wysokość
        question_h = max(min_question_h, min(max_question_h, self.question_widget.sizeHint().height() if hasattr(self,
                                                                                                                 'question_widget') else min_question_h))

        if hasattr(self, 'question_widget'):
            self.question_widget.setFixedHeight(question_h)

        # ---------------------------
        # Buttony - zachowują swoje minimalne i maksymalne rozmiary
        # ---------------------------
        if hasattr(self, 'row1'):
            for i in range(self.row1.count()):
                wdg = self.row1.itemAt(i).widget()
                if wdg:
                    wdg.setMaximumHeight(200)
        if hasattr(self, 'row2'):
            for i in range(self.row2.count()):
                wdg = self.row2.itemAt(i).widget()
                if wdg:
                    wdg.setMaximumHeight(200)

        # ---------------------------
        # AprilTags na wierzchu
        # ---------------------------
        self.april.setGeometry(0, 0, self.card.width(), self.card.height())
        self.april.raise_()

    def paintEvent(self, event):
        # Wymuszenie czarnego tła za pomocą paintEvent, aby upewnić się, że styl jest stosowany
        import PyQt6.QtGui as QtGui
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("black"))
