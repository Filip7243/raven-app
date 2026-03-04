import os
import sys
from pathlib import Path

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QApplication

from controllers.FlowController import FlowController
from controllers.TestMetrics import TestMetrics
from pages.AnswerPage import AnswerPage
from pages.MainFormPage import MainFormPage
from pages.ResultPage import ResultsPage

CURRENT_DIRECTORY = Path(__file__).resolve().parent


def step_draw(is_tutorial: bool, question_path, answer_paths):
    def _factory():
        page = AnswerPage(is_tutorial=is_tutorial, question_path=question_path, answer_paths=answer_paths)
        return page

    return _factory


def build_module_sequence(module_letter: str):
    """
    Generuje sekwencję 12 kroków dla modułu (A, B, C, D, E)
    Każde pytanie ma format:
        assets:<M>/<m><n>q.png
        assets:<M>/<m><n>a1.png ... a6.png
    """
    module_lower = module_letter.lower()
    steps = []

    for i in range(1, 13):  # 1..12
        question_path = f"assets:{module_letter}/{module_lower}{i}q.png"

        answer_paths = [
            f"assets:{module_letter}/{module_lower}{i}a{ans_num}.png"
            for ans_num in range(1, 7)
        ]

        steps.append(step_draw(
            is_tutorial=False,
            question_path=question_path,
            answer_paths=answer_paths
        ))

    return steps


A_SEQUENCE = build_module_sequence("A")
B_SEQUENCE = build_module_sequence("A")
C_SEQUENCE = build_module_sequence("A")
D_SEQUENCE = build_module_sequence("A")
E_SEQUENCE = build_module_sequence("A")
# ALL_SEQUENCES = [A_SEQUENCE, B_SEQUENCE, C_SEQUENCE, D_SEQUENCE, E_SEQUENCE]
ALL_SEQUENCES = [A_SEQUENCE]
# MODULES = ["A", "B", "C", "D", "E"]
MODULES = ["A"]


def main():
    # InitRepository().createTypes()
    # InitRepository().createRavenExaminationTable()
    # InitRepository().createRavenAnswerTable()
    app = QApplication(sys.argv)
    current_module_index = 0

    QDir.addSearchPath("assets", os.fspath(CURRENT_DIRECTORY / "assets"))

    metrics = TestMetrics()

    controller = FlowController()
    controller.set_loop(True)
    controller.set_sequence(ALL_SEQUENCES[0])
    controller.set_test_mode(True)
    controller.set_metrics(metrics)
    # metrics.start_test()

    main_page = MainFormPage()
    main_page.showMaximized()

    def on_test_complete():
        nonlocal current_module_index
        try:
            summary = metrics.end_test()
            print(summary)
            meta = main_page.main_form.get_test_metadata()
            print(meta)
            if current_module_index == len(MODULES):
                meta.test_type = MODULES[current_module_index - 1]

                try:
                    controller.set_test_mode(False)
                    results_page = ResultsPage(examine_id=meta.examine_id, patient_id=meta.patient_id,
                                               exam_mode=meta.test_type)
                    controller.stack.addWidget(results_page)
                    controller.stack.setCurrentWidget(results_page)
                except Exception as e:
                    print(e)
                return
            meta.test_type = MODULES[current_module_index]
            metrics.test_meta_data(meta)
            metrics.start_test()
            controller.set_sequence(ALL_SEQUENCES[current_module_index])
            current_module_index += 1
            controller.set_on_complete(on_test_complete)
            controller.start()
        except Exception as e:
            import traceback
            print("ON TEST COMPLETE", e)
            traceback.print_exc()  # wypisze pełny stack trace na stdout

    def on_start_requested():
        nonlocal current_module_index
        current_module_index += 1
        meta = main_page.main_form.get_test_metadata()
        metrics.test_meta_data(meta)
        print("META SETTED:", meta)
        metrics.start_test()

        # Logika wyboru ekranu:
        screens = QGuiApplication.screens()
        print(f"DEBUG: Wykryto {len(screens)} ekranów.")
        for idx, s in enumerate(screens):
            print(f"DEBUG: Ekran {idx}: {s.name()} | Geometry: {s.geometry()}")

        # Jeśli są co najmniej dwa ekrany, wybieramy drugi (indeks 1).
        target_screen = screens[1] if len(screens) > 1 else screens[0]
        print(f"DEBUG: Wybrany ekran docelowy: {target_screen.name()}")

        # Ukrywamy formularz lekarza
        main_page.close()

        # Ustawiamy ekran dla okna testowego przed startem
        stack = controller.stack
        stack.hide()
        stack.setScreen(target_screen)
        geom = target_screen.geometry()
        stack.move(geom.topLeft())

        controller.set_on_complete(on_test_complete)
        controller.start()

    main_page.startRequested.connect(on_start_requested)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
