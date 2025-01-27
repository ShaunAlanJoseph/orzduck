from discord import Interaction, TextStyle
from discord.ui import Modal, TextInput, View
from typing import Dict, Optional, Protocol

from utils.context_manager import ctx_mgr


class ModalSubmitCallback(Protocol):
    async def __call__(
        self, *, interaction: Interaction, values: Dict[str, str]
    ) -> None: ...


class BaseModal(Modal):
    def __init__(
        self,
        *,
        title: str,
        custom_id: str,
        modal_submit_callback: ModalSubmitCallback,
        view: Optional[View],
        timeout: int = 180,
    ):
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.modal_submit_callback = modal_submit_callback
        self._add_items()
        self._init_interaction = ctx_mgr().get_init_interaction()
        self._active_msg = ctx_mgr().get_active_msg()
        self.view = view

    async def interaction_check(self, interaction: Interaction) -> bool:
        await interaction.response.defer()
        
        ctx_mgr().set_init_interaction(self._init_interaction)
        assert self._active_msg is not None
        ctx_mgr().set_active_msg(self._active_msg)

        return True

    def _add_items(self) -> None:
        pass

    def add_text_input(
        self,
        *,
        label: str,
        custom_id: str,
        long: bool,
        placeholder: Optional[str] = None,
        default: Optional[str] = None,
        required: bool = True,
        row: Optional[int] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ):
        text_style = TextStyle.long if long else TextStyle.short
        super().add_item(
            TextInput(
                label=label,
                custom_id=custom_id,
                placeholder=placeholder,
                required=required,
                default=default,
                style=text_style,
                row=row,
                min_length=min_length,
                max_length=max_length,
            )
        )

    async def on_submit(self, interaction: Interaction):
        values: Dict[str, str] = {}
        for item in self.children:
            if isinstance(item, TextInput):
                values[item.custom_id] = item.value
        if self.view is not None and self.view.is_finished():
            return
        await self.modal_submit_callback(interaction=interaction, values=values)
