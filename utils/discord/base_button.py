from discord import ButtonStyle, Interaction
from discord.ui import Button
from typing import Optional, Protocol, Any


class ButtonClickCallback(Protocol):
    async def __call__(self, interaction: Interaction) -> None: ...


class BaseButton(Button[Any]):
    def __init__(
        self,
        *,
        label: str,
        button_click_callback: ButtonClickCallback,
        disabled: bool = False,
        custom_id: Optional[str] = None,
        row: Optional[int] = None,
        style: ButtonStyle = ButtonStyle.green,
        emoji: Optional[str] = None,
    ):
        super().__init__(
            label=label,
            custom_id=custom_id,
            row=row,
            style=style,
            disabled=disabled,
            emoji=emoji,
        )
        self.button_click_callback = button_click_callback

    async def callback(self, interaction: Interaction):
        await self.button_click_callback(interaction=interaction)


class BaseURLButton(Button[Any]):
    def __init__(
        self,
        *,
        url: str,
        label: str,
        disabled: bool = False,
        row: Optional[int] = None,
        emoji: Optional[str] = None,
    ):
        super().__init__(
            label=label,
            url=url,
            row=row,
            disabled=disabled,
            emoji=emoji,
        )
