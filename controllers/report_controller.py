from fastapi import APIRouter
from fastapi.responses import FileResponse
from services.report_service import ReportService

router = APIRouter()
service = ReportService()

@router.post("/generate-report/{slug:path}")
def generate_report(slug: str):
    file_path = service.generate_excel(slug)
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file_path)
