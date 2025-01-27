from discord import Embed, Color
from typing import Any, Optional, Tuple


class BaseEmbed(Embed):
    def __init__(
            self,
            *,
            title: str,
            description: Optional[str] = None,
            color: Tuple[int, int, int] = (0, 0, 0)
    ):
        super().__init__(
            title=title, description=description, color=Color.from_rgb(*color)
        )
    
    def add_field(self, *, name: Any, value: str = "", inline: bool = True):  # type: ignore
        super().add_field(name=name, value=value, inline=inline)
    
    def set_image(self, filename: str):  # type: ignore
        super().set_image(url=f"attachment://{filename}")