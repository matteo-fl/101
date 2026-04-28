from fastapi import APIRouter
from app.storage.memory_store import get_presentation, save_presentation

router = APIRouter()

@router.get("/presentation/{pid}")
def get_presentation_route(pid: str):
    return get_presentation(pid)

@router.post("/presentation/{pid}")
def update_presentation(pid: str, data: dict):
    save_presentation(pid, data)
    return {"status": "ok"}