import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from db.service.ExaminationService import ExaminationService
from db.repository.PatientRepository import PatientRepository
from db.repository.RavenAnswerRepository import RavenAnswerRepository
from answers import (
    MODULE_A_ANSWERS,
    MODULE_B_ANSWERS,
    MODULE_C_ANSWERS,
    MODULE_D_ANSWERS,
    MODULE_E_ANSWERS,
)

MODULE_MAP = {
    "A": MODULE_A_ANSWERS,
    "B": MODULE_B_ANSWERS,
    "C": MODULE_C_ANSWERS,
    "D": MODULE_D_ANSWERS,
    "E": MODULE_E_ANSWERS,
}

MODES = ["A", "B", "C", "D", "E"]


class PdfGenerator:
    def __init__(self):
        self.patient_repo = PatientRepository()
        self.examination_service = ExaminationService()
        self.raven_answer_repo = RavenAnswerRepository()
        self.base_dir = Path.home() / "raven" / "outputs"

        # Rejestracja czcionki DejaVuSans (obsługa polskich znaków)
        font_path = os.path.join("assets", "fonts", "DejaVuSans.ttf")
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            self.font_name = 'DejaVuSans'
        else:
            self.font_name = 'Helvetica'

    def _format_timedelta(self, td):
        if td is None:
            return "0 minut 0 sekund"
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes} minut {seconds} sekund"

    def generate_report(self, exam_id, output_path):
        examination = self.examination_service.get_examination_by_id(exam_id)
        if not examination:
            return False

        patient = self.patient_repo.get_patient_by_id(examination.patient_id)
        if not patient:
            return False

        answers = self.raven_answer_repo.get_answers_by_examination_id(exam_id)

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Definicja stylów
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=self.font_name,
            fontSize=18,
            spaceAfter=12,
            alignment=1  # Center
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=self.font_name,
            fontSize=14,
            spaceAfter=10
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=self.font_name,
            fontSize=10
        )

        elements.append(Paragraph(f"Raport z badania Raven - ID: {exam_id}", title_style))
        elements.append(Spacer(1, 12))

        # --- Tabela 1: Dane pacjenta ---
        elements.append(Paragraph("Dane pacjenta", heading_style))

        impairment_str = "TAK" if examination.visual_impairment else "NIE"
        if examination.visual_impairment and examination.impairment_description:
            impairment_str += f" - {examination.impairment_description}"

        patient_data = [
            ["Imię", patient.first_name],
            ["Nazwisko", patient.last_name],
            ["Płeć", patient.gender.value if hasattr(patient.gender, 'value') else patient.gender],
            ["Data urodzenia", str(patient.date_of_birth)],
            ["Ręka dominująca", patient.dominant_hand.value if hasattr(patient.dominant_hand, 'value') else patient.dominant_hand],
            ["Wada wzroku", impairment_str],
            ["Wykształcenie",
             f"{examination.education.value if hasattr(examination.education, 'value') else (examination.education or '')} - {examination.education_details.value if hasattr(examination.education_details, 'value') else (examination.education_details or '')}"],
            ["Wiek", f"{examination.age_years} lat, {examination.age_months} mies., {examination.age_days} dni"]
        ]

        patient_table = Table(patient_data, colWidths=[150, 300])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 24))

        # --- Tabela 2: Dane badania ---
        elements.append(Paragraph("Podsumowanie badania", heading_style))

        exam_data = [
            ["Data badania", str(examination.date)],
            ["Czas całkowity", self._format_timedelta(examination.whole_time)],
            ["Średni czas na zadanie", self._format_timedelta(examination.avg_time)]
        ]

        exam_table = Table(exam_data, colWidths=[150, 300])
        exam_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
        ]))
        elements.append(exam_table)
        elements.append(Spacer(1, 24))

        # --- Tabela 3: Wyniki szczegółowe ---
        elements.append(Paragraph("Wyniki szczegółowe", heading_style))

        results_header = ["Nr", "Seria", "Karta", "Odpowiedź", "Poprawna", "Czas (s)"]
        results_data = [results_header]

        # Grupowanie i sortowanie odpowiedzi
        grouped = {mode: [] for mode in MODES}
        for ans in answers:
            if ans.test_type in grouped:
                grouped[ans.test_type].append(ans)

        for mode in MODES:
            grouped[mode].sort(key=lambda a: a.card)

        ordered_answers = []
        for mode in MODES:
            ordered_answers.extend(grouped[mode])

        correct_count = 0
        for i, ans in enumerate(ordered_answers, start=1):
            correct_ans = MODULE_MAP.get(ans.test_type, {}).get(ans.card)
            is_correct = (ans.answer == correct_ans)
            if is_correct:
                correct_count += 1

            results_data.append([
                str(i),
                ans.test_type,
                str(ans.card),
                str(ans.answer),
                "TAK" if is_correct else f"NIE ({correct_ans})",
                f"{ans.duration_s:.2f}" if ans.duration_s is not None else "0.00"
            ])

        results_table = Table(results_data, repeatRows=1, colWidths=[30, 50, 50, 80, 100, 70])

        # Stylizacja tabeli wyników
        table_style_list = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
        ]

        # Kolorowanie poprawności
        for i, ans in enumerate(ordered_answers, start=1):
            correct_ans = MODULE_MAP.get(ans.test_type, {}).get(ans.card)
            if ans.answer == correct_ans:
                table_style_list.append(('BACKGROUND', (4, i), (4, i), colors.lightgreen))
            else:
                table_style_list.append(('BACKGROUND', (4, i), (4, i), colors.lightpink))

        results_table.setStyle(TableStyle(table_style_list))
        elements.append(results_table)

        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(f"Suma poprawnych odpowiedzi: {correct_count} / {len(ordered_answers)}", normal_style))

        try:
            doc.build(elements)
            return True
        except Exception as e:
            print(f"Błąd podczas budowania PDF: {e}")
            return False
