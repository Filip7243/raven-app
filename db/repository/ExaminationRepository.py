from datetime import timedelta

from db.database_manager_singleton import get_db
from db.models import RavenExaminationDTO, PreviousExaminationsDTO


class ExaminationRepository:
    def __init__(self):
        self.db = get_db()

    def insert_examination(self, exam: RavenExaminationDTO):
        query = """
                INSERT INTO raven_examination (patient_id,
                                               date,
                                               whole_time,
                                               avg_time,
                                               age_years,
                                               age_months,
                                               age_days,
                                               visual_impairment,
                                               impairment_description,
                                               education,
                                               education_details,
                                               comments,
                                               examination_reason,
                                               total_duration_s)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    exam.patient_id,
                    exam.date,
                    exam.whole_time,
                    exam.avg_time,
                    exam.age_years,
                    exam.age_months,
                    exam.age_days,
                    exam.visual_impairment,
                    exam.impairment_description,
                    exam.education.value if exam.education else None,
                    exam.education_details.value if exam.education_details else None,
                    exam.comments,
                    exam.examination_reason,
                    exam.total_duration_s,
                ),
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id

    def update_examination(self, exam: RavenExaminationDTO):
        query = """
                UPDATE raven_examination
                SET patient_id = %s,
                    date       = %s,
                    whole_time = %s,
                    avg_time   = %s,
                    age_years  = %s,
                    age_months = %s,
                    age_days   = %s,
                    visual_impairment = %s,
                    impairment_description = %s,
                    education = %s,
                    education_details = %s,
                    comments = %s,
                    examination_reason = %s,
                    total_duration_s = %s
                WHERE id = %s
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    exam.patient_id,
                    exam.date,
                    exam.whole_time,
                    exam.avg_time,
                    exam.age_years,
                    exam.age_months,
                    exam.age_days,
                    exam.visual_impairment,
                    exam.impairment_description,
                    exam.education.value if exam.education else None,
                    exam.education_details.value if exam.education_details else None,
                    exam.comments,
                    exam.examination_reason,
                    exam.total_duration_s,
                    exam.id,
                ),
            )
            updated = cur.fetchone()
            self.db.conn.commit()
            return updated['id'] if updated else None

    def get_examination_by_id(self, exam_id: int):
        query = """
                SELECT *
                FROM raven_examination
                WHERE id = %s; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (exam_id,))
            row = cur.fetchone()
            if not row:
                return None

            # Konwersja pól tekstowych na enumy
            from db.models import School, SchoolDetails
            if row.get('education'):
                row['education'] = School(row['education'])
            if row.get('education_details'):
                row['education_details'] = SchoolDetails(row['education_details'])

            return RavenExaminationDTO(**row)

    def get_previous_examinations(self, patient_id) -> list[PreviousExaminationsDTO]:
        query = """
                SELECT e.id         as id,
                       e.whole_time as whole_time,
                       e.avg_time   as avg_time,
                       e.date       as date
                FROM raven_examination e
                         JOIN patient p ON p.id = e.patient_id
                WHERE p.id = %s \
                """

        with self.db.conn.cursor() as cur:
            cur.execute(query, (patient_id,))
            rows = cur.fetchall()
            if not rows:
                return []

            results = []
            for row in rows:
                results.append(PreviousExaminationsDTO(
                    patient_id=patient_id,
                    examine_id=row['id'],
                    failure_mappings=2,
                    valid_mappings=8,
                    avg_time=row['avg_time'],
                    whole_time=row['whole_time'],
                    pominiecia=0,
                    znieksztalcenia=0,
                    perserwacje=0,
                    rotacje=0,
                    przemieszczenia=0,
                    bledy_wzglednej_wielkosci=0,
                    result="-----",
                    comment="",
                    examine_date=row['date']
                ))

            return results

    def get_latest_examinations_with_patients(self):
        query = """
                SELECT e.id as exam_id,
                       e.patient_id as patient_id,
                       p.first_name as first_name,
                       p.last_name as last_name,
                       e.date as exam_date
                FROM raven_examination e
                JOIN patient p ON e.patient_id = p.id
                ORDER BY e.date DESC, exam_id DESC
                LIMIT 50;
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def update_examination_times(self, whole_time: timedelta, avg_time: timedelta, exam_id: int):
        query = """
                UPDATE raven_examination
                SET whole_time = %s,
                    avg_time   = %s
                WHERE id = %s
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    whole_time,
                    avg_time,
                    exam_id,
                ),
            )
            updated = cur.fetchone()
            self.db.conn.commit()
            return updated['id'] if updated else None
