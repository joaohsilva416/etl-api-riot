# Importando as libs
import requests
from dotenv import load_dotenv
import os
import time
import json

# Carrega as configurações do arquivo .env
load_dotenv()

class RiotClient():
    def __init__(self):
        self.api_key = os.getenv("RIOT_API_KEY") # Lendo a api key
        self.url_base = "https://americas.api.riotgames.com" # Define a url base
        self.headers = {
             "X-Riot-Token": self.api_key # Cria o header
        }
    
    # Função para pegar o site
    def _make_request(self, endpoint, params=None):
        url_full = f'{self.url_base}{endpoint}' # Concatena url base com endpoint
        response = requests.get(url_full, params=params, headers=self.headers) # Requisição do site
        data = response.json() # Armazena a resposta em um json

        # Verifica se o status code é diferente de 200
        if response.status_code != 200:
            # Interrompe o código caso erro for detectado
            raise Exception(f"{response.status_code} - {data}")
        
        return data
    
    # Função para pegar o puuid
    def get_puuid(self, game_name, tag_line):
        endpoint = f'/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}' # Define o endpoint
        value = self._make_request(endpoint)['puuid'] # Pega apenas o puuid
        
        return value
    
    # Função para pegar os id's das partidas
    def get_matches(self, puuid, count=20):
        endpoint = f'/lol/match/v5/matches/by-puuid/{puuid}/ids' # Define o endpoint
        value = self._make_request(endpoint, params={"count": count}) # Pega as 20 últimas id's

        return value
    
    # Função para pegar as informações das partidas
    def get_match_details(self, match_id):
        endpoint = f'/lol/match/v5/matches/{match_id}'
        value = self._make_request(endpoint)

        return value
    
def main():
    client = RiotClient()

    try:
        # Pegar PUUID
        my_puuid = client.get_puuid("kojiii", "00000")

        # Pegar Lista de Partidas
        matches_ids = client.get_matches(my_puuid)

        # 3. Loop de Download
        results = []

        print("Iniciando download das partidas...")
        
        for match_id in matches_ids:
            dados = client.get_match_details(match_id)
            results.append(dados)
            time.sleep(1) # Respeitando a API
            
        print(f"Sucesso! Detalhes baixados.")

        # 4. Salvar Arquivo
        print("Salvando arquivo Json...")
        with open('matches_raw.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
            
        print("Arquivo salvo com sucesso.")

    except Exception as e:
        print(f"Erro no processo: {e}")

if __name__ == '__main__':
    main()