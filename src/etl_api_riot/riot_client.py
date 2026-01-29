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
    
    