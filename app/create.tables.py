
from database import engine, metadata


metadata.create_all(engine)
print("Tables created successfully.")
