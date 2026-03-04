from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any

from PyQt6.QtCore import QBuffer, QIODeviceBase
from PyQt6.QtGui import QImage

from db.models import TestMetaData, RavenAnswerDTO
from db.repository.RavenAnswerRepository import RavenAnswerRepository
from db.service.ExaminationService import ExaminationService


# from db.models import TestMetaData, Image
# from db.repository.ImageRepository import ImageRepository
# from db.service.ExaminationService import ExaminationService


@dataclass
class AnswerRecord:
    """
    Klasa reprezentująca dane pojedynczego rysunku w teście BVRT.

    Attributes:
        index (int): Identyfikator rysunku.
        started_at (float): Czas (timestamp) pojawienia się planszy do rysowania.
        finished_at (float): Czas (timestamp) kliknięcia przycisku "Dalej", gdy badany uznał, że zakończył rysunek.
        test_type (str): seria testu raven (od A do E)
    """
    index: int
    patient_id: int
    examine_id: int
    started_at: float
    finished_at: float
    test_type: str
    answer: int
    card: int

    @property
    def duration_s(self) -> float:
        """
        Oblicza czas trwania rysowania w sekundach..

        Returns:
            float: Różnica między `finished_at` a `started_at` w sekundach.
        """
        return self.finished_at - self.started_at


class TestMetrics:
    examinationService = ExaminationService()
    ravenAnswerRepository = RavenAnswerRepository()

    def __init__(self, base_dir: Path | None = None):
        self._base_dir = Path(base_dir) if base_dir else Path.home() / "raven" / "outputs"
        print(f"base dir: {self._base_dir}")
        self._test_meta_data: TestMetaData | None = None
        self._session_dir: Path | None = None
        self._test_start: float | None = None
        self._test_end: float | None = None
        self._current_answer_start: float | None = None
        self._records: list[AnswerRecord] = []
        self._answers_counter: int = 0

    @property
    def session_dir(self) -> Path:
        if self._session_dir is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._session_dir = (
                    self._base_dir / f"raven_test_{ts}_patient_id_examine_id"
            )
            self._session_dir.mkdir(parents=True, exist_ok=True)
        return self._session_dir

    def test_meta_data(self, test_meta_data: TestMetaData):
        self._test_meta_data = test_meta_data

    def start_test(self):
        _ = self.session_dir  # Tworzy katalog sesji, jeśli nie istnieje
        self._test_start = perf_counter()
        self._records.clear()  # Usuwamy poprzednie rekordy (jeśli istnieją)
        self._answers_counter = 0
        print("STARTUJE_TEST")

    def end_test(self) -> dict[str, Any]:
        self._test_end = perf_counter()
        summary = {
            "total_duration": (self._test_end - self._test_start) if (self._test_end and self._test_start) else None,
            "answers": [
                {
                    **asdict(record),  # zmieniamy każdy rekord na słownik
                    "duration_s": record.duration_s,  # dodajemy czas trwania rysowania w sekundach
                } for record in self._records
            ]
        }
        print("META W METRICS:", self._test_meta_data)
        avg_time_seconds = 0.0
        if len(self._records) > 0:
            avg_time_seconds = summary["total_duration"] / len(self._records)

        self.examinationService.update_examination_times(self._test_meta_data.examine_id,
                                                         whole_time=timedelta(seconds=summary["total_duration"]),
                                                         avg_time=timedelta(seconds=avg_time_seconds))
        # zapisujemy do JSON
        ((self.session_dir / f"{self._test_meta_data.test_type}_summary.json")
         .write_text(json.dumps(summary, indent=2), encoding="utf-8"))
        return summary

    def start_answering(self):
        self._current_answer_start = perf_counter()
        self._answers_counter += 1

    def finish_answering(self, answer, card):
        if self._current_answer_start is None:
            self._current_answer_start = perf_counter()
        finished_at = perf_counter()
        new_answer = AnswerRecord(
            index=self._answers_counter,
            patient_id=self._test_meta_data.patient_id,
            examine_id=self._test_meta_data.examine_id,
            started_at=self._current_answer_start,
            finished_at=finished_at,
            test_type=self._test_meta_data.test_type,
            answer=answer,
            card=card
        )
        self._records.append(new_answer)
        new_answer = RavenAnswerDTO(
            id=None,
            raven_examination_id=self._test_meta_data.examine_id,
            card=card,
            started_at_ts=datetime.fromtimestamp(self._current_answer_start) if self._current_answer_start else None,
            finished_at_ts=datetime.fromtimestamp(finished_at),
            test_type=self._test_meta_data.test_type,
            answer=answer,
            duration_s=new_answer.duration_s
        )
        self.ravenAnswerRepository.insert_raven_answer(new_answer)
        print("KARTA: ", card)
        print("USER ODPOWIEDZIAL:", answer)
        self._current_answer_start = None
        return new_answer
