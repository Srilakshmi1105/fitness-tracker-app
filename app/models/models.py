from sqlalchemy import Table, Column, Integer, String, Float, Date, MetaData

from database import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, index=True),
    Column("hashed_password", String),
)

workouts = Table(
    "workouts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("workout_type", String),
    Column("duration_minutes", Integer),
    Column("calories_burned", Integer),
    Column("date", String),
)

meals = Table(
    "meals",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("meal_type", String),
    Column("calories", Integer),
    Column("description", String, nullable=True),
    Column("date", String),
)

weights = Table(
    "weights",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("weight_kg", Float),
    Column("date", String),
)
