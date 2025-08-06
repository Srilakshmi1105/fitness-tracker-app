import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitness_tracker.db")
