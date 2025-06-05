from models.startgg_api import StartGGApi

class TournamentService:
    def __init__(self):
        self.api = StartGGApi()

    def get_event_info(self, slug):
        # Llamada al método get_event_info() de la clase StartGGApi
        return self.api.get_event_info(slug)

    def get_participants_with_sets(self, slug):
        # Obtener la información del evento
        event_info = self.get_event_info(slug)  # Ahora usamos el método de la clase misma.
        event_id = event_info["event_id"]
        tournament_name = event_info["tournament_name"]

        # Obtener la lista de participantes
        players = self.api.get_participants_with_ids(event_id)

        sets_by_player = {}

        # Secuencial sin hilos, manteniendo el bucle infinito en cada petición
        for player in players:
            try:
                # Obtener los sets para cada jugador
                sets = self.api.get_sets_for_player_in_tournament(player["playerId"], tournament_name)
                sets_by_player[player["gamerTag"]] = sets
            except Exception as e:
                sets_by_player[player["gamerTag"]] = [{"error": str(e)}]

        return {
            "participants": [p["gamerTag"] for p in players],
            "sets": sets_by_player
        }
