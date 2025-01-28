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

        self.mode = "default"

        super().__init__(user=user_id)

    def _add_items(self):
        self.clear_items()

        if self.mode == "default":
            self._add_button(label="RELOAD PROBLEMS", custom_id="reload_problems", row=0)
            self._add_button(label="RELOAD USERS", custom_id="reload_users", row=0)

            self._add_button(label="TOURNAMENT", custom_id="tournament", row=1)

            self._add_button(label="ADD ADMIN", custom_id="add_admin", row=2)
            self._add_button(label="REMOVE ADMIN", custom_id="remove_admin", row=2)
            self._add_button(label="LIST ADMINS", custom_id="list_admins", row=2)
        
        elif self.mode in ["reload_problems", "reload_users"]:
            self._add_button(label="YES", custom_id="yes", row=0)
            self._add_button(label="NO", custom_id="no", row=0)

    async def _button_clicked(self, interaction: Interaction, custom_id: str) -> None:
        if custom_id not in ["add_admin", "remove_admin"]:
            await interaction.response.defer()

        if custom_id == "yes":
            if self.mode == "reload_problems":
                self.stop()
                await admin_reload_problems()
                return
            
            elif self.mode == "reload_users":
                self.stop()
                await admin_reload_users()
                return
            
            else:
                raise ValueError(f"Unknown mode: {self.mode}")

        
        elif custom_id == "no":
            self.mode = "default"

        elif custom_id == "reload_problems":
            self.mode = "reload_problems"

        elif custom_id == "reload_users":
            self.mode = "reload_users"

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
            self.stop()
            await list_admins()
            return

        else:
            raise ValueError(f"Unknown custom_id: {custom_id}")

        await self._send_view()
    
    async def _modal_submit(self, interaction: Interaction, custom_id: str, values: Dict[str, str]) -> None:
        await interaction.response.defer()

        if custom_id == "add_admin":
            self.stop()
            user_id = values["user_id"]
            await add_admin(int(user_id))
            return
        
        elif custom_id == "remove_admin":
            self.stop()
            user_id = values["user_id"]
            await remove_admin(int(user_id))
            return
            
        else:
            raise ValueError(f"Unknown custom_id: {custom_id}")

    async def _get_embed(self):
        if self.mode == "default":
            embed = BaseEmbed(title="Admin Menu", description="With great power comes great responsibility.")
        elif self.mode == "reload_problems":
            embed = BaseEmbed(title="Reload Problems", description="Are you sure you want to reload the problems?")
        elif self.mode == "reload_users":
            embed = BaseEmbed(title="Reload Users", description="Are you sure you want to reload the users?")
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
        files: List[File] = []
        return embed, files


async def orz_admin():
    await AdminMainView.send_view()


async def admin_reload_problems():
    from codeforces.api import get_problem_list
    from database.cf_queries import clear_problems, dump_problems
    from utils.general import get_time

    embed = BaseEmbed(title="Reloading Problems")
    embed.add_field(name="This will take around 10 seconds.", value="Please wait...")
    await Messenger.send_message(embed=embed)

    start_time = get_time()
    problems = get_problem_list()
    await clear_problems()
    await dump_problems(problems)
    end_time = get_time()

    embed = BaseEmbed(title="Problems Reloaded")
    embed.add_field(name="Problem Count", value=f"{len(problems)}")
    embed.add_field(name="Time Taken", value=f"{end_time - start_time} seconds")

    await Messenger.send_message(embed=embed)


async def admin_reload_users():
    from codeforces.api import get_users_info as cf_get_users_info
    from database.cf_queries import clear_users, dump_users
    from database.user_queries import get_users_info
    from utils.general import get_time

    embed = BaseEmbed(title="Reloading Users")
    embed.add_field(name="This will take around 2 seconds.", value="Please wait...")
    await Messenger.send_message(embed=embed)

    start_time = get_time()
    users_info = await get_users_info(None)
    cf_handles = [user["cf_handle"] for user in users_info]
    cf_users = cf_get_users_info(cf_handles)
    await clear_users()
    await dump_users(cf_users)
    end_time = get_time()

    embed = BaseEmbed(title="Users Reloaded")
    embed.add_field(name="User Count", value=f"{len(cf_users)}")
    embed.add_field(name="Time Taken", value=f"{end_time - start_time} seconds")

    await Messenger.send_message(embed=embed)


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