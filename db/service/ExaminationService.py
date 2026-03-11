from datetime import timedelta

from db.models import PreviousExaminationsDTO, PatientIdentity
from db.repository.ExaminationRepository import ExaminationRepository
from db.repository.PatientRepository import PatientRepository


class ExaminationService:
    examinationRepo = ExaminationRepository()
    patientRepo = PatientRepository()

    def update_examination_times(self, examination_id, whole_time: timedelta, avg_time: timedelta):
        return self.examinationRepo.update_examination_times(whole_time, avg_time, examination_id)

    def get_latest_examinations(self):
        return self.examinationRepo.get_latest_examinations_with_patients()

    def get_examination_by_id(self, examination_id: int):
        return self.examinationRepo.get_examination_by_id(examination_id)
