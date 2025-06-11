import requests
import time

class IGDBClient:
    AUTH_URL = "https://id.twitch.tv/oauth2/token"
    API_URL = "https://api.igdb.com/v4/games"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = 0  # timestamp da expiração

        self.autenticar()

    def autenticar(self):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(self.AUTH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        self.token_expiry = time.time() + data["expires_in"] - 60  # renovar 1 min antes

    def _headers(self):
        if not self.access_token or time.time() >= self.token_expiry:
            self.autenticar()
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
        }

    def buscar_jogos(self, nome_jogo, limite=10):
        headers = self._headers()

        query = f'''
        search "{nome_jogo}";
        fields name,genres.name,first_release_date,platforms.name,summary;
        limit {limite};
        '''

        response = requests.post(self.API_URL, headers=headers, data=query)
        response.raise_for_status()
        return response.json()