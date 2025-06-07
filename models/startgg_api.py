import requests
import time
from fastapi import HTTPException

API_URL = "https://api.start.gg/gql/alpha"
API_TOKEN = "Bearer e8099de98407f34dc9f65f5b79af4e92"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

class StartGGApi:

    def safe_post(self, query, variables):
        status_code = None
        response = None
        while status_code != 200:
            try:
                response = requests.post(API_URL, headers=HEADERS, json={"query": query, "variables": variables})
                status_code = response.status_code
                time.sleep(0.3)
            except Exception as e:
                print(f"Error during request: {e}")
                time.sleep(1)
        return response

    def get_event_info(self, slug):
        query = """
        query getEvent($slug: String) {
          event(slug: $slug) {
            id
            name
            tournament {
              name
              startAt
              images { url }
            }
            startAt
          }
        }
        """
        response = self.safe_post(query, {"slug": slug})
        data = response.json()
        
        try:
            event = data["data"]["event"]
            if not event:
                raise Exception("Evento no encontrado")
            return {
                "event_id": event["id"],
                "tournament_name": event["tournament"]["name"],
                "startAt": event["startAt"],
                "image_url": event["tournament"]["images"][0]["url"] if event["tournament"]["images"] else None
            }
        except Exception:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

    def get_participants_with_ids(self, event_id):
        query = """
        query EventEntrants($eventId: ID!, $page: Int!, $perPage: Int!) {
          event(id: $eventId) {
            entrants(query: {page: $page, perPage: $perPage}) {
              pageInfo { totalPages }
              nodes {
                participants {
                  gamerTag
                  player { id }
                }
              }
            }
          }
        }
        """
        page = 1
        per_page = 100
        players = []

        while True:
            variables = {"eventId": event_id, "page": page, "perPage": per_page}
            response = self.safe_post(query, variables)
            data = response.json()

            for entrant in data["data"]["event"]["entrants"]["nodes"]:
                for p in entrant["participants"]:
                    players.append({
                        "gamerTag": p["gamerTag"],
                        "playerId": p["player"]["id"]
                    })

            total_pages = data["data"]["event"]["entrants"]["pageInfo"]["totalPages"]
            if page >= total_pages:
                break
            page += 1

        return players

    def get_sets_for_player_in_tournament(self, player_id, tournament_name):
        query = """
        query Sets($playerId: ID!, $pagenum: Int) {
          player(id: $playerId) {
            sets(perPage: 50, page: $pagenum) {
              nodes {
                id
                displayScore
                event {
                  name
                  videogame { id }
                  tournament { name startAt }
                }
                slots { entrant { name } }
              }
              pageInfo { totalPages }
            }
          }
        }
        """
        pages_to_fetch = 2
        sets = []

        for page in range(1, pages_to_fetch + 1):
            variables = {"playerId": player_id, "pagenum": page}
            response = self.safe_post(query, variables)
            data = response.json()

            player_data = data.get("data", {}).get("player")
            if not player_data or "sets" not in player_data:
                return []

            player_sets = player_data["sets"]
            for set_data in player_sets["nodes"]:
                if set_data["event"]["videogame"]["id"] != 1386:
                    continue

                if set_data["event"]["tournament"]["name"] == tournament_name:
                    display_score = set_data.get("displayScore", "")
                    score_parts = display_score.replace(" ", "").split("-")
                    
                    if len(score_parts) == 2 and len(set_data.get("slots", [])) == 2:
                        try:
                            p1_score = int(score_parts[0][-1])
                            p2_score = int(score_parts[1][-1])
                        except ValueError:
                            continue

                        sets.append({
                            "player1_name": set_data["slots"][0]["entrant"]["name"],
                            "player1_score": p1_score,
                            "player2_name": set_data["slots"][1]["entrant"]["name"],
                            "player2_score": p2_score,
                            "event": set_data["event"]["name"],
                            "tournament": set_data["event"]["tournament"]["name"]
                        })
        return sets
