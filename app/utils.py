import csv
from pathlib import Path

def load_exercises():
    file_path = Path(__file__).parent / "exercises.csv"
    exercises = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean and convert data
            row['sets'] = float(row['sets']) if row['sets'].strip() else 3.0
            row['reps'] = row['reps'].strip() if row['reps'].strip() else "10"
            row['equipment'] = row['equipment'].strip() if row['equipment'] else "none"
            row['type'] = row['type'].strip() if row['type'] else "main"
            row['level'] = row['level'].strip() if row['level'] else "all"
            exercises.append(dict(row))
    return exercises
