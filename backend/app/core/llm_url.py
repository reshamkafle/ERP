"""Validate LLM base URLs to reduce SSRF risk."""

import socket
from ipaddress import ip_address
from urllib.parse import urlparse

from app.core.config import get_settings

# Hostnames that must never be used as LLM endpoints (metadata, local services).
_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "metadata",
        "metadata.google.internal",
        "metadata.google",
        "kubernetes.default.svc",
    }
)


def _is_blocked_ip(host: str) -> bool:
    try:
        addr = ip_address(host)
    except ValueError:
        return False
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
    )


def _hostname_blocked(hostname: str) -> bool:
    host = hostname.lower().rstrip(".")
    if host in _BLOCKED_HOSTNAMES:
        return True
    if host.endswith(".localhost") or host.endswith(".local"):
        return True
    if host.startswith("metadata.") or host.endswith(".metadata.google.internal"):
        return True
    return False


def _resolve_and_check_ips(hostname: str) -> None:
    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"Cannot resolve LLM host {hostname!r}") from exc
    if not infos:
        raise ValueError(f"Cannot resolve LLM host {hostname!r}")
    for info in infos:
        ip = info[4][0]
        if _is_blocked_ip(ip):
            raise ValueError(
                "LLM_BASE_URL must not resolve to private, loopback, or link-local addresses"
            )


def validate_llm_base_url(url: str) -> str:
    """Return normalized base URL or raise ValueError if disallowed."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise ValueError("LLM_BASE_URL must use http or https")
    if not parsed.hostname:
        raise ValueError("LLM_BASE_URL must include a hostname")

    host = parsed.hostname.lower()
    settings = get_settings()
    allowed = settings.llm_allowed_host_list
    if allowed and host not in allowed:
        raise ValueError(f"LLM host {host!r} is not in LLM_ALLOWED_HOSTS")

    if _hostname_blocked(host):
        raise ValueError("LLM_BASE_URL must not target localhost or internal metadata hosts")

    if _is_blocked_ip(host):
        raise ValueError("LLM_BASE_URL must not target private or loopback addresses")

    _resolve_and_check_ips(host)

    return url.rstrip("/")
