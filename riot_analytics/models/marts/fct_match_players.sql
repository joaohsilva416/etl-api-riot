-- unindo as bases de dados
select
    matches.id_partida,
    matches.duracao_partida,
    matches.modo_jogo,
    players.id_jogador,
    players.nome_jogador,
    players.nome_campeao,
    case
        when players.mortes = 0 then ROUND((players.abates + players.assistencias), 2)
        else ROUND((players.abates + players.assistencias) / players.mortes, 2)
    end as kda,
    players.abates,
    players.mortes,
    players.assistencias,
    players.dano_total_campeoes,
    players.ouro_total
from
    {{ref('stg_players')}} as players
left join {{ref('stg_matches')}} as matches
on players.id_partida = matches.id_partida