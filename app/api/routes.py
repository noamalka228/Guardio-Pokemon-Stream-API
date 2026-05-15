"""
Router for defining API routes.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["Pokemon"])
def read_root():
    """
    Returns a welcome message.
    """
    return {"message": "Welcome to Pokemon Stream API"}
