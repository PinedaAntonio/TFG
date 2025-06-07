from collections import defaultdict
from models.player_model import PlayerModel

class PlayerService:
    def __init__(self):
        self.model = PlayerModel()

    def get_player_stats(self, player_id):
        sets, gamerTag, profileImage = self.model.get_player_sets(player_id)

        grouped = defaultdict(list)
        for s in sets:
            grouped[s["tournament"]].append(s)

        stats = self.model.calculate_stats(sets, player_id)

        return {
            "total_sets": stats["total_sets"],
            "victories": stats["victories"],
            "winrate": stats["winrate"],
            "tournaments": grouped,
            "gamerTag": gamerTag,
            "profileImage": profileImage
        }
