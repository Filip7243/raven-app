from db.database_manager_singleton import get_db
from db.models import RavenNormResultDTO


class RavenNormsRepository:
    def __init__(self):
        self.db = get_db()

    def get_norms_by_age_and_score(self, total_months: int, user_raw_score: int) -> list[RavenNormResultDTO]:
        """
        Pobiera dopasowane normy dla podanego wieku (w miesiącach) i wyniku surowego.
        Wykorzystuje parametr DISTINCT ON (s.id), aby pobrać najlepszy dopasowany wynik dla każdej normy.
        """
        query = """
            SELECT DISTINCT ON (s.id) 
                s.name || ' (' || s.year || ')' AS nazwa_normy,
                n.raw_score AS dopasowany_wynik_z_tabeli,
                %s AS faktyczny_wynik,
                n.percentile AS centyl,
                n.sten AS sten
            FROM raven_norm_sets s
            JOIN raven_age_groups g ON s.id = g.norm_set_id
            JOIN raven_norms n ON g.id = n.age_group_id
            WHERE %s BETWEEN g.age_from_months AND g.age_to_months
              AND n.raw_score <= %s
            ORDER BY s.id, n.raw_score DESC;
        """
        with self.db.conn.cursor() as cur:
            cur.execute(query, (user_raw_score, total_months, user_raw_score))
            rows = cur.fetchall()
            if not rows:
                return []
            
            return [RavenNormResultDTO(**row) for row in rows]
