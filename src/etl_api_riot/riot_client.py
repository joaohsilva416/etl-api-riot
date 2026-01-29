# Importando as libs
import requests
from dotenv import load_dotenv
import os

class RiotClient():
    def __init__(self):
        # Carrega as configurações do arquivo .env
        load_dotenv()

        self.api_key = os.getenv("RIOT_API_KEY") # Lendo a api key
        self.url_base = "https://americas.api.riotgames.com" # Define a url base
        self.headers = {
             "X-Riot-Token": self.api_key # Cria o header
        }
    
    # Função para pegar o site
    def _make_request(self, endpoint):
        url_completa = f'{self.url_base}{endpoint}' # Concatena url base com endpoint
        response = requests.get(url_completa, headers=self.headers) # Requisição do site
        data = response.json() # Armazena a resposta em um json

        # Verifica se o status code é diferente de 200
        if response.status_code != 200:
            # Interrompe o código caso erro for detectado
            raise Exception(f"{response.status_code} - {data}")
        
        return data
    
    # Função para pegar o puuid
    def get_puuid(self, game_name, tag_line):
        endpoint = f'/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}' # Define o endpoint
        valor = self._make_request(endpoint)['puuid'] # Pega apenas o puuid
        
        return valor