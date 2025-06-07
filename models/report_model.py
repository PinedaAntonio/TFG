import requests
import time

API_URL = "https://api.start.gg/gql/alpha"
API_TOKEN = "Bearer e8099de98407f34dc9f65f5b79af4e92"
HEADERS = {"Authorization": API_TOKEN, "Content-Type": "application/json"}


class ReportModel:

    def safe_post(self, query, variables):
        status_code = None
        response = None
        while status_code != 200:
            try:
                response = requests.post(API_URL, headers=HEADERS, json={"query": query, "variables": variables})
                status_code = response.status_code
                if status_code != 200:
                    print(f"Request failed with status {status_code}, retrying...")
                    time.sleep(1)
            except Exception as e:
                print(f"Error during request: {e}")
                time.sleep(1)
        return response

    def get_event_id(self, slug):
        query = """
        query getEventId($slug: String) { event(slug: $slug) { id } }
        """
        variables = {"slug": slug}
        response = self.safe_post(query, variables)
        data = response.json()
        return data['data']['event']['id']

    def get_all_players(self, idtorneo):
        query = """
        query EventEntrants($eventId: ID!, $page: Int!, $perPage: Int!) {
          event(id: $eventId) {
            entrants(query: { page: $page, perPage: $perPage }) {
              nodes {
                participants { id gamerTag player { id } }
              }
            }
          }
        }
        """
        variables = {"eventId": idtorneo, "page": 1, "perPage": 150}
        response = self.safe_post(query, variables)
        data = response.json()

        playersarr = []
        for node in data['data']['event']['entrants']['nodes']:
            for player in node['participants']:
                playersarr.append(player)
        return playersarr

    def get_sets_for_player(self, player_id):
        query = """
        query Sets($playerId: ID!, $page: Int!) {
          player(id: $playerId) {
            sets(perPage: 50, page: $page) {
              nodes {
                displayScore
                slots {
                  entrant { participants { player { id gamerTag } } }
                }
                event { name tournament { name startAt } videogame { id } }
              }
              pageInfo { totalPages }
            }
          }
        }
        """

        all_sets = []
        page = 1
        pages_to_fetch = 2  # máximo de páginas a consultar

        while page <= pages_to_fetch:
            variables = {"playerId": player_id, "page": page}
            response = self.safe_post(query, variables)
            data = response.json()

            sets = data['data']['player']['sets']['nodes']
            all_sets.extend(sets)

            total_pages = data['data']['player']['sets']['pageInfo']['totalPages']

            if page >= total_pages:
                break

            page += 1
            time.sleep(0.5)

        return all_sets
