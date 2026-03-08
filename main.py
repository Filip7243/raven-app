import os
import sys
from pathlib import Path

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QApplication

from controllers.FlowController import FlowController
from controllers.TestMetrics import TestMetrics
from pages.AnswerPage import AnswerPage
from pages.AudioStepPage import AudioStepPage
from pages.MainFormPage import MainFormPage
from pages.ResultPage import ResultsPage

CURRENT_DIRECTORY = Path(__file__).resolve().parent


def step_audio(audio_file: str):
    def _factory():
        page = AudioStepPage(audio=audio_file)
        return page

    return _factory


def step_answer(is_tutorial: bool, question_path, answer_paths):
    def _factory():
        page = AnswerPage(is_tutorial=is_tutorial, question_path=question_path, answer_paths=answer_paths)
        return page

    return _factory


def build_module_sequence(module_letter: str):
    """
    Generuje sekwencję 12 kroków dla modułu (A, B, C, D, E)
    Każdy krok ma format:
        assets:raven/<module_letter>/<module_letter><nn>/matrix.svg
        assets:raven/<module_letter>/<module_letter><nn>/1.svg ... 6.svg lub 8.svg
    """
    steps = []

    for i in range(1, 13):  # 1..12
        step_num = f"{i:02d}"
        folder_path = f"assets:raven/{module_letter}/{module_letter}{step_num}"
        question_path = f"{folder_path}/matrix.png"

        # Sprawdzamy ile jest odpowiedzi (6 lub 8)
        # Na podstawie opisu: w każdym module jest od 1 do 6 lub od 1 do 8 plików
        # Możemy spróbować sprawdzić istnienie pliku 7.svg lub po prostu 
        # sprawdzić fizyczną ścieżkę (assets: jest mapowane w QDir)

        # Aby być bezpiecznym, spróbujemy wygenerować listę na podstawie tego co jest w folderze
        # Ale assets: to specyficzna ścieżka PyQt. 
        # Z opisu wynika, że mamy to po prostu zmienić w kodzie.

        # Zakładamy domyślnie 6, ale jeśli to moduł D lub E, może być 8?
        # Raven Advanced Progressive Matrices mają zazwyczaj 8 odpowiedzi.
        # Sprawdzimy czy dla danego kroku istnieje 8.svg lub 7.svg

        num_answers = 6
        if module_letter in ["C", "D", "E"]:
            num_answers = 8

        answer_paths = [
            f"{folder_path}/{ans_num}.png"
            for ans_num in range(1, num_answers + 1)
        ]

        steps.append(step_answer(
            is_tutorial=False,
            question_path=question_path,
            answer_paths=answer_paths
        ))

    return steps


TUTORIAL_SEQUENCE = [
    step_audio("assets:audio/01_raven_samouczek.wav"),
]

A_SEQUENCE = build_module_sequence("A")
B_SEQUENCE = build_module_sequence("B")
C_SEQUENCE = build_module_sequence("C")
D_SEQUENCE = build_module_sequence("D")
E_SEQUENCE = build_module_sequence("E")
# ALL_SEQUENCES = [A_SEQUENCE, B_SEQUENCE, C_SEQUENCE, D_SEQUENCE, E_SEQUENCE]
ALL_SEQUENCES = [A_SEQUENCE, B_SEQUENCE, C_SEQUENCE, D_SEQUENCE, E_SEQUENCE]
# MODULES = ["A", "B", "C", "D", "E"]
MODULES = ["A", "B", "C", "D", "E"]


def main():
    # InitRepository().createTypes()
    # InitRepository().createRavenExaminationTable()
    # InitRepository().createRavenAnswerTable()
    app = QApplication(sys.argv)
    current_module_index = 0

    QDir.addSearchPath("assets", os.fspath(CURRENT_DIRECTORY / "assets"))

    metrics = TestMetrics()

    controller = FlowController()
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
                try:
                    controller.set_test_mode(False)
                    results_page = ResultsPage(examine_id=meta.examine_id, patient_id=meta.patient_id,
                                               exam_mode=MODULES[current_module_index - 1])
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
            traceback.print_exc()

    def on_tutorial_complete():
        nonlocal current_module_index
        controller.set_loop(False)
        controller.set_on_complete(None)

        # Inicjalizacja metryk i start pierwszego modułu testowego
        meta = main_page.main_form.get_test_metadata()
        meta.test_type = MODULES[current_module_index]
        metrics.test_meta_data(meta)
        metrics.start_test()

        controller.set_sequence(ALL_SEQUENCES[current_module_index])
        current_module_index += 1
        controller.set_test_mode(True)
        controller.set_on_complete(on_test_complete)
        controller.start()

    def on_start_requested():
        # Pobieramy listę wszystkich ekranów
        screens = QGuiApplication.screens()
        print(f"DEBUG: Wykryto {len(screens)} ekranów.")
        for idx, s in enumerate(screens):
            print(f"DEBUG: Ekran {idx}: {s.name()} | Geometry: {s.geometry()}")

        # Wybór ekranu pacjenta (indeks 1 jeśli dostępny)
        target_screen = screens[1] if len(screens) > 1 else screens[0]
        print(f"DEBUG: Wybrany ekran docelowy: {target_screen.name()}")

        # Ukrywamy formularz lekarza
        main_page.close()

        # Konfiguracja okna testowego
        stack = controller.stack
        stack.hide()
        stack.setScreen(target_screen)
        geom = target_screen.geometry()
        stack.move(geom.topLeft())

        # Start od tutoriala
        controller.set_loop(True)
        controller.set_sequence(TUTORIAL_SEQUENCE)
        controller.set_test_mode(False)
        controller.set_on_complete(on_tutorial_complete)
        controller.start()

    main_page.startRequested.connect(on_start_requested)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
