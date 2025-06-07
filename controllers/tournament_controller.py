from fastapi import APIRouter, Path, HTTPException
from services.tournament_service import TournamentService

router = APIRouter()
service = TournamentService()

@router.get("/participants/{slug:path}")
def participants_with_sets(slug: str = Path(..., description="Slug completo del evento")):
    try:
        tournament_data = service.get_event_info(slug)
        participants_with_sets = service.get_participants_with_sets(slug)

        return {
            "tournament_info": {
                "tournament_name": tournament_data["tournament_name"],
                "startAt": tournament_data["startAt"],
                "image_url": tournament_data["image_url"],
            },
            "participants": participants_with_sets["participants"],
            "sets": participants_with_sets["sets"]
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
