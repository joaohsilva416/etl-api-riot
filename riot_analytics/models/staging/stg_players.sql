-- Importa os dados
with source as (
    select
        *
    from
        {{source('RIOT_DB', 'MATCHES_RAW')}}
),

-- inserir transformações
renamed as (
    select
        MATCH_DATA:info:gameId::INTEGER as id_partida,
        player.value:puuid::VARCHAR as id_jogador,
        player.value:riotIdGameName::VARCHAR as nome_jogador,
        player.value:championName::VARCHAR as nome_campeao,

        -- métricas de combate
        player.value:kills::INTEGER as abates,
        player.value:deaths::INTEGER as mortes,
        player.value:assists::INTEGER as assistencias,

        -- métricas de economia e dano
        player.value:totalDamageDealtToChampions::INTEGER as dano_total_campeoes,
        player.value:goldEarned::INTEGER as ouro_total,

        -- resultado da partida
        player.value:win::BOOLEAN as vitoria
    from
        source,
        LATERAL FLATTEN(input => source.MATCH_DATA:info:participants) as player
)

-- select final
select * from renamed