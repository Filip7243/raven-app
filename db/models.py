from dataclasses import dataclass
from datetime import date, timedelta, datetime
from enum import Enum
from typing import Optional


# --- ENUMY ---

class School(Enum):
    PODSTAWOWE = "PODSTAWOWE"
    SREDNIE = "SREDNIE"
    WYZSZE = "WYZSZE"


class SchoolDetails(Enum):
    KLASA1 = "KLASA1"
    KLASA2 = "KLASA2"
    KLASA3 = "KLASA3"
    KLASA4 = "KLASA4"
    KLASA5 = "KLASA5"
    KLASA6 = "KLASA6"
    KLASA7 = "KLASA7"
    KLASA8 = "KLASA8"
    TECHNIKUM = "TECHNIKUM"
    LICEUM = "LICEUM"
    LICENCJAT = "LICENCJAT"
    MAGISTER = "MAGISTER"
    DOKTORAT = "DOKTORAT"
    EDUKACJA_ZAKONCZONE = "EDUKACJA_ZAKONCZONE"


class Hand(Enum):
    PRAWA = "PRAWA"
    LEWA = "LEWA"


class Gender(Enum):
    MEZCZYZNA = "MEZCZYZNA"
    KOBIETA = "KOBIETA"


# --- MODELE DANYCH ---

@dataclass
class Patient:
    id: Optional[int]
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    dominant_hand: Hand


@dataclass
class TestMetaData:
    examine_id: int
    patient_id: int


@dataclass
class PatientSummaryDTO:
    id: Optional[int]
    age_years: int
    age_months: int
    age_days: int
    gender: Gender
    dominant_hand: Hand
    visual_impairment: bool
    impairment_description: Optional[str]
    comment: Optional[str]


@dataclass
class PreviousExaminationsDTO:
    patient_id: int
    examine_id: int
    failure_mappings: int
    valid_mappings: int
    avg_time: timedelta
    whole_time: timedelta
    pominiecia: int
    znieksztalcenia: int
    perserwacje: int
    rotacje: int
    przemieszczenia: int
    bledy_wzglednej_wielkosci: int
    result: str
    comment: Optional[str]
    examine_date: date


@dataclass
class PatientIdentity:
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    dominant_hand: Hand


@dataclass
class RavenExaminationDTO:
    id: Optional[int]
    patient_id: int
    date: date
    whole_time: Optional[timedelta]
    avg_time: Optional[timedelta]
    age_years: Optional[int]
    age_months: Optional[int]
    age_days: Optional[int]
    visual_impairment: bool
    impairment_description: Optional[str]
    education: Optional[School]
    education_details: Optional[SchoolDetails]
    comments: Optional[str]
    examination_reason: Optional[str]
    total_duration_s: Optional[float]


@dataclass
class RavenAnswerDTO:
    id: Optional[int]
    raven_examination_id: int
    card: int
    started_at_ts: Optional[datetime]
    finished_at_ts: Optional[datetime]
    test_type: Optional[str]
    answer: Optional[int]
    duration_s: Optional[float]


@dataclass
class RavenNormResultDTO:
    nazwa_normy: str
    dopasowany_wynik_z_tabeli: int
    faktyczny_wynik: int
    centyl: int
    sten: int
