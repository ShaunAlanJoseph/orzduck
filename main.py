from asyncio import run
from discord import Intents
from discord.ext import commands
from logging import basicConfig, INFO, info

from database.db import DB
from orzduck_cog import OrzDuckCog
from config import DISCORD_API_TOKEN, HQ_CHANNEL_ID
from utils.discord.disc_utils import fetch_channel
from utils.context_manager import ContextManager


basicConfig(level=INFO)


async def main():
    await DB.establish_connection()
    ContextManager.setup_context_manager()

    bot = commands.Bot(command_prefix="!", intents=Intents.all(), help_command=None)

    async def sync_tree():
        app_commands = await bot.tree.sync()
        info(f"Synced {len(app_commands)} commands.")

    async def announce_online():
        assert bot.user is not None
        HQ = await fetch_channel(bot, HQ_CHANNEL_ID)
        await HQ.send(  # type: ignore
            f"Hi, I've logged in as **User:** `{bot.user.name}` (**ID:** `{bot.user.id}`)"
        )

    @bot.event
    async def on_ready():  # type: ignore
        await bot.add_cog(OrzDuckCog(bot))
        await sync_tree()
        await announce_online()

    await bot.start(DISCORD_API_TOKEN)


if __name__ == "__main__":
    run(main())
