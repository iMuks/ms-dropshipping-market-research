"""Shared Claude Agent SDK plumbing for specialists (DRY).

Every specialist follows the same shape: run a single agent query with
WebSearch + WebFetch, collect the assistant's text, and pull a final
```json block out of the transcript. Centralizing that here keeps each
specialist file focused on its *prompt and schema*, not SDK mechanics
(CONVENTIONS.md: DRY — one place to change retry/parse/extract behavior).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from claude_agent_sdk import ClaudeAgentOptions, query
from pydantic import ValidationError

from niche_research.brief.models import EvidenceURL

_JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)

DEFAULT_TOOLS: tuple[str, ...] = ("WebSearch", "WebFetch")


async def run_specialist_query(
    *,
    system_prompt: str,
    prompt: str,
    model: str,
    max_turns: int,
    allowed_tools: tuple[str, ...] = DEFAULT_TOOLS,
) -> dict:
    """Run one specialist agent loop and return its parsed JSON block.

    Raises ``ValueError`` if the model never produced a valid ```json block —
    the caller (or orchestrator) decides whether that aborts the section or
    just marks it unavailable.
    """
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=list(allowed_tools),
        model=model,
        max_turns=max_turns,
    )

    chunks: list[str] = []
    async for message in query(prompt=prompt, options=options):
        text = extract_text(message)
        if text:
            chunks.append(text)

    return parse_json_block("\n".join(chunks))


def extract_text(message: object) -> str:
    """Best-effort text extraction from an SDK message object.

    The SDK uses typed message objects; we duck-type for ``content`` or
    ``text`` to stay resilient across minor SDK versions.
    """
    if isinstance(message, str):
        return message
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            text = getattr(block, "text", None) or (
                block.get("text") if isinstance(block, dict) else None
            )
            if text:
                parts.append(text)
        return "".join(parts)
    text = getattr(message, "text", None)
    return text if isinstance(text, str) else ""


def parse_json_block(transcript: str) -> dict:
    """Extract the final ```json block. Raise if the model didn't produce one."""
    matches = _JSON_BLOCK_RE.findall(transcript)
    if not matches:
        raise ValueError(
            "specialist: model did not return a ```json block. "
            "Transcript was:\n" + transcript[-2000:]
        )
    try:
        return json.loads(matches[-1])
    except json.JSONDecodeError as e:
        raise ValueError(
            f"specialist: found a ```json block but it was not valid JSON ({e}). "
            "Block was:\n" + matches[-1][-2000:]
        ) from e


def build_evidence(items: object) -> list[EvidenceURL]:
    """Build EvidenceURL list defensively.

    A single malformed URL from the model must not discard an otherwise-complete
    section. Skip bad entries rather than letting HttpUrl validation abort the
    whole investigation.
    """
    evidence: list[EvidenceURL] = []
    if not isinstance(items, list):
        return evidence
    for item in items:
        if not (isinstance(item, dict) and item.get("url")):
            continue
        try:
            evidence.append(
                EvidenceURL(
                    url=item["url"],
                    fetched_at=datetime.now(timezone.utc),
                    note=item.get("note", ""),
                )
            )
        except ValidationError:
            continue
    return evidence
