from models.tournament_model import StartGGApi

class TournamentService:
    def __init__(self):
        self.api = StartGGApi()

    def get_event_info(self, slug):
        return self.api.get_event_info(slug)

    def get_participants_with_sets(self, slug):
        event_info = self.get_event_info(slug)
        event_id = event_info["event_id"]
        tournament_name = event_info["tournament_name"]

        players = self.api.get_participants_with_ids(event_id)
        sets_by_player = {}

        for player in players:
            try:
                sets = self.api.get_sets_for_player_in_tournament(player["playerId"], tournament_name)
                sets_by_player[player["gamerTag"]] = sets
            except Exception as e:
                sets_by_player[player["gamerTag"]] = [{"error": str(e)}]

        return {
            "participants": players,
            "sets": sets_by_player
        }