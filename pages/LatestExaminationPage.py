from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from components.LatestExaminationsTable import LatestExaminationsTable
from components.StyledHeader import StyledHeader
from db.service.ExaminationService import ExaminationService


class LatestExaminationPage(QWidget):
    backRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.examination_service = ExaminationService()

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Nagłówek
        self.header = StyledHeader("OSTATNIE BADANIA")
        layout.addWidget(self.header)

        # Tabela
        self.table = LatestExaminationsTable(parent=self)
        layout.addWidget(self.table)

        # Przycisk powrotu
        bottom_layout = QHBoxLayout()
        self.back_button = QPushButton("Powrót")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setFixedSize(120, 40)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5a6268; }
        """)
        self.back_button.clicked.connect(self.backRequested.emit)

        bottom_layout.addStretch()
        bottom_layout.addWidget(self.back_button)
        layout.addLayout(bottom_layout)

    def load_data(self):
        """Metoda do odświeżania danych w tabeli"""
        try:
            data = self.examination_service.get_latest_examinations()
            self.table.set_data(data)
        except Exception as e:
            print(f"Błąd podczas ładowania ostatnich badań: {e}")

    def showEvent(self, event):
        """Odśwież dane przy każdym pokazaniu strony"""
        super().showEvent(event)
        self.load_data()
