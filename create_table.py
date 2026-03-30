from app.db.database import engine, Base
from app.db import models  # IMPORTANT

print("Tables before:", Base.metadata.tables.keys())

Base.metadata.create_all(bind=engine)

print("Tables after:", Base.metadata.tables.keys())
print("Done creating tables 🚀")