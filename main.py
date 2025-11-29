import os
import sys
from pathlib import Path

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QApplication

from controllers.FlowController import FlowController
from controllers.TestMetrics import TestMetrics
from db.InitRepository import InitRepository
from db.models import TestMetaData
from pages.AnswerPage import AnswerPage
from pages.MainFormPage import MainFormPage

CURRENT_DIRECTORY = Path(__file__).resolve().parent


def step_draw(is_tutorial: bool, question_path, answer_paths):
    def _factory():
        page = AnswerPage(is_tutorial=is_tutorial, question_path=question_path, answer_paths=answer_paths)
        return page

    return _factory


answer_paths = ['assets:A/a1a1.png', 'assets:A/a1a2.png', 'assets:A/a1a3.png',
                'assets:A/a1a4.png', 'assets:A/a1a5.png', 'assets:A/a1a6.png']
question_path = 'assets:A/a1q.png'
SEQUENCE = [
    step_draw(is_tutorial=False, question_path=question_path, answer_paths=answer_paths),
    step_draw(is_tutorial=False, question_path=question_path, answer_paths=answer_paths),
    step_draw(is_tutorial=False, question_path=question_path, answer_paths=answer_paths),
]


def main():
    # InitRepository().createTypes()
    # InitRepository().createRavenExaminationTable()
    # InitRepository().createRavenAnswerTable()
    app = QApplication(sys.argv)

    QDir.addSearchPath("assets", os.fspath(CURRENT_DIRECTORY / "assets"))

    metrics = TestMetrics()

    controller = FlowController()
    controller.set_loop(True)
    controller.set_sequence(SEQUENCE)
    controller.set_test_mode(True)
    controller.set_metrics(metrics)
    # metrics.start_test()

    main_page = MainFormPage()
    main_page.showMaximized()

    def on_test_complete():
        summary = metrics.end_test()
        print("SUMMARY:", summary)
        controller.set_test_mode(False)

    def on_start_requested():
        meta = main_page.main_form.get_test_metadata()
        metrics.test_meta_data(meta)
        metrics.start_test()
        main_page.close()
        controller.set_on_complete(on_test_complete)
        controller.start()

    main_page.startRequested.connect(on_start_requested)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
