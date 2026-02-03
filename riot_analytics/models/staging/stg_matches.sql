-- Importando os dados
with source as (
    select
        MATCH_DATA
    from
        {{source('RIOT_DB', 'MATCHES_RAW')}}
),

-- renamed: Inserir todas as transformações
renamed as (
    select
        MATCH_DATA:info:gameId::INTEGER as id_partida,
        TO_TIMESTAMP(MATCH_DATA:info:gameCreation::NUMBER / 1000) as data_inicio_partida,
        MATCH_DATA:info:gameDuration::INTEGER as duracao_partida,
        MATCH_DATA:info:gameMode::VARCHAR as modo_jogo,
        MATCH_DATA:info:gameVersion::VARCHAR as versao_jogo
    from
        source
)

-- final: select final
select * from renamed