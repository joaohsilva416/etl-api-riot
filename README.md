# ⚔️ Riot Games Data Pipeline (ELT)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Snowflake](https://img.shields.io/badge/snowflake-%2329B5E8.svg?style=for-the-badge&logo=snowflake&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Riot Games](https://img.shields.io/badge/Riot%20Games-EB0029?style=for-the-badge&logo=riotgames&logoColor=white)

## 📋 Sobre o Projeto
Este projeto é um pipeline **ELT (Extract, Load, Transform)** desenvolvido para extrair dados de partidas de **League of Legends** via API oficial da Riot Games. O objetivo é criar uma base analítica no Snowflake para monitorar estatísticas de jogadores.

O pipeline opera sob demanda (execução manual), priorizando a extração segura e o carregamento de dados brutos (Raw JSON) no Data Warehouse, garantindo que as transformações e limpezas sejam feitas posteriormente com **dbt Core**.

## 🏗️ Arquitetura e Fluxo
1. **Ingestion (Python Puro):** Scripts otimizados que autenticam na Riot API e iteram sobre listas de partidas (`MatchV5`).
2. **Storage (Snowflake):** Carregamento dos dados via conector nativo, salvando o payload completo em colunas do tipo `VARIANT` para preservar a estrutura original.
3. **Transformation (dbt):** Modelagem dos dados brutos, tratamento de chaves e criação de tabelas fato/dimensão.

## 🛠️ Stack Tecnológica & Bibliotecas
O projeto foi construído utilizando Python padrão e bibliotecas essenciais para manter a leveza e controle total do fluxo:

* **Linguagem:** Python 3.x
* **Requests:** Para gerenciamento das requisições HTTP (GET) junto à API da Riot.
* **Snowflake Connector:** Para conexão direta e segura com o Data Warehouse e execução de DDL/DML.
* **Python-dotenv & OS:** Gerenciamento seguro de credenciais e variáveis de ambiente (evitando hardcoding de senhas).
* **JSON:** Serialização e tratamento dos dicionários de dados antes do envio ao banco.
* **Time:** Implementação de estratégias de espera (`sleep`) para respeitar o Rate Limit da API.
* **Transformação:** dbt Core (Data Build Tool).

## 🔧 Desafios Técnicos Resolvidos

### 1. Harmonização de IDs (`br1_` Prefix)
A API da Riot retorna o `match_id` com o prefixo da região (ex: `BR1_123456`), mas logs internos podem omitir esse dado.
* **Solução:** Implementei lógica de normalização na camada de **Staging (dbt)** para padronizar as chaves, garantindo o JOIN correto entre tabelas.

### 2. Rate Limiting (Respeito à API)
A API da Riot possui limites estritos de requisições por minuto.
* **Solução:** Utilizei a biblioteca `time` com `time.sleep(1)` estratégico dentro dos loops de extração de detalhes da partida. Isso garante a integridade do processo de coleta sem bloqueios por excesso de chamadas.

### 3. Parsing de JSON no Snowflake
* **Solução:** Uso de `json.dump()` para preparar o objeto e ingestão em coluna `VARIANT` no Snowflake, permitindo que estruturas aninhadas complexas sejam "explodidas" (Flatten) via SQL/dbt posteriormente.

## 🚀 Passo a Passo para Execução

### Pré-requisitos
* Python instalado.
* Poetry instalado (`pipx install poetry`).
* Conta ativa no Snowflake (com Database e Schema criados).
* API Key da Riot Games (Development Key).

### 1. Clonar o Repositório
Abra seu terminal e clone o projeto para sua máquina local:
```bash
git clone https://github.com/joaohsilva416/etl-api-riot.git
cd etl-api-riot
```

### 2. Instalar Dependências
Instale o Poetry via pipx (de preferência) e configure as dependências do projeto:
```bash
pipx install poetry
poetry install
```
Configure o dbt e instale as dependências usando:
```bash
poetry run dbt deps --project-dir riot_analytics
```
E certifique-se de que o Snowflake esteja configurado para aceitar conexões do dbt e da aplicação Python.

### 3. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com suas credenciais:
```ini, toml
RIOT_API_KEY="RGAPI-sua-chave-aqui"
SNOWFLAKE_USER="seu_usuario"
SNOWFLAKE_PASSWORD="sua_senha"
SNOWFLAKE_ACCOUNT="sua_conta"
SNOWFLAKE_WAREHOUSE="seu_warehouse"
SNOWFLAKE_DATABASE="seu_db"
SNOWFLAKE_SCHEMA="seu_schema"
```

### 4. Executar a Extração
Utilize poetry run apontando para o caminho do módulo de extração:
```bash
poetry run python src/etl_api_riot/riot_client.py
```

### 5. Executar as Transformações (dbt)
A execução segue a ordem lógica de dependências (Staging -> Marts):
1. Staging Matches:
```bash
poetry run dbt run --select riot_analytics/models/staging/stg_matches.sql
```

2. Staging Players:
```bash
poetry run dbt run --select riot_analytics/models/staging/stg_players.sql
```

3. Marts
```bash
poetry run dbt run --select riot_analytics/models/marts/fct/match_players.sql
```

*(Nota: Certifique-se de estar na raiz onde o comando consegue localizar o dbt_project.yml ou ajuste o diretório conforme necessário).*

---
Developed by **João Henrique**
