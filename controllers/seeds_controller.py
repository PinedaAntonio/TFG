from fastapi import APIRouter
from fastapi.responses import FileResponse
from services.seeds_service import SeedsService

router = APIRouter()
service = SeedsService()

@router.post("/generate-seeds/{slug:path}")
def generate_seeds(slug: str):
    file_path = service.generate_seeds_excel(slug)
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file_path)
