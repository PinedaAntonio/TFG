from fastapi import APIRouter, Path, HTTPException
from services.tournament_service import TournamentService

router = APIRouter()
service = TournamentService()

@router.get("/participants/{slug:path}")
def participants_with_sets(slug: str = Path(..., description="Slug completo del evento")):
    try:
        # Obtener información del torneo
        tournament_data = service.get_event_info(slug)

        # Obtener los participantes y sets asociados
        participants_with_sets = service.get_participants_with_sets(slug)

        # Incluir la información del torneo junto con los participantes y sets
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
        raise e  # Re-lanzamos el error HTTP si ocurre
    except Exception as e:
        # Capturamos cualquier otro error y lo enviamos con un detalle
        raise HTTPException(status_code=500, detail=str(e))
