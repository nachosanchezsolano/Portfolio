from types import SimpleNamespace

from frameworks_and_drivers.settings import settings_from_worker_env


def test_worker_settings_read_cloudflare_bindings() -> None:
    settings = settings_from_worker_env(
        SimpleNamespace(
            APP_ENV="production",
            ALLOWED_ORIGINS="https://nachosanchez.com.ar,https://www.nachosanchez.com.ar",
            RATE_LIMIT_REQUESTS="30",
            RATE_LIMIT_WINDOW_SECONDS="60",
            ADMIN_API_KEY="admin-secret",
        )
    )

    assert settings.app_env == "production"
    assert settings.origins == [
        "https://nachosanchez.com.ar",
        "https://www.nachosanchez.com.ar",
    ]
    assert settings.rate_limit_requests == 30
    assert settings.rate_limit_window_seconds == 60
    assert settings.admin_api_key == "admin-secret"


def test_worker_settings_convert_js_proxy_bindings() -> None:
    class JsProxyString:
        def to_py(self) -> str:
            return "https://nachosanchez.com.ar"

    settings = settings_from_worker_env(
        SimpleNamespace(ALLOWED_ORIGINS=JsProxyString())
    )

    assert settings.origins == ["https://nachosanchez.com.ar"]
