from fitness_ai.catalog import load_exercises
from fitness_ai.parser import parse_intent
from fitness_ai.recommender import recommend


def test_beginner_band_abdominal_recommends_only_catalog_items():
    catalog = load_exercises()
    intent = parse_intent("อยากออกกำลังกายหน้าท้อง เพิ่งเริ่มต้น ที่บ้านมีสายแรงต้าน", catalog)

    response = recommend(catalog, intent, max_results=3)

    catalog_titles = {exercise.title for exercise in catalog}
    assert response.status == "ok"
    assert response.recommendations
    assert {item.title for item in response.recommendations}.issubset(catalog_titles)
    assert response.recommendations[0].title == "Standing band anti-rotation press"


def test_wrist_injury_excludes_wrist_tagged_exercises():
    catalog = load_exercises()
    intent = parse_intent("อยากเล่นท้อง มีสายแรงต้าน แต่ช่วงนี้เจ็บข้อมือมาก ยันพื้นไม่ไหว", catalog)

    response = recommend(catalog, intent, max_results=10)

    exclusions_by_title = {exercise.title: exercise.excluded_injuries for exercise in catalog}
    assert all("wrist" not in exclusions_by_title[item.title] for item in response.recommendations)
    assert "Partner plank" not in {item.title for item in response.recommendations}
    assert any(block.reason.startswith("Partner plank ถูกตัดออก") for block in response.safety_blocks)
    assert "Banded crunch" in {item.title for item in response.recommendations}


def test_requested_lower_back_risk_is_blocked_and_safe_alternative_returned():
    catalog = load_exercises()
    intent = parse_intent("ช่วงนี้เจ็บหลังล่างมาก แต่อยากฝืนเล่นท่า Bench barbell rollout", catalog)

    response = recommend(catalog, intent, max_results=5)

    assert response.status == "safety_block"
    assert "Bench barbell rollout" not in {item.title for item in response.recommendations}
    assert any(block.requested_title == "Bench barbell rollout" for block in response.safety_blocks)
    assert response.recommendations


def test_no_safe_match_returns_safety_block_without_inventing_names():
    catalog = load_exercises()
    intent = parse_intent("เจ็บข้อมือ อยากเล่น kettlebell ขั้นสูง หน้าท้อง", catalog)

    response = recommend(catalog, intent, max_results=5)

    assert response.status == "safety_block"
    assert response.recommendations == []
    assert response.safety_blocks[0].blocked_injuries == ["wrist"]