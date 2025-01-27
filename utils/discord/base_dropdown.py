from discord import Interaction
from discord.ui import Select
from typing import Any, Dict, List, Optional, Protocol


class DropdownSelectedCallback(Protocol):
    async def __call__(self, interaction: Interaction, values: List[str]): ...


class BaseDropdown(Select[Any]):
    def __init__(
        self,
        *,
        custom_id: str,
        options: Dict[str, str],
        dropdown_selected_callback: DropdownSelectedCallback,
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
        if not disabled and len(options) == 0:
            options = {"_no_options": "No options available!"}
            disabled = True

        if len(description or []) >= 25:
            raise ValueError("Description length must be less than 25")

        if description:
            if len(description) != len(options):
                raise ValueError(
                    "Description length must be the same as options length"
                )

        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            disabled=disabled,
            min_values=min_values,
            max_values=max_values,
            row=row,
        )

        emojis = emojis or {}

        if description:
            for choices, desc in zip(options.items(), description):
                value, label = choices
                self.add_option(
                    label=label, value=value, emoji=emojis.get(value), description=desc
                )
        else:
            for value, label in options.items():
                self.add_option(label=label, value=value, emoji=emojis.get(value))

        self.dropdown_selected_callback = dropdown_selected_callback

    async def callback(self, interaction: Interaction):
        await self.dropdown_selected_callback(
            interaction=interaction, values=self.values
        )
