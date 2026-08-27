import asgi
from uuid import uuid4
from workers import WorkerEntrypoint

from frameworks_and_drivers.cloudflare_context import reset_worker_env, set_worker_env
from frameworks_and_drivers.cloudflare_worker_controller import build_cloudflare_flow, build_cloudflare_security
from frameworks_and_drivers.fastapi_app import create_app
from frameworks_and_drivers.settings import settings_from_worker_env
from frameworks_and_drivers.structured_logging import StructuredLogger
from interface_adapters.controllers import ChatController
from frameworks_and_drivers.providers.cloudflare.security import InMemorySyntacticSanitizer


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        token = set_worker_env(self.env)
        request_fields = {
            "cf_ray": request.headers.get("cf-ray"),
            "method": request.method,
            "path": request.url.split("?", 1)[0],
        }
        logger = StructuredLogger(**request_fields)
        try:
            # Build the adapter at runtime so Wrangler vars are available to CORS/security.
            settings = settings_from_worker_env(self.env)
            sessions = getattr(self, "_sessions", None)
            if sessions is None:
                from frameworks_and_drivers.in_memory_session_repository import InMemorySessionRepository

                sessions = InMemorySessionRepository()
                self._sessions = sessions
            security = getattr(self, "_security", None)
            if security is None:
                security = build_cloudflare_security(settings)
                self._security = security
            request_id = str(uuid4())
            logger = StructuredLogger(request_id=request_id, **request_fields)
            logger.info("request_started")
            application = create_app(
                ChatController(
                    build_cloudflare_flow(logger, sessions),
                    InMemorySyntacticSanitizer(),
                ),
                security,
                settings,
                logger,
            )
            response = await asgi.fetch(application, request, self.env)
            logger.info("request_completed", status_code=response.status)
            return response
        except Exception as error:
            logger.error(
                "worker_request_failed",
                error_type=type(error).__name__,
            )
            raise
        finally:
            reset_worker_env(token)
