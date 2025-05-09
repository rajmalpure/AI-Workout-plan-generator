from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import UserProfile, WorkoutSession
from app.generator import generate_workout
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Workout Plan Generator API!"}

@app.post("/generate-workout", response_model=List[WorkoutSession])
def generate(user: UserProfile):
    return generate_workout(user)
