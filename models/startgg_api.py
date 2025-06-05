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
                print(f"Request Status: {status_code}")  # Muestra el código de estado
                if status_code != 200:
                    print("Request failed, retrying...")  # Si la solicitud falla, muestra un mensaje
                    time.sleep(1)  # Espera antes de reintentar
            except Exception as e:
                print(f"Error during request: {e}")
                time.sleep(1)  # Espera antes de reintentar
        print("Request successful!")
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
              images {
                url  # Obtiene la URL de la imagen de portada
              }
            }
            startAt
          }
        }
        """
        print(f"Fetching event information for slug: {slug}")  # Debugging: Imprimir slug
        response = self.safe_post(query, {"slug": slug})
        data = response.json()
        print(f"Event Data: {data}")  # Debugging: Imprimir los datos recibidos de la API
        
        try:
            event = data["data"]["event"]
            if not event:
                raise Exception("Evento no encontrado")
            return {
                "event_id": event["id"],
                "tournament_name": event["tournament"]["name"],
                "startAt": event["startAt"],  # Fecha de inicio del torneo
                "image_url": event["tournament"]["images"][0]["url"] if event["tournament"]["images"] else None,  # URL de la imagen del torneo
            }
        except Exception:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

    def get_participants_with_ids(self, event_id):
        query = """
        query EventEntrants($eventId: ID!, $page: Int!, $perPage: Int!) {
          event(id: $eventId) {
            entrants(query: {page: $page, perPage: $perPage}) {
              pageInfo {
                totalPages
              }
              nodes {
                participants {
                  gamerTag
                  player {
                    id
                  }
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
            print(f"Fetching participants: Page {page}")  # Debugging: Imprimir la página que se está buscando
            response = self.safe_post(query, variables)
            data = response.json()
            print(f"Participants Data: {data}")  # Debugging: Imprimir los datos recibidos de la API

            for entrant in data["data"]["event"]["entrants"]["nodes"]:
                for p in entrant["participants"]:
                    players.append({
                        "gamerTag": p["gamerTag"],
                        "playerId": p["player"]["id"]
                    })

            total_pages = data["data"]["event"]["entrants"]["pageInfo"]["totalPages"]
            print(f"Total Pages: {total_pages}")  # Debugging: Imprimir el número total de páginas
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
                  tournament {
                    name
                    startAt
                  }
                }
              }
              pageInfo {
                totalPages
              }
            }
          }
        }
        """
        pages_to_fetch = 2  # Número de páginas a obtener
        sets = []

        # Itera por las primeras 2 páginas
        for page in range(1, pages_to_fetch + 1):
            variables = {"playerId": player_id, "pagenum": page}
            print(f"Fetching sets for player {player_id}: Page {page}")  # Debugging: Imprimir el jugador y la página
            response = self.safe_post(query, variables)
            data = response.json()
            print(f"Player Sets Data: {data}")  # Debugging: Imprimir los datos recibidos de la API

            player_data = data.get("data", {}).get("player")
            if not player_data or "sets" not in player_data:
                print(f"No sets found for player {player_id}.")  # Debugging: Si no hay sets, lo notificamos
                return []  # Si no hay sets, retornamos una lista vacía

            player_sets = player_data["sets"]
            for set_data in player_sets["nodes"]:
                if set_data["event"]["tournament"]["name"] == tournament_name:
                    sets.append({
                        "displayScore": set_data["displayScore"],
                        "event": set_data["event"]["name"],
                        "tournament": set_data["event"]["tournament"]["name"]
                    })

        return sets
