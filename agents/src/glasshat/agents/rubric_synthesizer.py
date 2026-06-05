"""RubricSynthesizer — official rules -> SynthesizedRubric (spec §4-§7).

Path A (preset_id) and Path D (custom_yaml) are deterministic and credential-free.
Path B (rules_url) lazily fetches the page then asks the LLM to synthesize. PDF
(Path C) is not supported in this build (use a preset, URL, or custom YAML). The
agent's behaviour *is* its prompt: ``prompts/rubric_synthesizer.md``.
"""

from __future__ import annotations

import ipaddress
import socket
from pathlib import Path
from urllib.parse import urlparse

import yaml
from glasshat.agents.types import EvaluationInput
from glasshat.rubric.models import SynthesizedRubric
from glasshat.rubric.presets import load_preset
from glasshat.rubric.validation import validate_custom_yaml
from glasshat.shared.config import Settings, get_settings
from glasshat.shared.enums import SourceKind
from glasshat.shared.errors import SynthesisError
from glasshat.shared.protocols import LlmClient
from pydantic import ValidationError

SYNTH_PROMPT_PATH = Path(__file__).parent / "prompts" / "rubric_synthesizer.md"


def _load_prompt() -> str:
    return SYNTH_PROMPT_PATH.read_text(encoding="utf-8")


async def synthesize_from_text(
    rules_text: str,
    llm: LlmClient,
    *,
    identifier: str,
    source_kind: SourceKind = SourceKind.URL,
) -> SynthesizedRubric:
    """Synthesize a rubric from raw rules text via the LLM (Paths B/C core)."""
    prompt = f"{_load_prompt()}\n\nRULES TEXT:\n{rules_text}"
    raw = await llm.generate(prompt, tier="pro")
    try:
        data = yaml.safe_load(raw)
        rubric = SynthesizedRubric.model_validate(data)
    except (yaml.YAMLError, ValidationError) as exc:
        raise SynthesisError(f"could not synthesize a valid rubric from source: {exc}") from exc
    rubric.source.identifier = identifier
    rubric.source.type = source_kind
    return rubric


async def synthesize(inp: EvaluationInput, llm: LlmClient) -> SynthesizedRubric:
    """Produce the SynthesizedRubric for an evaluation input.

    Dispatch order: preset_id -> custom_yaml -> rules_url -> rules_pdf_uri.
    """
    src = inp.rubric_source
    if src.get("preset_id"):
        return load_preset(src["preset_id"])
    if src.get("custom_yaml"):
        return validate_custom_yaml(yaml.safe_load(src["custom_yaml"]))
    if src.get("rules_url"):
        text = await _fetch_url(src["rules_url"])
        return await synthesize_from_text(text, llm, identifier=src["rules_url"])
    if src.get("rules_pdf_uri"):
        raise SynthesisError(
            "rules_pdf_uri is not supported in this build; use preset_id, rules_url, or custom_yaml"
        )
    raise SynthesisError(
        "no rubric source provided (one of preset_id, custom_yaml, rules_url, rules_pdf_uri)"
    )


_REDIRECT_STATUS = frozenset({301, 302, 303, 307, 308})


def _blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """True for any address an SSRF must never reach (loopback / private / cloud
    metadata 169.254.169.254 / reserved / multicast / unspecified)."""
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _resolved_ips(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    try:
        return [ipaddress.ip_address(host)]  # host is already a literal IP
    except ValueError:
        pass
    infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    out: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    for info in infos:
        try:
            out.append(ipaddress.ip_address(info[4][0]))
        except ValueError:  # pragma: no cover - getaddrinfo always yields parseable addrs
            continue
    return out


def assert_fetchable(url: str, settings: Settings | None = None) -> str:
    """SSRF gate for rules_url (M3): https-only, optional host allowlist, and a
    resolve-time block of private/loopback/metadata addresses. Returns the host.

    Raises :class:`SynthesisError` for any disallowed target. Redirects are not
    followed by the fetcher, so this check cannot be bypassed by a 3xx hop."""
    settings = settings or get_settings()
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise SynthesisError("rules_url must be an https:// URL (SSRF guard)")
    host = parsed.hostname
    if not host:
        raise SynthesisError("rules_url has no host (SSRF guard)")
    allow = [h.strip().lower() for h in settings.rules_url_allowed_hosts.split(",") if h.strip()]
    if allow and host.lower() not in allow:
        raise SynthesisError(f"rules_url host '{host}' is not in the allowlist (SSRF guard)")
    for ip in _resolved_ips(host):
        if _blocked_ip(ip):
            raise SynthesisError(
                "rules_url resolves to a private/loopback/metadata address (SSRF guard)"
            )
    return host


async def _fetch_url(url: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    assert_fetchable(url, settings)
    return await _stream_capped(url, settings)


async def _stream_capped(
    url: str, settings: Settings
) -> str:  # pragma: no cover - requires network
    import httpx

    # follow_redirects=False so a 3xx cannot re-target a just-validated host at an
    # internal address; the size cap bounds memory / cost abuse.
    async with (
        httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client,
        client.stream("GET", url) as resp,
    ):
        if resp.status_code in _REDIRECT_STATUS:
            raise SynthesisError("rules_url redirects are not followed (SSRF guard)")
        resp.raise_for_status()
        chunks: list[bytes] = []
        total = 0
        async for chunk in resp.aiter_bytes():
            total += len(chunk)
            if total > settings.rules_url_max_bytes:
                raise SynthesisError("rules_url response exceeds the size cap")
            chunks.append(chunk)
    return b"".join(chunks).decode("utf-8", errors="replace")
