"""
Router for defining API routes.
"""
from json import JSONDecodeError
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/", tags=["Pokemon"])
def read_root():
    """
    Returns a welcome message.
    """
    return {"message": "Welcome to Pokemon Stream API"}

@router.post("/stream", tags=["Pokemon"])
async def stream(request: Request):
    """
    Returns a stream of pokemon.
    """
    try:
        data = await request.json()
    except JSONDecodeError:
        return {"message": "Invalid JSON"}
    return {"message": data}
