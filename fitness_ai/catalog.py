from __future__ import annotations

import csv
from pathlib import Path

from .schemas import Exercise

DATA_PATH = Path(__file__).resolve().parent / "data" / "exercises.csv"


def load_exercises(path: Path = DATA_PATH) -> list[Exercise]:
    """Load only curated exercises from the business-owned dataset."""
    with path.open(newline="", encoding="utf-8") as file_obj:
        rows = csv.DictReader(file_obj)
        return [
            Exercise(
                title=row["Title"],
                desc=row["Desc"],
                type=row["Type"],
                body_part=row["BodyPart"],
                equipment=row["Equipment"],
                level=row["Level"],
                rating=float(row["Rating"]),
                excluded_injuries=row["Excluded_Injuries"],
            )
            for row in rows
        ]