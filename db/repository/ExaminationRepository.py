from datetime import timedelta

from db.database_manager_singleton import get_db
from db.models import RavenExamination, PreviousExaminationsDTO


class ExaminationRepository:
    def __init__(self):
        self.db = get_db()

    def insert_examination(self, exam: RavenExamination):
        print("TATUJ MODE:", exam.test_type)
        query = """
                INSERT INTO raven_examination (patient_id,
                                               degree_id,
                                               date,
                                               whole_time,
                                               avg_time,
                                               test_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    exam.patient_id,
                    exam.degree_id,
                    exam.date,
                    exam.whole_time,
                    exam.avg_time,
                    exam.test_type.value,
                ),
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id

    def update_examination(self, exam: RavenExamination):
        query = """
                UPDATE raven_examination
                SET patient_id = %s,
                    degree_id  = %s,
                    date       = %s,
                    whole_time = %s,
                    avg_time   = %s,
                    test_type  = %s
                WHERE id = %s
                RETURNING id; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    exam.patient_id,
                    exam.degree_id,
                    exam.date,
                    exam.whole_time,
                    exam.avg_time,
                    exam.test_type,
                    exam.id,
                ),
            )
            updated = cur.fetchone()
            self.db.conn.commit()
            return updated['id'] if updated else None

    def get_examination_by_id(self, exam_id: int):
        query = """
                SELECT id,
                       patient_id,
                       degree_id,
                       date,
                       whole_time,
                       avg_time,
                       test_type
                FROM raven_examination
                WHERE id = %s; \
                """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (exam_id,))
            row = cur.fetchone()
            if not row:
                return None

            # konwersja wyniku na model Examination
            return RavenExamination(
                id=row['id'],
                patient_id=row['patient_id'],
                degree_id=row['degree_id'],
                date=row['date'],
                whole_time=row['whole_time'],
                avg_time=row['avg_time'],
                test_type=row['test_type'],
            )

    def get_previous_examinations(self, patient_id) -> list[PreviousExaminationsDTO]:
        query = """
                SELECT e.id         as id,
                       e.whole_time as whole_time,
                       e.avg_time   as avg_time,
                       e.date       as date,
                       e.test_type  as test_type
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
                    result="-----",
                    examine_date=row['date'],
                    test_type=row['test_type']
                ))

            return results

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
