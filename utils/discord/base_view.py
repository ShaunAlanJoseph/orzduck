from discord import Interaction, Embed, File, ButtonStyle
from discord.ui import View
from functools import partial
from typing import Any, Optional, List, Tuple, Dict
from logging import info

from utils.context_manager import ctx_mgr
from utils.discord.messenger import Messenger
from utils.discord.base_button import BaseButton, BaseURLButton
from utils.discord.base_dropdown import BaseDropdown


class BaseView(View):
    @classmethod
    async def send_view(cls, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError

    def __init__(
        self,
        *,
        user: Optional[int] = None,
        users: Optional[List[int]] = None,
        timeout: int = 180,
    ):
        # list of users to interact with the view
        self._users = (users or []) + ([user] if user else [])
        if not self._users:
            raise ValueError("Users must be specified.")

        # to lock interaction with the view
        self._lock = False

        # context vars
        self._init_interaction = ctx_mgr().get_init_interaction()
        self._active_msg = ctx_mgr().get_active_msg()

        super().__init__(timeout=timeout)

    def _add_items(self):
        pass

    async def interaction_check(self, interaction: Interaction) -> bool:
        ctx_mgr().set_init_interaction(self._init_interaction)
        assert self._active_msg is not None
        ctx_mgr().set_active_msg(self._active_msg)

        if interaction.user.id in self._users:
            if self._acquire_lock():
                return True
            else:
                await Messenger.send_message_ephemeral(
                    content="Please wait while the previous interaction is being processed!"
                )
        else:
            await Messenger.send_message_ephemeral(
                content="You aren't allowed to interact with this!"
            )
        return False

    async def on_error(
        self, interaction: Interaction, error: Exception, *args: Any, **kwargs: Any
    ):
        raise error

    async def on_timeout(self):
        self.clear_items()
        self._add_text_dropdown("Timed out . . .")

        assert self._active_msg is not None
        ctx_mgr().set_active_msg(self._active_msg)
        await Messenger.send_message_no_reset(view=self)
    
    def __del__(self):
        assert self._active_msg is not None
        info(f"{self.__class__.__name__} deleted, active_msg: {self._active_msg.id}")

    def stop(self):
        super().stop()
        assert self._active_msg is not None
        info(f"{self.__class__.__name__} stopped, active_msg: {self._active_msg.id}")

    async def stop_and_disable(self, *, custom_text: Optional[str] = None):
        self.clear_items()
        self._add_text_dropdown(custom_text or "Stopped . . .")

        await Messenger.send_message_no_reset(view=self)
        self.stop()

    def _acquire_lock(self) -> bool:
        if not self._lock:
            self._lock = True
            return True
        return False

    def _release_lock(self):
        self._lock = False

    def _add_button(
        self,
        *,
        label: str,
        custom_id: str,
        style: ButtonStyle = ButtonStyle.green,
        row: Optional[int] = None,
        disabled: bool = False,
        emoji: Optional[str] = None,
    ):
        callback = partial(self._button_clicked, custom_id=custom_id)
        button = BaseButton(
            label=label,
            custom_id=custom_id,
            style=style,
            row=row,
            button_click_callback=callback,
            disabled=disabled,
            emoji=emoji,
        )
        self.add_item(button)

    def _add_url_button(
        self,
        *,
        label: str,
        url: str,
        row: Optional[int] = None,
        disabled: bool = False,
        emoji: Optional[str] = None,
    ):
        button = BaseURLButton(
            label=label,
            row=row,
            disabled=disabled,
            emoji=emoji,
            url=url,
        )
        self.add_item(button)
    
    async def _button_clicked(self, interaction: Interaction, custom_id: str) -> None:
        raise NotImplementedError

    def _add_dropdown(
        self,
        *,
        custom_id: str,
        options: Dict[str, str],
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        row: Optional[int] = None,
        disabled: bool = False,
        emojis: Optional[Dict[str, str]] = None,
        description: Optional[List[str]] = None,
    ):
        """
        :param options: (value: label) of the select options
        """
        callback = partial(self._dropdown_selected, custom_id=custom_id)
        dropdown = BaseDropdown(
            custom_id=custom_id,
            options=options,
            placeholder=placeholder,
            dropdown_selected_callback=callback,
            min_values=min_values,
            max_values=max_values,
            row=row,
            disabled=disabled,
            emojis=emojis,
            description=description,
        )
        self.add_item(dropdown)

    def _add_text_dropdown(self, text: str):
        self._add_dropdown(
            custom_id="text_dropdown",
            options={"1": text},
            placeholder=text,
            disabled=True,
        )

    async def _dropdown_selected(
        self, interaction: Interaction, custom_id: str, values: List[str]
    ) -> None:
        raise NotImplementedError

    async def _modal_submit(
        self, interaction: Interaction, custom_id: str, values: Dict[str, str]
    ) -> None:
        raise NotImplementedError

    async def _get_embed(self) -> Tuple[Optional[Embed], List[File]]:
        raise NotImplementedError

    async def _update_view(self, interaction: Interaction):
        self._add_items()

    async def _send_view(self):
        self._add_items()
        embed, files = await self._get_embed()
        self._active_msg = await Messenger.send_message(
            view=self, embed=embed, files=files
        )
        self._release_lock()

