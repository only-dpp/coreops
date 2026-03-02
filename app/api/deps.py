<<<<<<< HEAD
from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
=======
from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
>>>>>>> 21599b0b39eba37876fc43d9838497fbe2974000
        db.close()