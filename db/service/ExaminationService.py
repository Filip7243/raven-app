from datetime import timedelta

from db.models import PreviousExaminationsDTO, PatientIdentity
from db.repository.ExaminationRepository import ExaminationRepository
from db.repository.PatientRepository import PatientRepository


class ExaminationService:
    examinationRepo = ExaminationRepository()
    patientRepo = PatientRepository()

    def update_examination_times(self, examination_id, whole_time: timedelta, avg_time: timedelta):
        return self.examinationRepo.update_examination_times(whole_time, avg_time, examination_id)
