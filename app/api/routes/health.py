<<<<<<< HEAD
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
=======
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
>>>>>>> 21599b0b39eba37876fc43d9838497fbe2974000
    return {"status": "ok"}