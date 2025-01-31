from asyncio import sleep
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING
from discord import File, Interaction

from io import BytesIO

from utils.general import generate_string, get_time
from utils.discord import BaseView, BaseEmbed, Messenger
from database import duel_queries
from orz_modules.duel import DuelStatus
from utils import image_handling as imgh

if TYPE_CHECKING:
    from codeforces.models import CFProblem
    from orz_modules.user import User


class B3Duel:
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
            "rating": rating
        }
        duel = cls(duel_data)
        await duel_queries.create_b3_duel(duel)
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
        self.progress: List[str] = duel_data["progress"]

        self.first_solve: Optional[int] = None
        self.last_solved_coords: Optional[int] = None

        self.rating: int = duel_data["rating"]
        self.problems: List[str] = duel_data["problems"]
        self.problems_loaded: List["CFProblem"] = duel_data.get("problems_loaded", [])

        self.tournament_id: Optional[str] = duel_data.get("tournament_id")

    async def load_players(self):
        from orz_modules.user import User

        self.player1_loaded = await User.load_user(self.player1)
        self.player2_loaded = await User.load_user(self.player2)

        await self.player1_loaded.load_disc_user()
        await self.player2_loaded.load_disc_user()
    
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

        self.first_solve = None
        self.last_solved_coords = None
        self.progress = ["~"] * len(self.problems_loaded)
        for time, problem, idx, player in timeline:
            if self.progress[idx] != "~":
                continue
            if time > self.end_time:
                self.status = DuelStatus.TIMED_OUT.value
                break
            self.first_solve = self.first_solve or player
            self.progress[idx] = f"{player}~{time}"
            self.last_solved_coords = idx
            self.update_board_status()
            if self.status != DuelStatus.ONGOING.value:
                self.end_time = time
                break

        if self.status == DuelStatus.ONGOING.value and get_time() > self.end_time:
            self.status = DuelStatus.TIMED_OUT.value

        await self.save_state()


    def get_board(self) -> List[Tuple[int, int]]:
        board = [(0, 0)] * 3
        for i, progress in enumerate(self.progress):
            if progress != "~":
                player = tuple(map(int, progress.split("~")))
                board[i] = player  # type: ignore
        return board
    
    def update_board_status(self):
        board = self.get_board()
        self.winner = None
        player1_count = 0
        player2_count = 0
        for i in range(3):
            if board[i][0] == self.player1:
                player1_count += 1
            elif board[i][0] == self.player2:
                player2_count += 1

        if player1_count == 2:
            self.status = DuelStatus.FINISHED.value
            self.winner = self.player1
            return
        if player2_count == 2:
            self.status = DuelStatus.FINISHED.value
            self.winner = self.player2
            return

        self.status = DuelStatus.ONGOING.value


    async def _get_player1_img(self) -> BytesIO:
        assert self.player1_loaded is not None
        assert self.player1_loaded.disc_user is not None
        player1_img = await self.player1_loaded.disc_user.display_avatar.read()
        return BytesIO(player1_img)

    async def _get_player2_img(self) -> BytesIO:
        assert self.player2_loaded is not None
        assert self.player2_loaded.disc_user is not None
        player2_img = await self.player2_loaded.disc_user.display_avatar.read()
        return BytesIO(player2_img)
    
    async def get_board_img(self) -> BytesIO:
        move_locations = [(100, 100), (400, 100), (700, 100)]
        move_size = (200, 200)

        player1_img = imgh.load_image(await self._get_player1_img())
        player1_img = imgh.extract_frames(player1_img)
        player1_img = [imgh.resize(img, move_size) for img in player1_img]

        player2_img = imgh.load_image(await self._get_player2_img())
        player2_img = imgh.extract_frames(player2_img)
        player2_img = [imgh.resize(img, move_size) for img in player2_img]

        board_img = imgh.load_image_from_path("bin/b3_board.png")
        board_img = imgh.extract_frames(board_img)
        layers = [board_img]
        layers_coords = [(0, 0)]
        
        board = self.get_board()
        for i in range(3):
            if board[i][0] == 0:
                continue
            player_img = player1_img if board[i][0] == self.player1 else player2_img
            layers.append(player_img)
            layers_coords.append(move_locations[i])
        
        return imgh.stack_and_animate(layers, layers_coords=layers_coords)
    
    async def save_state(self):
        await duel_queries.save_b3_duel(self)


class B3DuelView(BaseView):
    @classmethod
    async def send_view(cls, duel: B3Duel):
        view = cls(duel)
        await view._send_view()

    def __init__(self, duel: B3Duel):
        self.duel = duel
        super().__init__(
            users=[self.duel.player1, self.duel.player2],
            timeout=60 * self.duel.time_limit + 300,
        )

    def _add_items(self):
        self.clear_items()

        if self.duel.status == DuelStatus.ONGOING.value:
            self._add_button(label="REFRESH", custom_id="refresh", row=3)

    async def _button_clicked(self, interaction: Interaction, custom_id: str) -> None:
        await interaction.response.defer()

        if custom_id == "refresh":
            await self._send_refreshing_duel_dropdown()
            await self.refresh_duel()
            return

        else:
            raise ValueError(f"Invalid custom_id: {custom_id}")
    
    async def _send_refreshing_duel_dropdown(self):
        self.clear_items()
        self._add_text_dropdown("Refreshing . . .")
        self._active_msg = await Messenger.send_message_no_reset(view=self)
        self._release_lock()

    async def refresh_duel(self) -> None:
        await sleep(10)
        await self.duel.refresh_duel()
        if self.duel.status == DuelStatus.TIMED_OUT.value:
            await self.stop_and_disable(custom_text="Time's up!")
            return
        await self._send_view()
        if self.duel.status == DuelStatus.FINISHED.value:
            self.stop()

    async def _get_embed(self):
        embed = BaseEmbed(title="B3 Duel")
        if self.duel.status != DuelStatus.ONGOING.value:
            embed.add_field(name="")
            if self.duel.status == DuelStatus.FINISHED.value:
                embed.add_field(name="Winner 👑", value=f"<@{self.duel.winner}>")
            else:
                raise ValueError(f"Invalid status: {self.duel.status}")
            embed.add_field(name="")
        from datetime import datetime

        embed.timestamp = datetime.fromtimestamp(self.duel.start_time)
        embed.add_field(name="Player 1", value=f"<@{self.duel.player1}>")
        embed.add_field(name="Rating", value=f"{self.duel.rating}")
        embed.add_field(name="Player 2", value=f"<@{self.duel.player2}>")
        embed.add_field(
            name="",
            value=(
                f"**Duration:** {self.duel.time_limit} mins\n"
                f"**Start:** <t:{self.duel.start_time}:t> \\~\\~ <t:{self.duel.start_time}:R>\n"
                f"**End:** <t:{self.duel.end_time}:t> \\~\\~ <t:{self.duel.end_time}:R>"
            ),
            inline=False,
        )
        embed.add_field(name="x - > - o - < - x", inline=False)
        board = self.duel.get_board()
        for i in range(3):
            problem = self.duel.problems_loaded[i]
            value = f"**{i + 1}. [{problem.contestId}-{problem.index}]({problem.link})**"
            if board[i][0] != 0:
                time_taken = (board[i][1] - self.duel.start_time) // 60
                value += f"by <@{board[i][0]}> @ {time_taken} mins"
            else:
                value += "by **~ ~ ~**"
            embed.add_field(name="", value=value)

        board_img = await self.duel.get_board_img()
        board_img = File(board_img, "board.gif")
        files: List[File] = [board_img]
        return embed, files
