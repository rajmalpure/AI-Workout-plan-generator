from datetime import datetime, timedelta
from app.schemas import UserProfile, WorkoutSession, WorkoutSection, Exercise
from app.utils import load_exercises
import os
import json
from dotenv import load_dotenv
from google import genai

# Load API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Load exercise data
ALL_EXERCISES = load_exercises()

# 🔍 Exercise filter logic
def filter_exercises(section_type: str, level: str, equipment: list[str], target_muscles=None):
    matches = []
    for ex in ALL_EXERCISES:
        if ex["type"].lower() != section_type.lower():
            continue
        if ex["level"].lower() != level.lower() and ex["level"].lower() != "all":
            continue
        if ex["equipment"].lower() not in [e.lower() for e in equipment] and ex["equipment"].lower() != "none":
            continue
        if target_muscles and ex["muscle_group"].lower() not in [m.lower() for m in target_muscles]:
            continue
        matches.append(ex)
    print(f"[DEBUG] {section_type.upper()} matches: {len(matches)}")
    return matches

# 🧮 Convert types
def convert_exercise_data(exercise):
    if "sets" in exercise and exercise["sets"] not in (None, "", "null"):
        try:
            exercise["sets"] = float(exercise["sets"])
        except ValueError:
            exercise["sets"] = None
    else:
        exercise["sets"] = None
    return exercise

# 🧠 Generate AI-powered plan using Gemini
def ai_generate_detailed_plan(user: UserProfile) -> list[dict]:
    prompt = f"""
You are a professional AI fitness coach. Generate a 12-session workout plan for the user below.

Each session must include:
- "title": A 2-4 word catchy name
- "focus": A 1-sentence session goal
- "target_muscles": List of 1-2 muscle groups (e.g., "core", "legs", "full_body")
- "intensity": One of "low", "moderate", or "high"

Return a valid JSON array of 12 sessions, no markdown, no explanation.

User:
- Name: {user.name}
- Age: {user.age}
- Gender: {user.gender}
- Goal: {user.goal}
- Experience: {user.experience}
- Equipment: {', '.join(user.equipment)}
- Days/week: {user.days_per_week}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Or "gemini-2.0-pro"
            contents=prompt
        )
        output = response.text.strip()
        print("[GEMINI RAW RESPONSE]:\n", output)

        plan = json.loads(output)
        assert isinstance(plan, list) and len(plan) == 12
        return plan

    except Exception as e:
        print("[GEMINI ERROR]:", e)
        return [
            {
                "title": f"Session {i+1}",
                "focus": "General fitness",
                "target_muscles": [],
                "intensity": "moderate"
            } for i in range(12)
        ]

# 🏋️‍♀️ Generate final workout plan using AI + filters
def generate_workout(user: UserProfile):
    plan = []
    start_date = datetime.today()
    ai_sessions = ai_generate_detailed_plan(user)

    # ✅ Include bodyweight by default
    user_equipment = user.equipment.copy()
    if "bodyweight" not in [e.lower() for e in user_equipment]:
        user_equipment.append("bodyweight")

    for i in range(12):
        session_info = ai_sessions[i]
        date = start_date + timedelta(days=i)

        title = session_info.get("title", f"Session {i+1}")
        focus = session_info.get("focus", "General fitness")
        target_muscles = session_info.get("target_muscles", [])
        intensity = session_info.get("intensity", "moderate")

        print(f"[DEBUG] Session {i+1} — {title} | Focus: {focus} | Muscles: {target_muscles} | Intensity: {intensity}")
        print(f"[DEBUG] Equipment: {user_equipment}")

        warmup = filter_exercises("warmup", user.experience, user_equipment)[:2]
        main = filter_exercises("main", user.experience, user_equipment, target_muscles)[:3]
        cooldown = filter_exercises("cooldown", user.experience, user_equipment)[:2]

        if not main:
            print(f"[WARNING] No main exercises for session {i+1}. Using fallback.")
            main = filter_exercises("main", "all", ["bodyweight", "none"])[:3]

        plan.append(WorkoutSession(
            session=i + 1,
            date=date.strftime('%Y-%m-%d'),
            title=title,
            focus=focus,
            intensity=intensity,
            sections=WorkoutSection(
                warmup=[Exercise(**convert_exercise_data(ex)) for ex in warmup],
                main=[Exercise(**convert_exercise_data(ex)) for ex in main],
                cooldown=[Exercise(**convert_exercise_data(ex)) for ex in cooldown]
            )
        ))

    return plan
