"""SSRF gate tests for rules_url (M3) — the network-free validation surface."""

from __future__ import annotations

import ipaddress

import pytest
from glasshat.agents.rubric_synthesizer import _blocked_ip, assert_fetchable
from glasshat.shared.config import Settings
from glasshat.shared.errors import SynthesisError


def _settings(**kw: object) -> Settings:
    return Settings(_env_file=None, **kw)  # type: ignore[call-arg]


def test_rejects_non_https_scheme() -> None:
    with pytest.raises(SynthesisError, match="https"):
        assert_fetchable("http://example.com/rules", _settings())


def test_rejects_loopback_literal() -> None:
    with pytest.raises(SynthesisError, match="private/loopback/metadata"):
        assert_fetchable("https://127.0.0.1/rules", _settings())


def test_rejects_cloud_metadata_ip() -> None:
    # 169.254.169.254 — the classic SSRF target — is link-local → blocked.
    with pytest.raises(SynthesisError, match="private/loopback/metadata"):
        assert_fetchable("https://169.254.169.254/latest/meta-data/", _settings())


def test_rejects_private_rfc1918_literal() -> None:
    with pytest.raises(SynthesisError, match="private/loopback/metadata"):
        assert_fetchable("https://10.0.0.5/rules", _settings())


def test_rejects_localhost_name() -> None:
    # Resolves (via /etc/hosts, no network) to a loopback address → blocked.
    with pytest.raises(SynthesisError):
        assert_fetchable("https://localhost/rules", _settings())


def test_allowlist_rejects_unlisted_host() -> None:
    s = _settings(rules_url_allowed_hosts="rules.devpost.com")
    with pytest.raises(SynthesisError, match="allowlist"):
        assert_fetchable("https://evil.example.com/rules", s)


def test_allows_listed_public_host_literal_ip() -> None:
    # A public literal IP (example.com's address) needs no DNS, so the check is
    # hermetic: allow-listed + public → returns the host unchanged.
    s = _settings(rules_url_allowed_hosts="93.184.216.34")
    assert assert_fetchable("https://93.184.216.34/rules", s) == "93.184.216.34"


def test_unresolvable_host_raises_synthesis_error() -> None:
    # The reserved `.invalid` TLD (RFC 6761) never resolves → gaierror is mapped to
    # a clean SynthesisError, not an unhandled internal exception.
    with pytest.raises(SynthesisError, match="could not be resolved"):
        assert_fetchable("https://no-such-host.invalid/rules", _settings())


def test_blocked_ip_predicate() -> None:
    assert _blocked_ip(ipaddress.ip_address("127.0.0.1"))
    assert _blocked_ip(ipaddress.ip_address("169.254.169.254"))
    assert _blocked_ip(ipaddress.ip_address("::1"))
    assert _blocked_ip(ipaddress.ip_address("10.1.2.3"))
    assert not _blocked_ip(ipaddress.ip_address("93.184.216.34"))  # example.com public
