DROP TABLE IF EXISTS raven_examination CASCADE;
DROP TABLE IF EXISTS raven_answer CASCADE;

CREATE TYPE raven_mode AS ENUM ('A', 'B', 'C', 'D', 'E');

CREATE TABLE IF NOT EXISTS raven_migration (
    id SERIAL PRIMARY KEY,
    finished BOOLEAN DEFAULT FALSE
);

CREATE TABLE raven_examination (
    id SERIAL PRIMARY KEY,

    patient_id INTEGER NOT NULL,
    date DATE NOT NULL,

    whole_time INTERVAL,
    avg_time INTERVAL,

    age_years INTEGER,
    age_months INTEGER,
    age_days INTEGER,

    visual_impairment BOOLEAN DEFAULT FALSE,
    impairment_description TEXT,

    education school,
    education_details school_details,

    comments TEXT,
    examination_reason TEXT,

    total_duration_s DECIMAL(10,4),

    CONSTRAINT fk_raven_exam_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(id)
        ON DELETE CASCADE
);

CREATE TABLE raven_answer (
    id SERIAL PRIMARY KEY,

    raven_examination_id INTEGER NOT NULL,

    card INTEGER NOT NULL,

    started_at_ts TIMESTAMP,
    finished_at_ts TIMESTAMP,

    test_type TEXT,
    answer INTEGER,

    duration_s DECIMAL(10,4),

    CONSTRAINT fk_raven_answer_exam
        FOREIGN KEY (raven_examination_id)
        REFERENCES raven_examination(id)
        ON DELETE CASCADE
);

INSERT INTO raven_migration (id, finished)
VALUES (1, TRUE)
ON CONFLICT (id) DO UPDATE SET finished = TRUE;