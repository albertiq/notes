from src.constants import NOTES_DATA
from src.schemas import CodeNote


def get_notes() -> list[CodeNote]:
    return [CodeNote(**note) for note in NOTES_DATA]
