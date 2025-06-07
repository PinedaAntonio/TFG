import requests
import time

API_URL = "https://api.start.gg/gql/alpha"
API_TOKEN = "Bearer e8099de98407f34dc9f65f5b79af4e92"
HEADERS = {"Authorization": API_TOKEN, "Content-Type": "application/json"}


class SeedsModel:

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

    def get_seeds(self, idtorneo):
        query = """
        query EventEntrants($eventId: ID!, $page: Int!, $perPage: Int!) {
          event(id: $eventId) {
            entrants(query: { page: $page, perPage: $perPage }) {
              nodes {
                seeds { seedNum }
                participants {
                  gamerTag
                  player { id }
                }
              }
            }
          }
        }
        """
        variables = {"eventId": idtorneo, "page": 1, "perPage": 150}
        response = self.safe_post(query, variables)
        data = response.json()

        seeds = []
        for node in data['data']['event']['entrants']['nodes']:
            seedNum = node['seeds'][0]['seedNum']
            for participant in node['participants']:
                gamerTag = participant['gamerTag']
                seeds.append({"seedNum": seedNum, "gamerTag": gamerTag})

        # Ordenamos por seedNum
        seeds = sorted(seeds, key=lambda x: x['seedNum'])
        return seeds
