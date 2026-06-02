from __future__ import annotations

from .schemas import (
    Exercise,
    ParsedIntent,
    RecommendationItem,
    RecommendationResponse,
    SafetyBlock,
)


def _matches_filters(exercise: Exercise, intent: ParsedIntent) -> bool:
    if intent.body_part and exercise.body_part != intent.body_part:
        return False
    if intent.equipment and exercise.equipment not in intent.equipment:
        return False
    if intent.level and exercise.level != intent.level:
        return False
    return True


def _blocked_injuries(exercise: Exercise, injuries: list[str]) -> list[str]:
    injury_set = set(injuries)
    return sorted(injury_set.intersection(exercise.excluded_injuries))


def _to_item(exercise: Exercise, injuries: list[str]) -> RecommendationItem:
    safety_notes = ["ผ่าน Rule Engine: ไม่มีแท็กข้อห้ามที่ตรงกับอาการบาดเจ็บที่ระบุ"] if injuries else []
    return RecommendationItem(
        title=exercise.title,
        desc=exercise.desc,
        type=exercise.type,
        body_part=exercise.body_part,
        equipment=exercise.equipment,
        level=exercise.level,
        rating=exercise.rating,
        safety_notes=safety_notes,
    )


def recommend(catalog: list[Exercise], intent: ParsedIntent, max_results: int = 5) -> RecommendationResponse:
    """Filter catalog deterministically; never invent exercise names."""
    filtered = [exercise for exercise in catalog if _matches_filters(exercise, intent)]

    safety_blocks: list[SafetyBlock] = []
    safe: list[Exercise] = []
    for exercise in filtered:
        blocked = _blocked_injuries(exercise, intent.injuries)
        if blocked:
            safety_blocks.append(
                SafetyBlock(
                    requested_title=exercise.title if exercise.title in intent.requested_titles else None,
                    reason=f"{exercise.title} ถูกตัดออกเพราะมีแท็กข้อห้าม: {', '.join(blocked)}",
                    blocked_injuries=blocked,
                )
            )
        else:
            safe.append(exercise)

    if not safe and any(block.requested_title for block in safety_blocks):
        safe = [
            exercise
            for exercise in catalog
            if not _blocked_injuries(exercise, intent.injuries)
            and exercise.title not in intent.requested_titles
        ]

    safe.sort(key=lambda exercise: exercise.rating, reverse=True)
    recommendations = [_to_item(exercise, intent.injuries) for exercise in safe[:max_results]]

    if recommendations:
        status = "safety_block" if any(block.requested_title for block in safety_blocks) else "ok"
        return RecommendationResponse(
            status=status,
            message_th=_build_message(intent, recommendations, safety_blocks),
            parsed_intent=intent,
            safety_blocks=safety_blocks,
            recommendations=recommendations,
        )

    return RecommendationResponse(
        status="safety_block" if safety_blocks else "no_match",
        message_th=_build_no_match_message(intent, safety_blocks),
        parsed_intent=intent,
        safety_blocks=safety_blocks,
        recommendations=[],
    )


def _build_message(
    intent: ParsedIntent,
    recommendations: list[RecommendationItem],
    safety_blocks: list[SafetyBlock],
) -> str:
    names = ", ".join(f"**{item.title}**" for item in recommendations)
    injury_note = ""
    if intent.injuries:
        injury_note = " ระบบได้ตัดท่าที่ชนกับอาการบาดเจ็บออกก่อนแล้ว"
    block_note = ""
    if any(block.requested_title for block in safety_blocks):
        block_note = " ท่าที่คุณเจาะจงบางท่าถูกปฏิเสธเพื่อความปลอดภัย"
    return f"แนะนำ {names} จากฐานข้อมูลของเราเท่านั้นครับ{injury_note}{block_note}"


def _build_no_match_message(intent: ParsedIntent, safety_blocks: list[SafetyBlock]) -> str:
    if safety_blocks:
        return "ขออภัยครับ ระบบไม่พบท่าที่ผ่านเงื่อนไขความปลอดภัยทั้งหมด จึงไม่แนะนำท่าเสี่ยงให้ครับ"
    return "ขออภัยครับ ยังไม่พบท่าออกกำลังกายในฐานข้อมูลที่ตรงกับเงื่อนไขนี้"