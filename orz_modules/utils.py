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
