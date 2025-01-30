from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING
from discord import File, Interaction
from io import BytesIO

from utils.general import generate_string, get_time
from utils.discord import BaseView, BaseEmbed
from database import duel_queries
from orz_modules.duel import DuelStatus
from utils import image_handling as imgh

if TYPE_CHECKING:
    from codeforces.models import CFProblem
    from orz_modules.user import User

WINNING_FILES = [
    [(0, 0), (0, 1), (0, 2)],  # Row 1
    [(1, 0), (1, 1), (1, 2)],  # Row 2
    [(2, 0), (2, 1), (2, 2)],  # Row 3
    [(0, 0), (1, 0), (2, 0)],  # Col 1
    [(0, 1), (1, 1), (2, 1)],  # Col 2
    [(0, 2), (1, 2), (2, 2)],  # Col 3
    [(0, 0), (1, 1), (2, 2)],  # Main diagonal
    [(0, 2), (1, 1), (2, 0)],  # Anti diagonal
]

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
        self.progress: List[str] = duel_data["progress"]

        self.first_solve: Optional[int] = None
        self.last_solved_coords: Optional[Tuple[int, int]] = None
        self.winning_file_index: Optional[int] = None

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
            self.last_solved_coords = divmod(idx, 3)
            self.update_board_status()
            if self.status != DuelStatus.ONGOING.value:
                self.end_time = time
                break

        if self.status == DuelStatus.ONGOING.value and get_time() > self.end_time:
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

    def update_board_status(self):
        """
        Returns the current status of the board as FINISHED, ONGOING, or DRAW.
        
        If FINISHED, returns (FINISHED, winning_player, winning_file_index).
        If DRAW, returns (DRAW, -1, -1).
        If ONGOING, returns (ONGOING, -1, -1).
        """
        board = self.get_board()
        empty_cells: List[Tuple[int, int]] = []
        self.winner = None
        self.winning_file_index = None
        
        # Check for a win
        for i, file in enumerate(WINNING_FILES):
            player = board[file[0][0]][file[0][1]][0]
            if player == 0:
                continue

            if all(board[x][y][0] == player for x, y in file):
                self.status = DuelStatus.FINISHED.value
                self.winner = player
                self.winning_file_index = i
                return

        for row in range(3):
            for col in range(3):
                if board[row][col][0] == 0:
                    empty_cells.append((row, col))

        for player in [self.player1, self.player2]:
            for i, file in enumerate(WINNING_FILES):
                occupied_by_player = sum(1 for x, y in file if board[x][y][0] == player)
                empty_in_file = sum(1 for x, y in file if board[x][y][0] == 0)
                
                if occupied_by_player + empty_in_file == 3:
                    self.status = DuelStatus.ONGOING.value
                    return

        self.status = DuelStatus.DRAW.value

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
        move_locations = [
            [(50, 50), (350, 50), (650, 50)],
            [(50, 350), (350, 350), (650, 350)],
            [(50, 650), (350, 650), (650, 650)],
        ]
        move_size = (200, 200)

        player1_img = imgh.load_image(await self._get_player1_img())
        player1_img = imgh.extract_frames(player1_img)
        player1_img = [imgh.resize(img, move_size) for img in player1_img]

        player2_img = imgh.load_image(await self._get_player2_img())
        player2_img = imgh.extract_frames(player2_img)
        player2_img = [imgh.resize(img, move_size) for img in player2_img]

        board_img = imgh.load_image_from_path("bin/tictac_board.png")
        board_img = imgh.extract_frames(board_img)
        layers = [board_img]
        layers_coords = [(0, 0)]

        board = self.get_board()
        for i in range(3):
            for j in range(3):
                if board[i][j][0] == 0:
                    continue
                x, y = move_locations[i][j]
                img = player1_img if board[i][j][0] == self.player1 else player2_img
                layers.append(img)
                layers_coords.append((x, y))
        
        if self.status == DuelStatus.FINISHED.value:
            assert self.winning_file_index is not None
            if self.winning_file_index < 3:
                row = self.winning_file_index
                across = imgh.load_image_from_path("bin/tictac_across.png")
                across = imgh.extract_frames(across)
                layers.append(across)
                layers_coords.append((0, 300 * row))
                
            elif self.winning_file_index < 6: 
                col = self.winning_file_index - 3
                across = imgh.load_image_from_path("bin/tictac_across.png")
                across = imgh.extract_frames(across)
                across = [imgh.rotate_90_clockwise(img) for img in across]
                layers.append(across)
                layers_coords.append((300 * col, 0))
            
            else:
                diag = imgh.load_image_from_path("bin/tictac_diag.png")
                diag = imgh.extract_frames(diag)
                if self.winning_file_index == 7:
                    diag = [imgh.flip(img) for img in diag]
                layers.append(diag)
                layers_coords.append((0, 0))

        return imgh.stack_and_animate(layers, layers_coords=layers_coords)

    async def save_state(self):
        await duel_queries.save_tictac_duel(self)


class TickTacDuelView(BaseView):
    @classmethod
    async def send_view(cls, duel: TicTacDuel):
        view = cls(duel)
        await view._send_view()

    def __init__(self, duel: TicTacDuel):
        self.duel = duel
        super().__init__(
            users=[self.duel.player1, self.duel.player2],
            timeout=60 * self.duel.time_limit + 300,
        )

    def _add_items(self):
        self.clear_items()

        # board = self.duel.get_board()
        # for i in range(3):
        #     for j in range(3):
        #         idx = i * 3 + j
        #         problem = self.duel.problems_loaded[idx]
        #         if board[i][j][0] == 0:
        #             self._add_url_button(
        #                 label=f"{idx + 1}",
        #                 url=problem.link,
        #                 row=i,
        #             )
        #         else:
        #             emoji = "❌" if self.duel.first_solve == board[i][j][0] else "⭕"
        #             self._add_url_button(
        #                 label=emoji,
        #                 url=problem.link,
        #                 row=i,
        #             )

        if self.duel.status == DuelStatus.ONGOING.value:
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
        self._release_lock()

    async def _get_embed(self):
        embed = BaseEmbed(title="TicTac Duel")
        if self.duel.status != DuelStatus.ONGOING.value:
            embed.add_field(name="")
            if self.duel.status == DuelStatus.FINISHED.value:
                embed.add_field(name="Winner 👑", value=f"<@{self.duel.winner}>")
            elif self.duel.status == DuelStatus.DRAW.value:
                embed.add_field(name="Draw 😕")
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
            for j in range(3):
                idx = 3 * i + j
                problem = self.duel.problems_loaded[idx]
                # name = f"Problem {idx + 1}."
                value = f"**{idx + 1}. [{problem.contestId}-{problem.index}]({problem.link})**"
                if board[i][j][0] != 0:
                    time_taken = (board[i][j][1] - self.duel.start_time) // 60
                    value += f"by <@{board[i][j][0]}> @ {time_taken} mins"
                else:
                    value += "by **~ ~ ~**"
                embed.add_field(name="", value=value)

        board_img = await self.duel.get_board_img()
        board_img = File(board_img, "board.gif")
        files: List[File] = [board_img]
        return embed, files
