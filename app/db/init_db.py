from app.db.database import engine, Base
from app.models import user, workout, meal, weight_log

def init_db():
    Base.metadata.create_all(bind=engine)
