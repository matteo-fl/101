from fastapi import APIRouter
from app.services.llm_service import generate_slides
from app.services.adapter_service import to_canvas
from app.storage.memory_store import save_presentation
import uuid

router = APIRouter()

@router.post("/generate")
async def generate(data: dict):
    llm_result = generate_slides(data)
    canvas_json = to_canvas(llm_result)

    pid = str(uuid.uuid4())
    save_presentation(pid, canvas_json)

    return {"id": pid}