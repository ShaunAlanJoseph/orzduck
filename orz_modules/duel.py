from enum import Enum
from discord import File, Interaction
from typing import List, Optional

from utils.context_manager import ctx_mgr
from utils.discord import BaseView, Messenger, BaseEmbed
from orz_modules.user import User


class Duel(Enum):
    TICTAC = "TicTac"
    B3 = "Best of 3"
    CLASSIC = "Classic"


class DuelStatus(Enum):
    ONGOING = "ongoing"
    FINISHED = "finished"
    DRAW = "draw"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


class DuelWaitingView(BaseView):
    @classmethod
    async def send_view(cls, duel_mode: Duel, player1: int, rating: int, time_limit: int):
        view = cls(duel_mode, player1, rating, time_limit)
        await view._send_view()
    
    def __init__(self, duel_mode: Duel, player1: int, rating: int, time_limit: int):
        self.duel_mode = duel_mode
        self.player1: int = player1
        self.player2: Optional[int] = None
        self.rating = rating
        self.time_limit = time_limit

        self.mode = "one_player"
        super().__init__()
    
    def _add_items(self):
        self.clear_items()

        if self.mode == "one_player":
            self._add_button(label="Join", custom_id="join")
            self._add_button(label="Cancel", custom_id="cancel")

        elif self.mode == "two_players":
            self._add_button(label="Start", custom_id="start")
            self._add_button(label="Cancel", custom_id="cancel")
        
        else:
            raise ValueError(f"Invalid mode: {self.mode}")
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        ctx_mgr().set_init_interaction(self._init_interaction)
        assert self._active_msg is not None
        ctx_mgr().set_active_msg(self._active_msg)

        user_id = interaction.user.id
        custom_id = interaction.data["custom_id"]  # type: ignore

        if custom_id == "join":
            if user_id == self.player1:
                await interaction.response.send_message(
                    content="You have already joined the duel.",
                    ephemeral=True
                )
                return False
            
            try:
                await User.load_user(user_id)
                return True
            except IndexError:
                await interaction.response.send_message(
                    content="You need to register yourself first!",
                    ephemeral=True
                )
                return False
            
        elif custom_id == "start":
            if user_id == self.player1 or user_id == self.player2:
                return True

        elif custom_id == "cancel" and self.mode == "one_player":
            if user_id == self.player1:
                return True
        
        elif custom_id == "cancel" and self.mode == "two_players":
            if user_id == self.player1 or user_id == self.player2:
                return True
        
        else:
            raise ValueError(f"Invalid custom_id: {custom_id}")

        await interaction.response.send_message(
            content="You aren't allowed to interact with this!",
            ephemeral=True
        )
        return False
    
    async def _button_clicked(self, interaction: Interaction, custom_id: str) -> None:
        await interaction.response.defer()

        if custom_id == "join":
            self.mode = "two_players"
            self.player2 = interaction.user.id
        
        elif custom_id == "cancel":
            await self.stop_and_disable(custom_text="Cancelled . . .")
            return

        elif custom_id == "start":
            if self.duel_mode == Duel.TICTAC:
                self.stop()
                assert self.player2 is not None
                await _orz_duel_tictac(self.player1, self.player2, self.rating, self.time_limit)
                return
            
            else:
                raise ValueError(f"Invalid duel_mode: {self.duel_mode}")
        
        else:
            raise ValueError(f"Invalid custom_id: {custom_id}")
        
        await self._send_view()
    
    async def _get_embed(self):
        if self.mode == "one_player":
            embed = BaseEmbed(title="Waiting for player . . .")
            embed.add_field(name="Duel Mode", value=f"{self.duel_mode.value}", inline=False)
            embed.add_field(name="Player 1", value=f"<@{self.player1}>")
            embed.add_field(name="")
            embed.add_field(name="Player 2", value="???")
            embed.add_field(name="Rating", value=f"{self.rating}")
            embed.add_field(name="")
            embed.add_field(name="Time Limit", value=f"{self.time_limit} minutes")
        
        elif self.mode == "two_players":
            embed = BaseEmbed(title="Ready to Start!")
            embed.add_field(name="Duel Mode", value=f"{self.duel_mode.value}", inline=False)
            embed.add_field(name="Player 1", value=f"<@{self.player1}>")
            embed.add_field(name="")
            embed.add_field(name="Player 2", value=f"<@{self.player2}>")
            embed.add_field(name="Rating", value=f"{self.rating}")
            embed.add_field(name="")
            embed.add_field(name="Time Limit", value=f"{self.time_limit} minutes")
        
        else:
            raise ValueError(f"Invalid mode: {self.mode}")


        files: List[File] = []
        return embed, files


async def orz_duel_tictac(rating: int, time_limit: int):
    player1 = ctx_mgr().get_user_id()
    time_limit = min(time_limit, 300)
    await DuelWaitingView.send_view(Duel.TICTAC, player1, rating, time_limit)


async def _orz_duel_tictac(p1: int, p2: int, rating: int, time_limit: int):
    player1 = await User.load_user(p1)
    player2 = await User.load_user(p2)

    await _orz_duel_tictac_select_problems(player1, player2, rating, time_limit)


async def _orz_duel_tictac_select_problems(player1: User, player2: User, rating: int, time_limit: int):
    from codeforces.cf import get_duel_problems
    from duels.tictac_duel import TicTacDuel, TickTacDuelView

    try:
        assert player1.cf_handle is not None
        assert player2.cf_handle is not None
        problems = await get_duel_problems(
            player1.cf_handle, player2.cf_handle, rating - 100, rating + 100, 9
        )
    except ValueError:
        embed = BaseEmbed(title="No Problems Found", description="No problems found for the given rating range.")
        embed.add_field(name="Duel Mode", value=f"{Duel.TICTAC}", inline=False)
        embed.add_field(name="Player 1", value=f"<@{player1.user_id}>")
        embed.add_field(name="Player 2", value=f"<@{player2.user_id}>")
        embed.add_field(name="Rating", value=f"{rating}", inline=False)
        await Messenger.send_message(embed=embed)
        return
    
    duel = await TicTacDuel.create_duel(player1.user_id, player2.user_id, problems, rating, time_limit) 
    await TickTacDuelView.send_view(duel)