from constants import NOTES_DATA
from schemas import CodeNote


def get_notes() -> list[CodeNote]:
    return [CodeNote(**note) for note in NOTES_DATA]
