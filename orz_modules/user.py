from discord import File, Interaction
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from database import user_queries
from utils.context_manager import ctx_mgr
from utils.discord import BaseModal, BaseEmbed, Messenger, BaseView
from utils.general import get_time
from codeforces.cf import get_handle_verification_problem, get_user_problem_status, Verdict

if TYPE_CHECKING:
    from codeforces.api import CFUser, CFProblem


class User:
    @classmethod
    async def load_user(cls, user_id: int):
        """
        :raises IndexError: If user_id is not found in the database
        """
        user_data = await user_queries.get_user_info(user_id)
        return cls(user_data)

    def __init__(self, user_data: Dict[str, Any]):
        self.user_id: int = user_data["user_id"]
        self.fullname: str = user_data["fullname"]
        self.join_time: str = user_data["join_time"]

        self.cf_handle: Optional[str] = user_data.get("cf_handle", None)
        self.cf_user: Optional["CFUser"] = None

        self.college_mail: Optional[str] = user_data.get("college_mail", None)
        self.roll_number: Optional[str] = user_data.get("roll_number", None)

    def load_cf_user(self):
        from codeforces.api import get_user_info

        assert self.cf_handle is not None
        self.cf_user = get_user_info(self.cf_handle)

    async def save_user(self):
        await user_queries.save_user(self)


async def orz_register():
    modal = BaseModal(
        title="Register Yourself",
        custom_id="register",
        modal_submit_callback=_orz_register,
        view=None,
    )
    modal.add_text_input(
        label="Full Name", custom_id="fullname", long=False, placeholder="fullname"
    )
    modal.add_text_input(
        label="Codeforces Handle",
        custom_id="cf_handle",
        long=False,
        placeholder="cf_handle",
    )
    modal.add_text_input(
        label="College Email",
        custom_id="college_mail",
        long=False,
        placeholder="college_mail",
    )
    modal.add_text_input(
        label="Roll Number",
        custom_id="roll_number",
        long=False,
        placeholder="roll_number",
    )

    await ctx_mgr().get_init_interaction().response.send_modal(modal)


async def _orz_register(interaction: Interaction, values: Dict[str, Any]):
    await interaction.response.defer()

    values["user_id"] = ctx_mgr().get_user_id()
    values["join_time"] = get_time()

    user = User(values)
    assert user.cf_handle is not None
    assert user.college_mail is not None
    assert user.roll_number is not None

    if await user_queries.check_duplicate_cf_handle(user.cf_handle):
        embed = BaseEmbed(
            title="Duplicate Codeforces Handle",
            description="This Codeforces handle is already registered.",
        )
        embed.add_field(name="Codeforces Handle", value=user.cf_handle)
        await Messenger.send_message(embed=embed)
        return

    if await user_queries.check_duplicate_college_mail(user.college_mail):
        embed = BaseEmbed(
            title="Duplicate College Email",
            description="This College Email is already registered.",
        )
        embed.add_field(name="College Email", value=user.college_mail)
        await Messenger.send_message(embed=embed)
        return

    if await user_queries.check_duplicate_roll_number(user.roll_number):
        embed = BaseEmbed(
            title="Duplicate Roll Number",
            description="This Roll Number is already registered.",
        )
        embed.add_field(name="Roll Number", value=user.roll_number)
        await Messenger.send_message(embed=embed)
        return

    await _orz_register_get_problem(user)


class UserVerificationView(BaseView):
    @classmethod
    async def send_view(cls, user: User, problem: "CFProblem"):
        view = cls(user, problem)
        await view._send_view()

    def __init__(self, user: User, problem: "CFProblem"):
        self.user = user
        assert user.cf_handle is not None
        self.cf_handle = user.cf_handle
        self.problem = problem
        self.start_time = get_time()

        self.mode = "default"

        super().__init__(user=user.user_id)

    def _add_items(self):
        self.clear_items()

        if self.mode == "default":
            self._add_button(label="DONE", custom_id="done")
        elif self.mode == "checking":
            self._add_button(label="CHECKING", custom_id="checking", disabled=True)

    async def _button_clicked(self, interaction: Interaction, custom_id: str) -> None:
        await interaction.response.defer()

        if custom_id == "done":
            self.mode = "checking"            
            await self.check_done()
            return

        else:
            raise ValueError(f"Invalid custom_id: {custom_id}")
        
        await self._send_view()
    
    async def _get_embed(self):
        embed = BaseEmbed(title="Handle Verification", description="Verifying your codeforces handle.")
        embed.add_field(name="CF Handle", value=self.cf_handle)
        embed.add_field(name="Problem", value=f"[{self.problem.name}]({self.problem.link})")

        files: List[File] = []
        return embed, files

    async def check_done(self):
        curr_time = get_time()
        if curr_time - self.start_time > 90:
            await self.stop_and_disable(custom_text="Verification Timed Out")
            return

        submissions = get_user_problem_status(self.cf_handle, self.problem, self.start_time)
        for submission in submissions:
            if submission[1] == Verdict.COMPILATION_ERROR.value:
                self.stop()
                await _orz_register_verified(self.user)
                return

        self.mode = "default"
        await self._send_view()        


async def _orz_register_get_problem(user: User):
    problem = await get_handle_verification_problem()
    await UserVerificationView.send_view(user, problem)


async def _orz_register_verified(user: User):
    assert user.cf_handle is not None
    assert user.college_mail is not None
    assert user.roll_number is not None
    await user.save_user()

    embed = BaseEmbed(
        title="Registration Successful",
        description="You have been successfully registered.",
    )
    embed.add_field(name="Full Name", value=user.fullname)
    embed.add_field(name="Codeforces Handle", value=user.cf_handle)
    embed.add_field(name="College Email", value=user.college_mail)
    embed.add_field(name="Roll Number", value=user.roll_number)

    await Messenger.send_message(embed=embed)