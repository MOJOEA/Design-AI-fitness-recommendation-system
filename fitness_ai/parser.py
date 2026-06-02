from __future__ import annotations

from .schemas import Exercise, ExerciseLevel, ParsedIntent

BODY_PART_KEYWORDS = {
    "Abdominal": ["abdominal", "abs", "core", "หน้าท้อง", "ท้อง", "กล้ามท้อง"],
    "Back": ["back", "กล้ามหลัง", "เล่นหลัง", "ท่าหลัง"],
    "Glutes": ["glutes", "สะโพก", "ก้น"],
    "Full Body": ["full body", "ทั้งตัว", "ทั่วตัว"],
}

EQUIPMENT_KEYWORDS = {
    "Bands": ["bands", "band", "resistance band", "สายแรงต้าน", "ยางยืด"],
    "Barbell": ["barbell", "บาร์เบล"],
    "Kettlebells": ["kettlebell", "kettlebells", "เคตเทิลเบล"],
    "Bodyweight": ["bodyweight", "ไม่ใช้อุปกรณ์", "น้ำหนักตัว"],
    "Dumbbell": ["dumbbell", "ดัมเบล"],
}

LEVEL_KEYWORDS = {
    ExerciseLevel.beginner: ["beginner", "เริ่มต้น", "มือใหม่", "เพิ่งเริ่ม"],
    ExerciseLevel.intermediate: ["intermediate", "ระดับกลาง", "กลางๆ", "ระดับกลางๆ"],
    ExerciseLevel.advanced: ["advanced", "ขั้นสูง", "โปร"],
}

INJURY_KEYWORDS = {
    "wrist": ["wrist", "ข้อมือ", "ยันพื้นไม่ไหว"],
    "lower_back": ["lower back", "lower_back", "หลังล่าง", "เอว"],
    "knee": ["knee", "เข่า"],
    "shoulder": ["shoulder", "ไหล่"],
}

GOAL_KEYWORDS = {
    "strength": ["strength", "สร้างกล้าม", "กล้าม", "หนา"],
    "cardio": ["cardio", "คาร์ดิโอ", "เผาผลาญ"],
}

NEGATIVE_INJURY_PHRASES = ["ไม่เจ็บ", "ไม่มีอาการเจ็บ", "ไม่บาดเจ็บ", "no injury", "not injured"]


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def parse_intent(message: str, catalog: list[Exercise]) -> ParsedIntent:
    """Deterministically parse user language into normalized filters.

    This local parser is intentionally conservative. A production deployment can
    replace this with an LLM/NLU parser only if its JSON output is validated by
    the same Pydantic schema and the downstream rule engine remains authoritative.
    """
    text = message.casefold()

    body_part = next((name for name, words in BODY_PART_KEYWORDS.items() if _contains_any(text, words)), None)
    equipment = [name for name, words in EQUIPMENT_KEYWORDS.items() if _contains_any(text, words)]
    level = next((level for level, words in LEVEL_KEYWORDS.items() if _contains_any(text, words)), None)

    injuries: list[str] = []
    if not _contains_any(text, NEGATIVE_INJURY_PHRASES):
        injuries = [name for name, words in INJURY_KEYWORDS.items() if _contains_any(text, words)]

    goals = [name for name, words in GOAL_KEYWORDS.items() if _contains_any(text, words)]
    requested_titles = [exercise.title for exercise in catalog if exercise.title.casefold() in text]

    return ParsedIntent(
        body_part=body_part,
        equipment=equipment,
        level=level,
        injuries=injuries,
        goals=goals,
        requested_titles=requested_titles,
    )