from fastapi import Header, HTTPException, Request

from application.ports.security_ports import RequestSecurity, SecurityError


class RequestSecurityController:
    """Translates HTTP request identity into the framework-independent security port."""

    def __init__(self, policy: RequestSecurity) -> None:
        self._policy = policy

    async def protect(
        self,
        request: Request,
        x_api_key: str | None = Header(default=None),
    ) -> None:
        client_id = request.client.host if request.client else "unknown"
        try:
            await self._policy.check(client_id, x_api_key)
        except SecurityError as error:
            status_code = 429 if "rate limit" in str(error) else 401
            raise HTTPException(status_code=status_code, detail=str(error)) from error
