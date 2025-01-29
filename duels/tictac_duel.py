from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING

from discord import File, Interaction

from utils.general import generate_string, get_time
from utils.discord import BaseView, BaseEmbed
from database import duel_queries
from orz_modules.duel import DuelStatus

if TYPE_CHECKING:
    from codeforces.models import CFProblem
    from orz_modules.user import User


class TicTacDuel:
    @classmethod
    async def create_duel(
        cls,
        player1: int,
        player2: int,
        problems_loaded: List["CFProblem"],
        rating: int,
        time_limit: int,
    ):
        start_time = get_time()
        duel_data: Dict[str, Any] = {
            "duel_id": generate_string(16),
            "player1": player1,
            "player2": player2,
            "start_time": start_time,
            "time_limit": time_limit,
            "end_time": start_time + time_limit * 60,
            "status": DuelStatus.ONGOING.value,
            "problems": [
                f"{problem.contestId}~{problem.index}" for problem in problems_loaded
            ],
            "progress": ["~"] * len(problems_loaded),
            "problems_loaded": problems_loaded,
            "rating": rating,
        }
        duel = cls(duel_data)
        await duel_queries.create_tictac_duel(duel)
        await duel.load_players()
        return duel

    def __init__(self, duel_data: Dict[str, Any]):
        self.duel_id: str = duel_data["duel_id"]

        self.player1: int = duel_data["player1"]
        self.player2: int = duel_data["player2"]

        self.player1_loaded: Optional["User"] = None
        self.player2_loaded: Optional["User"] = None

        self.start_time: int = duel_data["start_time"]
        self.time_limit: int = duel_data["time_limit"]
        self.end_time: int = duel_data["end_time"]

        self.status: str = duel_data["status"]
        self.winner: Optional[int] = duel_data.get("winner")
        self.first_solve: Optional[int] = None
        self.progress: List[str] = duel_data["progress"]

        self.rating: int = duel_data["rating"]
        self.problems: List[str] = duel_data["problems"]
        self.problems_loaded: List["CFProblem"] = duel_data.get("problems_loaded", [])

        self.tournament_id: Optional[str] = duel_data.get("tournament_id")

    async def load_players(self):
        from orz_modules.user import User

        self.player1_loaded = await User.load_user(self.player1)
        self.player2_loaded = await User.load_user(self.player2)

    async def refresh_duel(self):
        from codeforces.cf import get_user_problems_status, Verdict

        assert self.player1_loaded is not None
        assert self.player1_loaded.cf_handle is not None
        assert self.player2_loaded is not None
        assert self.player2_loaded.cf_handle is not None

        player1_progress = get_user_problems_status(
            self.player1_loaded.cf_handle, self.problems_loaded, self.start_time
        )
        player2_progress = get_user_problems_status(
            self.player2_loaded.cf_handle, self.problems_loaded, self.start_time
        )

        timeline: List[Tuple[int, "CFProblem", int, int]] = (
            []
        )  # time, problem, idx, player
        for i, problem in enumerate(self.problems_loaded):
            for time, verdict in player1_progress[problem]:
                if verdict == Verdict.OK.value:
                    timeline.append((time, problem, i, self.player1))
                    break
            for time, verdict in player2_progress[problem]:
                if verdict == Verdict.OK.value:
                    timeline.append((time, problem, i, self.player2))
                    break
        timeline.sort(key=lambda x: x[0])

        row = [0] * 3
        col = [0] * 3
        diag = [0] * 2
        self.first_solve = None
        self.progress = ["~"] * len(self.problems_loaded)
        for time, problem, idx, player in timeline:
            if self.progress[idx] != "~":
                continue
            if time > self.end_time:
                self.status = DuelStatus.TIMED_OUT.value
                break
            self.first_solve = self.first_solve or player
            self.progress[idx] = f"{player}~{time}"
            x, y = divmod(idx, 3)
            row[x] += 1
            col[y] += 1
            if x == y:
                diag[0] += 1
            if x + y == 2:
                diag[1] += 1
            if row[x] == 3 or col[y] == 3 or diag[0] == 3 or diag[1] == 3:
                self.winner = player
                self.status = DuelStatus.FINISHED.value
                self.end_time = time
                break
        
        if self.status != DuelStatus.FINISHED.value and get_time() > self.end_time:
            self.status = DuelStatus.TIMED_OUT.value
        
        await self.save_state()

    def get_board(self) -> List[List[Tuple[int, int]]]:
        board = [[(0, 0)] * 3 for _ in range(3)]
        for i, progress in enumerate(self.progress):
            if progress != "~":
                player = tuple(map(int, progress.split("~")))
                x, y = divmod(i, 3)
                board[x][y] = player  # type: ignore
        return board
    
    async def save_state(self):
        await duel_queries.save_tictac_duel(self)


class TickTacDuelView(BaseView):
    @classmethod
    async def send_view(cls, duel: TicTacDuel):
        view = cls(duel)
        await view._send_view()

    def __init__(self, duel: TicTacDuel):
        self.duel = duel
        super().__init__(users=[self.duel.player1, self.duel.player2], timeout=60 * 60)

    def _add_items(self):
        self.clear_items()

        board = self.duel.get_board()
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                problem = self.duel.problems_loaded[idx]
                if board[i][j][0] == 0:
                    self._add_url_button(
                        label=f"{idx + 1}",
                        url=problem.link,
                        row=i,
                    )
                else:
                    emoji = "❌" if self.duel.first_solve == board[i][j][0] else "⭕"
                    self._add_url_button(
                        label=emoji,
                        url=problem.link,
                        row=i,
                    )

        if self.duel.status != DuelStatus.FINISHED.value:
            self._add_button(label="REFRESH", custom_id="refresh", row=3)

    async def _button_clicked(self, interaction: Interaction, custom_id: str) -> None:
        await interaction.response.defer()

        if custom_id == "refresh":
            await self.refresh_duel()
            return

        else:
            raise ValueError(f"Invalid custom_id: {custom_id}")

    async def refresh_duel(self) -> None:
        await self.duel.refresh_duel()
        if self.duel.status == DuelStatus.TIMED_OUT.value:
            await self.stop_and_disable(custom_text="Time's up!")
            return
        await self._send_view()
        if self.duel.status == DuelStatus.FINISHED.value:
            self.stop()

    async def _get_embed(self):
        embed = BaseEmbed(title="TicTac Duel")
        if self.duel.status == DuelStatus.FINISHED.value:
            embed.add_field(name="")
            embed.add_field(name="Winner 👑", value=f"<@{self.duel.winner}>")
            embed.add_field(name="")
        from datetime import datetime

        embed.timestamp = datetime.fromtimestamp(self.duel.start_time)
        embed.add_field(name="Player 1", value=f"<@{self.duel.player1}>")
        embed.add_field(name="Rating", value=f"{self.duel.rating}")
        embed.add_field(name="Player 2", value=f"<@{self.duel.player2}>")
        embed.add_field(name="Start Time", value=f"<t:{self.duel.start_time}:R>")
        embed.add_field(name="Duration", value=f"{self.duel.time_limit} minutes")
        embed.add_field(name="End Time", value=f"<t:{self.duel.end_time}:R>")
        embed.add_field(name="x - > - o - < - x", inline=False)
        board = self.duel.get_board()
        for i in range(3):
            for j in range(3):
                value = "**~ ~ ~ ~**"
                if board[i][j][0] != 0:
                    value = f"<t:{board[i][j][1]}:R>\n<@{board[i][j][0]}>"
                embed.add_field(name=f"Problem {i * 3 + j + 1}", value=value)

        files: List[File] = []
        return embed, files
