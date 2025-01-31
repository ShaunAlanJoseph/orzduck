from discord import Interaction, app_commands
from discord.ext.commands import Cog, Bot  # type: ignore
from logging import info

from utils.context_manager import ctx_mgr
from orz_modules.utils import is_admin_app_command, is_user_app_command


class OrzDuckCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        info("OrzDuckCog has been initialized.")
    
    async def cog_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            return
        await super().cog_app_command_error(interaction, error)
    
    @app_commands.command(
        name="orz", description="OTZ"
    )
    async def orz(self, interaction: Interaction):
        await interaction.response.send_message("quack!")
    
    @app_commands.command(name="admin", description="High level admin stuff!")
    @is_admin_app_command()
    async def orz_admin(self, interaction: Interaction):
        from orz_modules.admin import orz_admin

        ctx_mgr().set_init_interaction(interaction)
        await orz_admin()
    
    @app_commands.command(name="register", description="Register yourself?")
    @is_user_app_command(invert=True)
    async def orz_register(self, interaction: Interaction):
        from orz_modules.user import orz_register

        ctx_mgr().set_init_interaction(interaction)
        await orz_register()
    
    @app_commands.command(name="duel_tictac", description="Start a TicTacToe duel!")
    @is_user_app_command()
    async def orz_duel_tictac(self, interaction: Interaction, rating: int = 900, time_limit: int = 60):
        from orz_modules.duel import orz_duel_tictac

        ctx_mgr().set_init_interaction(interaction)
        await orz_duel_tictac(rating, time_limit)

    @app_commands.command(name="duel_b3", description="Start a B3 duel!")
    @is_user_app_command()
    async def orz_duel_b3(self, interaction: Interaction, rating: int = 900, time_limit: int = 60):
        from orz_modules.duel import orz_duel_b3

        ctx_mgr().set_init_interaction(interaction)
        await orz_duel_b3(rating, time_limit)
    