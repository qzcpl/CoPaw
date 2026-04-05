# -*- coding: utf-8 -*-
"""API routers."""
from fastapi import APIRouter

from .agent import router as agent_router
from .agents import router as agents_router
from .bots import router as bots_router
from .callid import router as callid_router
from .channels import router as channels_router
from .chat import router as chat_router
from .config import router as config_router
from .gray_release import router as gray_release_router
from .local_models import router as local_models_router
from .monitor import router as monitor_router
from .providers import router as providers_router
from .queue import router as queue_router
from .routing import router as routing_router
from .skills import router as skills_router
from .skills_stream import router as skills_stream_router
from .tenant import router as tenant_router
from .workspace import router as workspace_router
from .envs import router as envs_router
from .mcp import router as mcp_router
from .tools import router as tools_router
from ..crons.api import router as cron_router
from ..runner.api import router as runner_router
from .console import router as console_router
from .token_usage import router as token_usage_router
from .auth import router as auth_router
from .messages import router as messages_router
from .files import router as files_router
from .settings import router as settings_router

router = APIRouter()

router.include_router(agents_router)
router.include_router(agent_router)
router.include_router(bots_router)
router.include_router(callid_router)
router.include_router(channels_router)
router.include_router(chat_router)
router.include_router(config_router)
router.include_router(console_router)
router.include_router(cron_router)
router.include_router(gray_release_router)
router.include_router(local_models_router)
router.include_router(mcp_router)
router.include_router(messages_router)
router.include_router(monitor_router)
router.include_router(providers_router)
router.include_router(queue_router)
router.include_router(routing_router)
router.include_router(runner_router)
router.include_router(skills_router)
router.include_router(skills_stream_router)
router.include_router(tenant_router)
router.include_router(tools_router)
router.include_router(workspace_router)
router.include_router(envs_router)
router.include_router(token_usage_router)
router.include_router(auth_router)
router.include_router(files_router)
router.include_router(settings_router)


def create_agent_scoped_router() -> APIRouter:
    """Create agent-scoped router that wraps existing routers.

    Returns:
        APIRouter with all routers mounted under /agents/{agentId}/
    """
    from .agent_scoped import create_agent_scoped_router as _create

    return _create()


__all__ = ["router", "create_agent_scoped_router"]
