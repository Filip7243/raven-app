from db.database_manager_singleton import get_db
from db.models import RavenAnswer


class RavenAnswerRepository:
    def __init__(self):
        self.db = get_db()

    def insert_raven_answer(self, answer: RavenAnswer):
        query = """
                INSERT INTO raven_answer (examination_id, \
                                          card, \
                                          answer, \
                                          duration_s, \
                                          started_at, \
                                          finished_at,
                                          card_mode)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """

        with self.db.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    answer.examination_id,
                    answer.card,
                    answer.answer,
                    answer.duration_s,
                    answer.started_at,
                    answer.finished_at,
                    answer.card_mode.value
                )
            )
            new_id = cur.fetchone()['id']
            self.db.conn.commit()
            return new_id

    def get_answers_by_examination_id(self, examination_id: int):
        query = """
                SELECT *
                FROM raven_answer
                WHERE examination_id = %s
                ORDER BY card_mode, card;
                """

        with self.db.conn.cursor() as cur:
            cur.execute(query, (examination_id,))
            rows = cur.fetchall()
            if not rows:
                return []

            answers = []
            for row in rows:
                answers.append(RavenAnswer(**row))
            return answers
