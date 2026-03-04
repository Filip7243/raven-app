from dataclasses import dataclass
from datetime import date, timedelta
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


class RavenMode(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


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
    age_years: int
    age_months: int
    age_days: int
    gender: Gender
    dominant_hand: Hand
    eye_impairment: bool
    eye_description: Optional[str] = None


@dataclass
class Comment:
    patient_id: int
    comment: str


@dataclass
class PatientDegree:
    id: Optional[int]
    patient_id: int
    degree: School
    degree_details: SchoolDetails


@dataclass
class RavenExamination:
    id: Optional[int]
    patient_id: int
    degree_id: int
    date: date
    whole_time: Optional[timedelta]
    avg_time: Optional[timedelta]
    test_type: RavenMode


@dataclass
class Image:
    examine_id: int
    content: bytes
    time: Optional[timedelta]


@dataclass
class AfterwardsOpinion:
    examine_id: int
    opinion: Optional[str]


@dataclass
class TestMetaData:
    examine_id: int
    patient_id: int
    test_type: RavenMode


@dataclass
class PatientSummaryDTO:
    id: Optional[int]
    age_years: int
    age_months: int
    age_days: int
    gender: Gender
    dominant_hand: Hand
    eye_description: Optional[str]
    comment: Optional[str]


@dataclass
class PreviousExaminationsDTO:
    patient_id: int
    examine_id: int
    failure_mappings: int
    valid_mappings: int
    avg_time: timedelta
    whole_time: timedelta
    result: str
    examine_date: date
    test_type: RavenMode


@dataclass
class PatientIdentity:
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    dominant_hand: Hand


@dataclass
class RavenAnswer:
    id: Optional[int]
    examination_id: int
    card: int
    answer: int
    duration_s: float
    started_at: float
    finished_at: float
    card_mode: RavenMode
