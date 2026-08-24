import asyncio

import pytest

from application.ports.security_ports import SecurityError
from frameworks_and_drivers.security.in_memory import InMemoryRequestSecurity


def test_security_accepts_correct_api_key() -> None:
    policy = InMemoryRequestSecurity("secret", max_requests=3, window_seconds=60)
    asyncio.run(policy.check("client-1", "secret"))


@pytest.mark.parametrize("credential", [None, "wrong"])
def test_security_rejects_missing_or_invalid_api_key(credential: str | None) -> None:
    policy = InMemoryRequestSecurity("secret", max_requests=3, window_seconds=60)
    with pytest.raises(SecurityError, match="invalid api key"):
        asyncio.run(policy.check("client-1", credential))


def test_invalid_api_key_does_not_consume_rate_limit() -> None:
    policy = InMemoryRequestSecurity("secret", max_requests=1, window_seconds=60)
    with pytest.raises(SecurityError, match="invalid api key"):
        asyncio.run(policy.check("client-1", "wrong"))
    asyncio.run(policy.check("client-1", "secret"))


def test_security_allows_requests_when_api_key_is_disabled() -> None:
    policy = InMemoryRequestSecurity("", max_requests=1, window_seconds=60)
    asyncio.run(policy.check("client-1", None))


def test_security_rejects_requests_after_rate_limit() -> None:
    policy = InMemoryRequestSecurity("", max_requests=2, window_seconds=60)
    asyncio.run(policy.check("client-1"))
    asyncio.run(policy.check("client-1"))

    with pytest.raises(SecurityError, match="rate limit exceeded"):
        asyncio.run(policy.check("client-1"))


def test_rate_limit_is_scoped_per_client() -> None:
    policy = InMemoryRequestSecurity("", max_requests=1, window_seconds=60)
    asyncio.run(policy.check("client-1"))
    asyncio.run(policy.check("client-2"))
