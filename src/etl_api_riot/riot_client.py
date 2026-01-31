# Importando as libs
import requests
from dotenv import load_dotenv
import os
import time
import json
import snowflake.connector

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
        endpoint = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}" # Define o endpoint
        value = self._make_request(endpoint)['puuid'] # Pega apenas o puuid
        
        return value
    
    # Função para pegar os id's das partidas
    def get_matches(self, puuid, count=20):
        endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids" # Define o endpoint
        value = self._make_request(endpoint, params={"count": count}) # Pega as 20 últimas id's

        return value
    
    # Função para pegar as informações das partidas
    def get_match_details(self, match_id):
        endpoint = f"/lol/match/v5/matches/{match_id}"
        value = self._make_request(endpoint)

        return value
    
# classe para conectar e salvar dados no SnowFlake
class SnowFlakeLoader():
    def __init__(self):
        # Lendo as informações de login das variáveis de ambiente
        self.account = os.getenv("ACCOUNT")
        self.user = os.getenv("USER")
        self.password = os.getenv("PASSWORD")
        self.role = os.getenv("ROLE")
        self.warehouse = os.getenv("WAREHOUSE")
        self.database = os.getenv("DATABASE")
        self.schema = os.getenv("SCHEMA")
    
    # Função para conectar no snowflake
    def connect_to_snowflake(self):
        return snowflake.connector.connect(
            account = self.account,
            user = self.user,
            password = self.password,
            role = self.role,
            warehouse = self.warehouse,
        )
    
    # Função para criar a tabela
    def create_table(self):
        conn = self.connect_to_snowflake()
        cursor = conn.cursor()

        # Criando e usando database
        cursor.execute("CREATE DATABASE IF NOT EXISTS RIOT_DB")
        cursor.execute("USE DATABASE RIOT_DB")

        # Criando e usando schema
        cursor.execute("CREATE SCHEMA IF NOT EXISTS PUBLIC")
        cursor.execute("USE SCHEMA RIOT_DB.PUBLIC")

        # Criando a tabela
        query = cursor.execute("""
                        CREATE TABLE IF NOT EXISTS MATCHES_RAW(
                               MATCH_ID VARCHAR(50) PRIMARY KEY,
                               MATCH_DATA VARIANT,
                               CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP())
        """)

        # Encerrando conexão
        cursor.close()
        conn.close()
    
    def load_data(self, match_results):
        conn = self.connect_to_snowflake()
        cursor = conn.cursor()
        try:
            # Usando database e schema
            cursor.execute("USE DATABASE RIOT_DB")
            cursor.execute("USE SCHEMA RIOT_DB.PUBLIC")

            # for loop para percorrer cada partida
            for match in match_results:
                try:
                    # Pegamos o ID de dentro do JSON
                    match_id = match['metadata']['matchId']

                    # Transformamos o dict em string JSON para enviar
                    match_json_str = json.dumps(match)

                    # Query de Insert usando PARSE_JSON
                    # Usamos %s para evitar SQL Injection (bind variable)
                    sql = "INSERT INTO MATCHES_RAW (MATCH_ID, MATCH_DATA) SELECT %s, PARSE_JSON(%s)"

                    cursor.execute(sql, (match_id, match_json_str))
                except KeyError:
                    print(f"Erro: Partida sem ID encontrado. Pulando...")
                except Exception as e:
                    print(f"Erro ao inserir partida {match_id}: {e}")
                    
            conn.commit() # Confirma a transação
            print("Commit realizado com sucesso!")
        finally:
            cursor.close()
            conn.close()
        
def main():
    client = RiotClient()

    try:
        # Pegar PUUID
        my_puuid = client.get_puuid("kojiii", "00000")

        # Pegar Lista de Partidas
        matches_ids = client.get_matches(my_puuid)

        # Loop de Download
        results = []

        print("Iniciando download das partidas...")
        
        for match_id in matches_ids:
            dados = client.get_match_details(match_id)
            results.append(dados)
            time.sleep(1) # Respeitando a API
            
        print(f"Sucesso! Detalhes baixados.")

        # Salvar Arquivo
        print("Salvando arquivo Json...")
        with open("matches_raw.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
            
        print("Arquivo salvo com sucesso.")

        print("Iniciando carga no Snowflake...")
        loader = SnowFlakeLoader()
        loader.create_table() # Garante que a tabela existe
        loader.load_data(results) # Carrega os dados para o snowflake
        print("Carga concluída!")

    except Exception as e:
        print(f"Erro no processo: {e}")

if __name__ == "__main__":
    main()