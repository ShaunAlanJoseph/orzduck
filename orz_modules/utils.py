from discord import Interaction, app_commands

from config import ADMINS


def is_admin_app_command():
    async def predicate(interaction: Interaction):
        user_id = interaction.user.id

        if user_id in ADMINS:
            return True
        
        await interaction.response.send_message(f"Imagine thinking that you could use this command. 🤧")
        return False
    
    return app_commands.check(predicate)


def is_user_app_command(invert: bool = False):
    async def predicate(interaction: Interaction): 
        from orz_modules.user import User
        user_id = interaction.user.id
        try:
            await User.load_user(user_id)
            return True
        except IndexError:
            await interaction.response.send_message(f"First use `/register` to register yourself. 😕")
            return False
    
    async def inverted_predicate(interaction: Interaction):
        from orz_modules.user import User
        user_id = interaction.user.id
        try:
            await User.load_user(user_id)
            await interaction.response.send_message(f"You are already registered. 😕")
            return False
        except IndexError:
            return True
    
    return app_commands.check(inverted_predicate if invert else predicate)

