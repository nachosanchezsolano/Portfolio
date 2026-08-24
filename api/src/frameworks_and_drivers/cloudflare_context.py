from contextvars import ContextVar
from typing import Any


_worker_env: ContextVar[Any] = ContextVar("worker_env")


def set_worker_env(env: Any):
    return _worker_env.set(env)


def reset_worker_env(token: Any) -> None:
    _worker_env.reset(token)


def get_worker_env() -> Any:
    try:
        return _worker_env.get()
    except LookupError as error:
        raise RuntimeError("Cloudflare Worker environment is not available") from error


def to_python(value: Any) -> Any:
    """Convert a Pyodide JavaScript proxy when running inside Workers."""
    converter = getattr(value, "to_py", None)
    return converter() if converter else value
