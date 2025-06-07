from fastapi import APIRouter, HTTPException
from services.player_service import PlayerService

router = APIRouter()
service = PlayerService()

@router.get("/player/{player_id}")
def get_player_data(player_id: int):
    try:
        player_data = service.get_player_stats(player_id)
        return player_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
