import asgi
from workers import WorkerEntrypoint

from frameworks_and_drivers.cloudflare_context import reset_worker_env, set_worker_env
from frameworks_and_drivers.cloudflare_worker_controller import build_cloudflare_flow, build_cloudflare_security
from frameworks_and_drivers.fastapi_app import create_app
from interface_adapters.controllers import ChatController
from frameworks_and_drivers.providers.cloudflare.security import InMemorySyntacticSanitizer


# The HTTP contract and all domain/application code stay in FastAPI.
app = create_app(
    ChatController(build_cloudflare_flow(), InMemorySyntacticSanitizer()),
    build_cloudflare_security(),
)


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        token = set_worker_env(self.env)
        try:
            return await asgi.fetch(app, request, self.env)
        finally:
            reset_worker_env(token)
