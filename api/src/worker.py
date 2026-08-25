import asgi
from workers import WorkerEntrypoint

from frameworks_and_drivers.cloudflare_context import reset_worker_env, set_worker_env
from frameworks_and_drivers.cloudflare_worker_controller import build_cloudflare_flow, build_cloudflare_security
from frameworks_and_drivers.fastapi_app import create_app
from frameworks_and_drivers.settings import settings_from_worker_env
from interface_adapters.controllers import ChatController
from frameworks_and_drivers.providers.cloudflare.security import InMemorySyntacticSanitizer


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        token = set_worker_env(self.env)
        try:
            # Build the adapter at runtime so Wrangler vars are available to CORS/security.
            settings = settings_from_worker_env(self.env)
            application = create_app(
                ChatController(build_cloudflare_flow(), InMemorySyntacticSanitizer()),
                build_cloudflare_security(settings),
                settings,
            )
            return await asgi.fetch(application, request, self.env)
        finally:
            reset_worker_env(token)
