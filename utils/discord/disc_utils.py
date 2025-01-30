from discord.ext.commands import Bot  # type: ignore


class DiscUtils:
    _instance = None

    @classmethod
    def setup_disc_utils(cls, bot: Bot):
        cls._instance = cls(bot)
    
    @classmethod
    def get_instance(cls):
        assert cls._instance is not None, "DiscUtils not set up"
        return cls._instance

    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def fetch_channel(self, channel_id: int):
        return await self.bot.fetch_channel(channel_id)

    async def fetch_user(self, user_id: int):
        return await self.bot.fetch_user(user_id)


def disc_utils():
    return DiscUtils.get_instance()