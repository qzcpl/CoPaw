"""
CoPaw Server Routes
"""
from . import auth
from . import callid
from . import bot
from . import tenant
from . import queue
from . import monitor
from . import routing
from . import gray_release
from . import chat

__all__ = [
    "auth",
    "callid",
    "bot",
    "tenant",
    "queue",
    "monitor",
    "routing",
    "gray_release",
    "chat",
]
