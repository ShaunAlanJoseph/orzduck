from discord.ext.commands import Bot  # type: ignore


async def fetch_channel(bot: Bot, channel_id: int):
    return await bot.fetch_channel(channel_id)