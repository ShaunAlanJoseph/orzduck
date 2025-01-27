from typing import Dict, List
from functools import partial
from discord import File, Interaction

from utils.discord import BaseView, BaseModal, BaseEmbed, Messenger
from utils.context_manager import ctx_mgr


class AdminMainView(BaseView):
    @classmethod
    async def send_view(cls):
        view = cls()
        await view._send_view()

    def __init__(self):
        user_id = ctx_mgr().get_user_id()

        super().__init__(user=user_id)

    def _add_items(self):
        self.clear_items()

        self._add_button(label="RELOAD PROBLEMS", custom_id="reload_problems", row=0)
        self._add_button(label="RELOAD USERS", custom_id="reload_users", row=0)

        self._add_button(label="TOURNAMENT", custom_id="tournament", row=1)

        self._add_button(label="ADD ADMIN", custom_id="add_admin", row=2)
        self._add_button(label="REMOVE ADMIN", custom_id="remove_admin", row=2)
        self._add_button(label="LIST ADMINS", custom_id="list_admins", row=2)

    async def _button_clicked(self, interaction: Interaction, custom_id: str) -> None:
        if custom_id not in ["add_admin", "remove_admin"]:
            await interaction.response.defer()

        if custom_id == "reload_problems":
            pass

        elif custom_id == "reload_users":
            pass

        elif custom_id == "tournament":
            pass

        elif custom_id == "add_admin":
            callback = partial(self._modal_submit, custom_id=custom_id)
            modal = BaseModal(
                title="Add Admin",
                custom_id="add_admin",
                view=self,
                modal_submit_callback=callback,
            )
            modal.add_text_input(
                label="User ID",
                custom_id="user_id",
                long=False,
                placeholder="User ID",
                min_length=15,
                max_length=25,
            )
            await interaction.response.send_modal(modal)
            return

        elif custom_id == "remove_admin":
            callback = partial(self._modal_submit, custom_id=custom_id)
            modal = BaseModal(
                title="Remove Admin",
                custom_id="remove_admin",
                view=self,
                modal_submit_callback=callback,
            )
            modal.add_text_input(
                label="User ID",
                custom_id="user_id",
                long=False,
                placeholder="User ID",
                min_length=15,
                max_length=25,
            )
            await interaction.response.send_modal(modal)
            return
        
        elif custom_id == "list_admins":
            await list_admins()
            self.stop()
            return

        else:
            raise ValueError(f"Unknown custom_id: {custom_id}")

        await self._send_view()
    
    async def _modal_submit(self, interaction: Interaction, custom_id: str, values: Dict[str, str]) -> None:
        await interaction.response.defer()

        if custom_id == "add_admin":
            user_id = values["user_id"]
            await add_admin(int(user_id))
            self.stop()
            return
        
        elif custom_id == "remove_admin":
            user_id = values["user_id"]
            await remove_admin(int(user_id))
            self.stop()
            return
            
        else:
            raise ValueError(f"Unknown custom_id: {custom_id}")

    async def _get_embed(self):
        embed = BaseEmbed(title="Admin Menu", description="With great power comes great responsibility.")
        files: List[File] = []
        return embed, files


async def orz_admin():
    await AdminMainView.send_view()


async def add_admin(admin_user_id: int):
    from config import ADMINS

    if admin_user_id not in ADMINS:
        ADMINS.append(admin_user_id)

        embed = BaseEmbed(title="Admin Added")
        embed.add_field(name="Admin ID", value=f"<@{admin_user_id}>")
    
    else:
        embed = BaseEmbed(title="Admin Already Exists")
        embed.add_field(name="Admin ID", value=f"<@{admin_user_id}>")
    
    await Messenger.send_message(embed=embed)


async def remove_admin(admin_user_id: int):
    from config import ADMINS

    if admin_user_id in ADMINS:
        ADMINS.remove(admin_user_id)

        embed = BaseEmbed(title="Admin Removed")
        embed.add_field(name="Admin ID", value=f"<@{admin_user_id}>")

    else:
        embed = BaseEmbed(title="Admin Not Found")
        embed.add_field(name="Admin ID", value=f"<@{admin_user_id}>")
    
    await Messenger.send_message(embed=embed)
    

async def list_admins():
    from config import ADMINS

    embed = BaseEmbed(title="List of Admins")
    for i, admin_user_id in enumerate(ADMINS):
        embed.add_field(name=f"{i + 1}", value=f"<@{admin_user_id}>")

    await Messenger.send_message(embed=embed)