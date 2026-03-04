from db.database_manager_singleton import get_db
from db.models import RavenAnswerDTO


class RavenAnswerRepository:
    def __init__(self):
        self.db = get_db()

    def insert_raven_answer(self, answer: RavenAnswerDTO):
        query = """
                INSERT INTO raven_answer (raven_examination_id, \
                                          card, \
                                          answer, \
                                          duration_s, \
                                          started_at_ts, \
                                          finished_at_ts,
                                          test_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """

        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    answer.raven_examination_id,
                    answer.card,
                    answer.answer,
                    answer.duration_s,
                    answer.started_at_ts,
                    answer.finished_at_ts,
                    answer.test_type
                )
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id

    def get_answers_by_examination_id(self, examination_id: int):
        query = """
                SELECT *
                FROM raven_answer
                WHERE raven_examination_id = %s
                ORDER BY test_type, card;
                """

        with self.db.conn.cursor() as cur:
            cur.execute(query, (examination_id,))
            rows = cur.fetchall()
            if not rows:
                return []

            answers = []
            for row in rows:
                answers.append(RavenAnswerDTO(**row))
            return answers
