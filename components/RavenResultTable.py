from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QSizePolicy, QHeaderView, QScrollBar
)

from answers import (
    MODULE_A_ANSWERS,
    MODULE_B_ANSWERS,
    MODULE_C_ANSWERS,
    MODULE_D_ANSWERS,
    MODULE_E_ANSWERS,
)
from db.repository.RavenAnswerRepository import RavenAnswerRepository

MODULE_MAP = {
    "A": MODULE_A_ANSWERS,
    "B": MODULE_B_ANSWERS,
    "C": MODULE_C_ANSWERS,
    "D": MODULE_D_ANSWERS,
    "E": MODULE_E_ANSWERS,
}

MODES = ["A", "B", "C", "D", "E"]

QUESTIONS_PER_MODULE = 12
TOTAL_QUESTIONS = QUESTIONS_PER_MODULE * len(MODES)
COL_NUM = 5  # nowa kolumna "Seria"


class RavenResultTable(QWidget):
    ravenRepository = RavenAnswerRepository()

    def __init__(self, examination_id, parent=None):
        super().__init__(parent)

        self.examination_id = examination_id

        self.table = QTableWidget(TOTAL_QUESTIONS + 1, COL_NUM)  # +1 na podsumowanie
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.table)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Ustawienie fixed height, aby wymusić scroll wertykalny
        fixed_height = 600  # możesz dostosować do potrzeb
        self.table.setMinimumHeight(fixed_height)
        self.table.setMaximumHeight(fixed_height)

        # Włącz scroll wertykalny (domyślnie jest)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.patient_answers = self._load_data()

        self._setup_ui()
        self._populate_table()

    def _load_data(self):
        """Pobranie odpowiedzi z bazy"""
        return self.ravenRepository.get_answers_by_examination_id(
            examination_id=self.examination_id
        )

    def _setup_ui(self):
        table = self.table

        table.setAlternatingRowColors(True)
        table.horizontalHeader().setVisible(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bfbfbf;
                font-size: 11pt;
                border: 2px solid #a0a0a0;
                border-radius: 6px;
                background-color: #f6f6f6;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)

        headers = ["Numer pytania", "Seria", "Odpowiedź użytkownika", "Poprawna odpowiedź", "Czas (s)"]
        for i, h in enumerate(headers):
            item = QTableWidgetItem(h)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            table.setHorizontalHeaderItem(i, item)

        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _populate_table(self):
        correct_count = 0

        # 1️⃣ najpierw grupujemy według card_mode (serii)
        grouped = {mode: [] for mode in MODES}

        for ans in self.patient_answers:
            grouped[ans.card_mode].append(ans)

        # 2️⃣ sort po card wewnątrz serii (1..12)
        for mode in MODES:
            grouped[mode].sort(key=lambda a: a.card)

        # 3️⃣ płaska lista w kolejności A→B→C→D→E
        ordered_answers = []
        for mode in MODES:
            ordered_answers.extend(grouped[mode])

        # 4️⃣ teraz enumerate działa poprawnie (1..60)
        for row_index, ans in enumerate(ordered_answers):
            global_question_number = row_index + 1

            examine_mode = ans.card_mode  # A/B/C/D/E
            correct_ans = MODULE_MAP[examine_mode].get(ans.card)

            user_ans = ans.answer
            duration = round(ans.duration_s, 2)

            is_correct = user_ans == correct_ans
            if is_correct:
                correct_count += 1

            # Numer pytania
            self._set_cell(row_index, 0, str(global_question_number), bold=True)

            # Seria
            self._set_cell(row_index, 1, examine_mode, bold=True)

            # Odpowiedź użytkownika
            self._set_answer_cell(row_index, 2, str(user_ans), is_correct)

            # Poprawna odpowiedź
            self._set_cell(row_index, 3, str(correct_ans), bold=True)

            # Czas
            self._set_cell(row_index, 4, str(duration), bold=True)

        # Podsumowanie
        summary_row = TOTAL_QUESTIONS
        self._set_cell(summary_row, 0, "Poprawnych:", bold=True)
        self._set_cell(summary_row, 1, "-", bold=True)
        self._set_cell(summary_row, 2, f"{correct_count}/{TOTAL_QUESTIONS}", bold=True)

        avg_time = round(sum(a.duration_s for a in ordered_answers) / TOTAL_QUESTIONS, 2)
        self._set_cell(summary_row, 4, f"{avg_time}s", bold=True)

    def _set_cell(self, row, col, text, bold=False):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = item.font()
        font.setBold(bold)
        item.setFont(font)
        self.table.setItem(row, col, item)

    def _set_answer_cell(self, row, col, text, is_correct):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if is_correct:
            item.setBackground(QColor(200, 247, 197))  # jasna zieleń
        else:
            item.setBackground(QColor(247, 197, 197))  # jasna czerwień

        font = item.font()
        font.setBold(True)
        item.setFont(font)

        self.table.setItem(row, col, item)
