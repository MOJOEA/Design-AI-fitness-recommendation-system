# Personalized Fitness AI Recommendation System

This module implements a zero-hallucination recommendation pipeline for the fitness use case. The LLM-facing responsibilities are intentionally isolated: parsing can be swapped for an external NLP model, and final wording can be replaced by a language model, but the catalog filtering and injury exclusions remain deterministic Python business logic.

## Architecture

1. **Input Parsing**: `fitness_ai.parser.parse_intent` converts natural language into a validated `ParsedIntent` object.
2. **Core Business Logic**: `fitness_ai.recommender.recommend` filters only rows loaded from `fitness_ai/data/exercises.csv`, then blocks any exercise whose `excluded_injuries` intersects with the parsed injuries.
3. **Structured Output**: `fitness_ai.schemas.RecommendationResponse` returns Thai natural-language guidance plus structured JSON fields for frontend consumption.

## Run locally

```bash
python -m pip install -r requirements-fitness.txt
& ".\.venv\Scripts\pip" list
uvicorn fitness_ai.api:app --reload
```

## Run tests

```bash
$env:PYTHONPATH="."
& ".\.venv\Scripts\python.exe" -m pytest tests/test_fitness_ai.py -q
```

Then call:

```bash
curl -X POST http://127.0.0.1:8000/recommendations \
  -H 'Content-Type: application/json' \
  -d '{"message":"อยากเล่นท้อง มีสายแรงต้าน แต่เจ็บข้อมือ", "max_results": 3}'
```

## Safety guarantee boundary

The system never creates exercise names in the recommender. Recommendations are projected from the loaded catalog only. If no safe row exists after filtering, the response contains no recommendation items and explains that the request was blocked or had no match.

# ระบบแนะนำท่าออกกำลังกายอัจฉริยะ (Personalized Fitness AI Recommendation System)

โมดูลนี้คือระบบท่อส่งข้อมูลการแนะนำท่าออกกำลังกาย (Recommendation Pipeline) แบบ **Zero-Hallucination (การันตีข้อมูลไม่หลอน)** สำหรับธุรกิจฟิตเนส โดยมีการแยกส่วนหน้าที่การทำงานกับโมเดลภาษา (LLM) อย่างชัดเจน: ในส่วนของการถอดรหัสคำสั่ง (Parsing) สามารถสลับไปใช้โมเดล NLP ภายนอกได้ และข้อความสรุปผลสุดท้าย (Final Wording) สามารถปรับแต่งด้วย Language Model ได้ แต่ส่วนการคัดกรองข้อมูลคลังท่าทาง (Catalog Filtering) และเงื่อนไขข้อยกเว้นการบาดเจ็บ (Injury Exclusions) จะทำงานอยู่บน **Deterministic Python Business Logic** ที่แม่นยำ 100%

---

# ระบบแนะนำท่าออกกำลังกายอัจฉริยะ (Personalized Fitness AI Recommendation System)

โมดูลนี้คือระบบท่อส่งข้อมูลการแนะนำท่าออกกำลังกาย (Recommendation Pipeline) แบบ **Zero-Hallucination (การันตีข้อมูลไม่หลอน)** สำหรับธุรกิจฟิตเนส โดยมีการแยกส่วนหน้าที่การทำงานกับโมเดลภาษา (LLM) อย่างชัดเจน: ในส่วนของการถอดรหัสคำสั่ง (Parsing) สามารถสลับไปใช้โมเดล NLP ภายนอกได้ และข้อความสรุปผลสุดท้าย (Final Wording) สามารถปรับแต่งด้วย Language Model ได้ แต่ส่วนการคัดกรองข้อมูลคลังท่าทาง (Catalog Filtering) และเงื่อนไขข้อยกเว้นการบาดเจ็บ (Injury Exclusions) จะทำงานอยู่บน **Deterministic Python Business Logic** ที่แม่นยำ 100%

---

## 📂 โครงสร้างไฟล์ (Project Structure)

```bash
DESIGN-AI-FITNESS-RECOMMENDATION-SYSTEM/
├── .venv/                         # Virtual Environment ของ Python
├── fitness_ai/                    # โฟลเดอร์ซอร์สโค้ดหลักของระบบ
│   ├── data/
│   │   └── exercises.csv          # คลังข้อมูลท่าออกกำลังกายที่คัดสรรแล้ว (Curated Dataset)
│   ├── __init__.py
│   ├── api.py                     # ตัวควบคุมระบบ API (FastAPI Endpoints)
│   ├── catalog.py                 # ระบบจัดการและโหลดข้อมูลคลังท่าออกกำลังกาย
│   ├── parser.py                  # ระบบแกะความหมายภาษาธรรมชาติ (NLP Parser)
│   ├── recommender.py             # แกนประมวลผลหลัก ทำหน้าที่คัดเลือกท่า (Core Engine)
│   └── schemas.py                 # โครงสร้างและโมเดลข้อมูล (Pydantic Models)
└── tests/                         # โฟลเดอร์ชุดทดสอบระบบ
    ├── conftest.py                # ไฟล์ตั้งค่า Root Path สำหรับ Pytest
    └── test_fitness_ai.py         # ชุดทดสอบระบบคัดกรองและความปลอดภัย
```

## อธิบายไฟล์การทำงาน (Module Responsibilities)

`fitness_ai/data/exercises.csv: `คลังเก็บข้อมูลท่าออกกำลังกายของธุรกิจ พร้อมแท็กระบุอุปกรณ์ ส่วนของร่างกาย ระดับ และข้อห้ามสำหรับอาการบาดเจ็บ (Excluded_Injuries)

`fitness_ai/catalog.py:`ทำหน้าที่โหลดข้อมูลจากไฟล์ CSV เข้าสู่ระบบอย่างปลอดภัย และคัดกรองเฉพาะแถวข้อมูลที่เป็นของธุรกิจ (Business-owned rows) เท่านั้น

`fitness_ai/parser.py:` แปลงคำสั่งภาษาธรรมชาติ (ทั้งภาษาไทยและอังกฤษ) ให้กลายเป็นออบเจกต์โครงสร้างข้อมูล ParsedIntent ที่ตรวจสอบความถูกต้องแล้ว

`fitness_ai/recommender.py:` แกนประมวลผลหลัก ทำหน้าที่เปรียบเทียบข้อจำกัดด้านอาการบาดเจ็บของผู้ใช้กับแท็กในคลัง หากพบจุดที่ตรงกัน (Intersect) จะตัดท่านั้นทิ้งทันที พร้อมเตรียมข้อความเตือนความปลอดภัย (Safety Blocks)

`fitness_ai/schemas.py:` กำหนดโครงสร้างข้อมูล Request และ Response ด้วย Pydantic เพื่อควบคุมหน้าตาข้อมูลที่จะตอบกลับไปยัง Frontend

`fitness_ai/api.py:` ตัวขับเคลื่อน Web Server ด้วย FastAPI ประกอบไปด้วย Endpoint สำหรับการตรวจเช็กสถานะระบบ และ Endpoint สำหรับการรับคำขอเพื่อแนะนำท่าออกกำลังกาย

## ขอบเขตการรับประกันความปลอดภัย (Safety Guarantee Boundary)
ระบบนี้มีกฎเหล็ก "ห้ามจินตนาการหรือเมคข้อมูลเองเด็ดขาด" โดยผลลัพธ์การแนะนำท่าออกกำลังกายจะมาจากการสกัดโปรเจกต์ข้อมูลที่มีอยู่จริงในคลังแค็ตตาล็อกที่โหลดขึ้นมาเท่านั้น `หากผู้ใช้ระบุเงื่อนไขการบาดเจ็บมา แล้วไม่พบท่าออกกำลังกายใดที่ปลอดภัยหลงเหลืออยู่เลยหลังจากผ่านขั้นตอนการกรอง ระบบจะส่งค่าผลลัพธ์กลับไปเป็นรายการว่าง (Empty Items) `พร้อมข้อความภาษาไทยอธิบายให้ผู้ใช้ทราบอย่างตรงไปตรงมาว่า**คำขอถูกบล็อกเพื่อความปลอดภัย หรือไม่มีท่าที่เหมาะสมตรงกัน และไม่มีการปลอมแปลงชื่อท่าขึ้นมาใหม่ในระบบโดยเด็ดขาด**