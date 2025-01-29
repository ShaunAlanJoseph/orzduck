from typing import TYPE_CHECKING

from database.db import DB

if TYPE_CHECKING:
    from duels.tictac_duel import TicTacDuel


async def create_tictac_duel(duel: "TicTacDuel"):
    query = (
        "INSERT INTO duels_tictac (duel_id, player1, player2, start_time, time_limit, end_time, status, winner, rating, problems, progress, tournament_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    await DB.execute_query(
        query,
        duel.duel_id,
        duel.player1,
        duel.player2,
        duel.start_time,
        duel.time_limit,
        duel.end_time,
        duel.status,
        duel.winner,
        duel.rating,
        duel.problems,
        duel.progress,
        duel.tournament_id,
    )


async def save_tictac_duel(duel: "TicTacDuel"):
    query = "UPDATE duels_tictac SET end_time = ?, status = ?, winner = ?, progress = ? WHERE duel_id = ?"
    await DB.execute_query(
        query,
        duel.end_time,
        duel.status,
        duel.winner,
        duel.progress,
        duel.duel_id,
    )
