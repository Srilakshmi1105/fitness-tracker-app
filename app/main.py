from __future__ import annotations
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Dummy user store for example (replace with DB)
fake_users_db = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(BaseModel):
    email: EmailStr
    hashed_password: str


class UserIn(BaseModel):
    email: EmailStr
    password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/register")
async def register(user_in: UserIn):
    if user_in.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user_in.password)
    fake_users_db[user_in.email] = {"email": user_in.email, "hashed_password": hashed_password}
    return {"msg": "User registered successfully"}


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["email"]},
                                       expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None or email not in fake_users_db:
            raise credentials_exception
        return fake_users_db[email]
    except JWTError:
        raise credentials_exception


@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["email"]}


# ----------------------
# Workout Logging Models
# ----------------------

class Workout(BaseModel):
    id: int
    workout_type: str
    duration_minutes: int
    calories_burned: int
    date: str  # ISO date string, e.g. "2025-08-06"


user_workouts: dict[str, List[Workout]] = {}


@app.post("/workouts", status_code=201)
async def add_workout(
        workout: Workout,
        current_user: dict = Depends(get_current_user)
):
    email = current_user["email"]
    if email not in user_workouts:
        user_workouts[email] = []
    user_workouts[email].append(workout)
    return {"msg": "Workout added successfully", "workout": workout}


@app.get("/workouts", response_model=List[Workout])
async def get_workouts(current_user: dict = Depends(get_current_user)):
    email = current_user["email"]
    return user_workouts.get(email, [])


# ----------------------
# Meal Logging Models
# ----------------------

class Meal(BaseModel):
    id: int
    meal_type: str  # e.g., Breakfast, Lunch, Dinner, Snack
    calories: int
    description: str | None = None
    date: str  # ISO date string


user_meals: dict[str, List[Meal]] = {}


@app.post("/meals", status_code=201)
async def add_meal(
        meal: Meal,
        current_user: dict = Depends(get_current_user)
):
    email = current_user["email"]
    if email not in user_meals:
        user_meals[email] = []
    user_meals[email].append(meal)
    return {"msg": "Meal logged successfully", "meal": meal}


@app.get("/meals", response_model=List[Meal])
async def get_meals(current_user: dict = Depends(get_current_user)):
    email = current_user["email"]
    return user_meals.get(email, [])


# ----------------------
# Weight Tracking Models
# ----------------------

class WeightEntry(BaseModel):
    id: int
    weight_kg: float
    date: str  # ISO date string


user_weights: dict[str, List[WeightEntry]] = {}


@app.post("/weights", status_code=201)
async def add_weight(
        weight: WeightEntry,
        current_user: dict = Depends(get_current_user)
):
    email = current_user["email"]
    if email not in user_weights:
        user_weights[email] = []
    user_weights[email].append(weight)
    return {"msg": "Weight logged successfully", "weight": weight}


@app.get("/weights", response_model=List[WeightEntry])
async def get_weights(current_user: dict = Depends(get_current_user)):
    email = current_user["email"]
    return user_weights.get(email, [])
