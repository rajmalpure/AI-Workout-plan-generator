from datetime import datetime, timedelta
from app.schemas import UserProfile, WorkoutSession, WorkoutSection, Exercise
from app.utils import load_exercises

ALL_EXERCISES = load_exercises()

def filter_exercises(section_type: str, level: str, equipment: list[str]):
    return [
        ex for ex in ALL_EXERCISES
        if ex["type"].lower() == section_type.lower()
        and (ex["level"].lower() == level.lower() or ex["level"].lower() == "all")
        and (ex["equipment"].lower() in [e.lower() for e in equipment] or ex["equipment"].lower() == "none")
    ]

def convert_exercise_data(exercise):
    # Convert sets field to float if possible
    if "sets" in exercise and exercise["sets"] not in (None, "", "null"):
        try:
            exercise["sets"] = float(exercise["sets"])
        except ValueError:
            exercise["sets"] = None
    else:
        exercise["sets"] = None
    return exercise

def generate_workout(user: UserProfile):
    plan = []
    start_date = datetime.today()

    for i in range(12):
        date = start_date + timedelta(days=i)
        warmup = filter_exercises("warmup", user.experience, user.equipment)[:2]
        main = filter_exercises("main", user.experience, user.equipment)[i % 5 : i % 5 + 3]
        cooldown = filter_exercises("cooldown", user.experience, user.equipment)[:2]

        plan.append(WorkoutSession(
            session=i + 1,
            date=date.strftime('%Y-%m-%d'),
            sections=WorkoutSection(
                warmup=[Exercise(**convert_exercise_data(ex)) for ex in warmup],
                main=[Exercise(**convert_exercise_data(ex)) for ex in main],
                cooldown=[Exercise(**convert_exercise_data(ex)) for ex in cooldown]
            )
        ))

    return plan
