"""Public Worker: the AI assistant remains preserved in experimental_worker.py."""
import asgi
from workers import WorkerEntrypoint

from frameworks_and_drivers.public_portfolio_app import app

# Chatbot de IA desactivado temporalmente. Implementación conservada para pruebas
# y futura reintegración. Experimental registration (not imported or executed):
# from experimental_worker import Default


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)
