import socket

import pytest

from app.core.llm_url import validate_llm_base_url


def test_validate_llm_base_url_rejects_private_ip() -> None:
    with pytest.raises(ValueError, match="private"):
        validate_llm_base_url("http://127.0.0.1:11434")


def test_validate_llm_base_url_rejects_localhost_hostname() -> None:
    with pytest.raises(ValueError, match="localhost"):
        validate_llm_base_url("http://localhost:11434")


def test_validate_llm_base_url_rejects_metadata_host() -> None:
    with pytest.raises(ValueError, match="metadata"):
        validate_llm_base_url("http://metadata.google.internal/computeMetadata/v1/")


def test_validate_llm_base_url_accepts_https_host(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_getaddrinfo(host: str, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))]

    monkeypatch.setattr("app.core.llm_url.socket.getaddrinfo", fake_getaddrinfo)
    assert validate_llm_base_url("https://api.openai.com/v1") == "https://api.openai.com/v1"


def test_validate_llm_base_url_rejects_dns_to_private(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_getaddrinfo(host: str, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 0))]

    monkeypatch.setattr("app.core.llm_url.socket.getaddrinfo", fake_getaddrinfo)
    with pytest.raises(ValueError, match="resolve"):
        validate_llm_base_url("https://evil.example.com/v1")
