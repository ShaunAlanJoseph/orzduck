from discord import Interaction, app_commands
from discord.ext.commands import Cog, Bot  # type: ignore
from logging import info


class OrzDuckCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        info("OrzDuckCog has been initialized.")
    
    @app_commands.command(
        name="orz", description="OTZ"
    )
    async def orz(self, interaction: Interaction):
        await interaction.response.send_message("orz perf!")
