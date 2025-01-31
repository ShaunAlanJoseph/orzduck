from discord import Message, Embed, File, AllowedMentions
from discord.ui import View
from typing import Optional, List, Dict, Any

from utils.context_manager import ctx_mgr


class Messenger:
    @staticmethod
    async def send_message_new(
        *,
        content: Optional[str] = None,
        embed: Optional[Embed] = None,
        view: Optional[View] = None,
        file: Optional[File] = None,
        files: Optional[List[File]] = None,
        mention_author: bool = False,
    ) -> Message:
        interaction = ctx_mgr().get_init_interaction()
        message = ctx_mgr().get_active_msg()

        # Merge into `files`
        files = (files or []) + ([file] if file else [])

        allowed_mentions = (
            AllowedMentions.all() if mention_author else AllowedMentions.none()
        )
        kwargs: Dict[str, Any] = {}
        for kwarg in ["content", "embed", "view", "files"]:
            if locals()[kwarg]:
                kwargs[kwarg] = locals()[kwarg]

        if message is not None:
            message = await message.reply(**kwargs, allowed_mentions=allowed_mentions)

        elif not interaction.response.is_done():
            message = await interaction.response.send_message(
                **kwargs, allowed_mentions=allowed_mentions
            )
            message = await interaction.original_response()
        
        else:
            message = await interaction.followup.send(
                **kwargs, allowed_mentions=allowed_mentions, wait=True
            )
        
        message = await message.channel.fetch_message(message.id)

        ctx_mgr().set_active_msg(message)
        ctx_mgr().set_send_new_msg(False)
        return message

    @staticmethod
    async def send_message(
        *,
        content: Optional[str] = None,
        embed: Optional[Embed] = None,
        view: Optional[View] = None,
        file: Optional[File] = None,
        files: Optional[List[File]] = None,
        mention_author: bool = False,
    ) -> Message:
        message = ctx_mgr().get_active_msg()

        # Edit the old message
        if message is not None and not ctx_mgr().get_send_new_msg():
            # Merge into `files`
            files = (files or []) + ([file] if file else [])

            allowed_mentions = (
                AllowedMentions.all() if mention_author else AllowedMentions.none()
            )

            message = await message.edit(
                content=content,
                embed=embed,
                view=view,
                attachments=files,
                allowed_mentions=allowed_mentions,
            )
            ctx_mgr().set_active_msg(message)
            ctx_mgr().set_send_new_msg(False)
            return message

        # Send a new message
        else:
            return await Messenger.send_message_new(
                content=content,
                embed=embed,
                view=view,
                file=file,
                files=files,
                mention_author=mention_author,
            )

    @staticmethod
    async def send_message_no_reset(
        *,
        content: Optional[str] = None,
        embed: Optional[Embed] = None,
        view: Optional[View] = None,
        file: Optional[File] = None,
        files: Optional[List[File]] = None,
        mention_author: bool = False,
    ) -> Message:
        message = ctx_mgr().get_active_msg()

        # Edit the old message
        if message is not None and not ctx_mgr().get_send_new_msg():
            # Merge into `files`
            files = (files or []) + ([file] if file else [])
            attachments = files  # type: ignore
            allowed_mentions = (
                AllowedMentions.all() if mention_author else AllowedMentions.none()
            )

            kwargs: Dict[str, Any] = {}
            for kwarg in ["content", "embed", "view", "attachments"]:
                if locals()[kwarg]:  # has to exclude None and []
                    kwargs[kwarg] = locals()[kwarg]
            message = await message.edit(**kwargs, allowed_mentions=allowed_mentions)

            ctx_mgr().set_active_msg(message)
            ctx_mgr().set_send_new_msg(False)
            return message

        # Send a new message
        else:
            return await Messenger.send_message_new(
                content=content,
                embed=embed,
                view=view,
                file=file,
                files=files,
                mention_author=mention_author,
            )

    @staticmethod
    async def send_message_ephemeral(
        *,
        content: Optional[str] = None,
        embed: Optional[Embed] = None,
        view: Optional[View] = None,
        file: Optional[File] = None,
        files: Optional[List[File]] = None,
        mention_author: bool = False,
    ):
        interaction = ctx_mgr().get_init_interaction()
        assert interaction is not None and interaction.response.is_done()

        # Merge into `files`
        files = (files or []) + ([file] if file else [])

        allowed_mentions = (
            AllowedMentions.all() if mention_author else AllowedMentions.none()
        )
        kwargs: Dict[str, Any] = {}
        for kwarg in ["content", "embed", "view", "files"]:
            if locals()[kwarg]:
                kwargs[kwarg] = locals()[kwarg]

        await interaction.followup.send(
            **kwargs, allowed_mentions=allowed_mentions, ephemeral=True
        )
