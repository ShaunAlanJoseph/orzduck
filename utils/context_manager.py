from contextvars import ContextVar
from logging import info
from discord import Message, Interaction
from typing import Optional


class ContextManager:
    _instance = None

    @classmethod
    def setup_context_manager(cls):
        cls._instance = cls()
        info("ContextManager has been setup.")
    
    @classmethod
    def get_instance(cls):
        assert cls._instance is not None, "ContextManager has not been setup."
        return cls._instance
    
    def __init__(self):
        self._init_interaction: ContextVar[Optional[Interaction]] = ContextVar("InitInteraction", default=None)
        self._active_msg: ContextVar[Optional[Message]] = ContextVar("ActiveMsg", default=None)
        self._send_new_msg: ContextVar[bool] = ContextVar("SendNewMsg", default=False)
    
    def set_init_interaction(self, interaction: Interaction):
        self._init_interaction.set(interaction)
    
    def get_init_interaction(self) -> Interaction:
        interaction = self._init_interaction.get()
        assert interaction is not None, "InitInteraction is not set."
        return interaction
    
    def get_user_id(self) -> int:
        return self.get_init_interaction().user.id
    
    def set_active_msg(self, message: Message):
        self._active_msg.set(message)
    
    def reset_active_msg(self):
        self._active_msg.set(None)

    def get_active_msg(self) -> Optional[Message]:
        return self._active_msg.get()
    
    def set_send_new_msg(self, send_new_msg: bool):
        self._send_new_msg.set(send_new_msg)
    
    def get_send_new_msg(self) -> bool:
        return self._send_new_msg.get()


def ctx_mgr() -> ContextManager:
    return ContextManager.get_instance()