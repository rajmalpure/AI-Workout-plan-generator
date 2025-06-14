from pydantic import BaseModel
from typing import Optional, List

class Exercise(BaseModel):
    name: str
    muscle_group: Optional[str]
    equipment: Optional[str]
    type: Optional[str]
    level: Optional[str]
    sets: Optional[float]
    reps: Optional[str]

class WorkoutSection(BaseModel):
    warmup: List[Exercise]
    main: List[Exercise]
    cooldown: List[Exercise]

class WorkoutSession(BaseModel):
    session: int
    date: str
    title: Optional[str]
    focus: Optional[str]
    intensity: Optional[str]
    sections: WorkoutSection
    
class UserProfile(BaseModel):
    name: str
    age: int
    gender: str
    goal: str
    experience: str
    equipment: List[str]
    days_per_week: int
