from db.database_manager_singleton import get_db


class InitRepository:
    def __init__(self):
        self.db = get_db()

    def createTypes(self):
        query = """
            CREATE TYPE raven_mode AS ENUM ('A', 'B', 'C', 'D', 'E');
        """
        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Types have been created")

    def createRavenExaminationTable(self):
        query = """
                CREATE TABLE IF NOT EXISTS raven_examination
                (
                    id         SERIAL PRIMARY KEY,
                    patient_id INTEGER REFERENCES patient (id) ON DELETE CASCADE,
                    degree_id  INTEGER REFERENCES patient_degree (id) ON DELETE CASCADE,
                    date       DATE,
                    whole_time INTERVAL,
                    avg_time   INTERVAL,
                    test_type  raven_mode
                );
                CREATE INDEX IF NOT EXISTS idx_examination_patient_id
                    ON raven_examination (patient_id);
                """

        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Examination table has been created")

    def createRavenAnswerTable(self):
        query = """
                CREATE TABLE IF NOT EXISTS raven_answer
                (
                    id             SERIAL PRIMARY KEY,
                    examination_id INTEGER REFERENCES raven_examination (id) ON DELETE CASCADE,
                    card           INTEGER,
                    answer         INTEGER,
                    duration_s     FLOAT,
                    started_at     FLOAT,
                    finished_at    FLOAT
                );
                CREATE INDEX IF NOT EXISTS idx_examination_answer_id
                    ON raven_answer (examination_id);
                """

        with self.db.conn.cursor() as cur:
            cur.execute(query)
            print("Answer table has been created")
