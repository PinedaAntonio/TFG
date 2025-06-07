import requests
from fastapi import HTTPException

API_URL = "https://api.start.gg/gql/alpha"
API_TOKEN = "Bearer e8099de98407f34dc9f65f5b79af4e92"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

class PlayerModel:

    def safe_post(self, query, variables):
        status_code = None
        response = None
        while status_code != 200:
            try:
                response = requests.post(API_URL, headers=HEADERS, json={"query": query, "variables": variables})
                status_code = response.status_code
            except Exception as e:
                print(f"Error during request: {e}")
                continue
        return response

    def get_player_sets(self, player_id):
      query = """
      query Sets($playerId: ID!, $pagenum: Int) {
        player(id: $playerId) {
          gamerTag
          user {
            images {
              url
              type
            }
          }
          sets(perPage: 50, page: $pagenum) {
            nodes {
              id
              displayScore
              event {
                name
                videogame { id }
                tournament { name startAt }
              }
              slots {
                entrant {
                  name
                  participants {
                    player { id }
                  }
                }
              }
            }
            pageInfo { totalPages }
          }
        }
      }
      """
      pages_to_fetch = 2
      sets = []
      gamerTag = None
      profileImage = None

      for page in range(1, pages_to_fetch + 1):
          variables = {"playerId": player_id, "pagenum": page}
          response = self.safe_post(query, variables)
          data = response.json()

          player_data = data.get("data", {}).get("player")
          if not player_data or "sets" not in player_data:
              return [], None, None

          if gamerTag is None:
              gamerTag = player_data["gamerTag"]

              # Extraer el profileImage
              user = player_data.get("user")
              if user and "images" in user:
                  for img in user["images"]:
                      if img["type"] == "profile":
                          profileImage = img["url"]
                          break

          player_sets = player_data["sets"]
          for set_data in player_sets["nodes"]:
              try:
                  if set_data["event"]["videogame"]["id"] != 1386:
                      continue

                  slots = set_data.get("slots", [])
                  if len(slots) != 2:
                      continue

                  display_score = set_data.get("displayScore", "")
                  score_parts = display_score.replace(" ", "").split("-")

                  if len(score_parts) != 2:
                      continue

                  try:
                      p1_score = int(score_parts[0][-1])
                      p2_score = int(score_parts[1][-1])
                  except ValueError:
                      continue

                  sets.append({
                      "player1_id": slots[0]["entrant"]["participants"][0]["player"]["id"],
                      "player1_name": slots[0]["entrant"]["name"],
                      "player1_score": p1_score,
                      "player2_id": slots[1]["entrant"]["participants"][0]["player"]["id"],
                      "player2_name": slots[1]["entrant"]["name"],
                      "player2_score": p2_score,
                      "event": set_data["event"]["name"],
                      "tournament": set_data["event"]["tournament"]["name"],
                      "date": set_data["event"]["tournament"]["startAt"]
                  })

              except Exception as e:
                  print(f"Exception while processing set: {e}")

      return sets, gamerTag, profileImage


    def calculate_stats(self, sets, player_id):
        victories = []
        total_sets = len(sets)

        for s in sets:
            p1_score = s["player1_score"]
            p2_score = s["player2_score"]
            p1_id = s["player1_id"]
            p2_id = s["player2_id"]

            if p1_id == player_id and p1_score > p2_score:
                victories.append(s)
            elif p2_id == player_id and p2_score > p1_score:
                victories.append(s)

        winrate = round((len(victories) / total_sets) * 100, 2) if total_sets > 0 else 0
        return {
            "total_sets": total_sets,
            "victories": len(victories),
            "winrate": winrate
        }
