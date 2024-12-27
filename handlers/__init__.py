from .admin import admin_router
from .creators import creators_router
from .tasks import user_router
from .common import common_router
from .groups import chat_router

routers = [admin_router, chat_router, creators_router, user_router, common_router]
