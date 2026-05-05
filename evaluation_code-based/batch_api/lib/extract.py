from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCORE_KEYS = (
    "instruction_adherence",
    "content_preservation",
    "overall_alignment_score",
)


def _get_custom_id(record: dict[str, Any]) -> str | None:
    """Retrieve custom_id / key common to all providers."""
    return record.get("custom_id") or record.get("key")


def _strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks (for Qwen thinking models)."""
    import re
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _normalize_code_eval_obj(obj: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize code-evaluation JSON into flat score fields."""
    # Preferred schema:
    # {
    #   "metrics": {
    #     "Instruction Adherence": {"score": int, "reason": str},
    #     "Content Preservation": {"score": int, "reason": str}
    #   },
    #   "overall_alignment_score": int
    # }
    metrics = obj.get("metrics")
    if isinstance(metrics, dict):
        ia = metrics.get("Instruction Adherence")
        cp = metrics.get("Content Preservation")
        overall = obj.get("overall_alignment_score")
        if (
            isinstance(ia, dict)
            and isinstance(cp, dict)
            and isinstance(overall, int)
            and "score" in ia
            and "score" in cp
        ):
            try:
                return {
                    "instruction_adherence": int(ia["score"]),
                    "content_preservation": int(cp["score"]),
                    "overall_alignment_score": int(overall),
                    "instruction_adherence_reason": str(ia.get("reason", "")),
                    "content_preservation_reason": str(cp.get("reason", "")),
                }
            except (ValueError, TypeError):
                return None

    # Fallback: already-flat format
    if all(k in obj for k in SCORE_KEYS):
        try:
            return {
                "instruction_adherence": int(obj["instruction_adherence"]),
                "content_preservation": int(obj["content_preservation"]),
                "overall_alignment_score": int(obj["overall_alignment_score"]),
                "instruction_adherence_reason": str(
                    obj.get("instruction_adherence_reason", "")
                ),
                "content_preservation_reason": str(
                    obj.get("content_preservation_reason", "")
                ),
            }
        except (ValueError, TypeError):
            return None
    return None


def _parse_json_scores(text: str) -> dict[str, Any] | None:
    """Extract code-evaluation scores from a JSON string."""
    for t in (text.strip(), _strip_thinking(text)):
        try:
            obj = json.loads(t)
            if isinstance(obj, dict):
                normalized = _normalize_code_eval_obj(obj)
                if normalized is not None:
                    return normalized
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    return None


def extract_scores_openai(record: dict[str, Any]) -> dict[str, Any] | None:
    """Extract scores from an OpenAI chat/completions batch response."""
    try:
        content = (
            record["response"]["body"]["choices"][0]["message"]["content"]
        )
        return _parse_json_scores(content)
    except (KeyError, IndexError, TypeError):
        return None


def extract_scores_gemini(record: dict[str, Any]) -> dict[str, Any] | None:
    """Extract scores from a Gemini batch response."""
    try:
        parts = record["response"]["candidates"][0]["content"]["parts"]
        for part in reversed(parts):
            if "text" in part:
                scores = _parse_json_scores(part["text"])
                if scores:
                    return scores
    except (KeyError, IndexError, TypeError):
        pass
    return None


def extract_scores_claude(record: dict[str, Any]) -> dict[str, Any] | None:
    """Extract scores from a Claude batch response."""
    try:
        content = record["result"]["message"]["content"]
        for item in content:
            if not isinstance(item, dict):
                continue

            if item.get("type") == "tool_use":
                input_obj = item.get("input")
                if isinstance(input_obj, dict):
                    normalized = _normalize_code_eval_obj(input_obj)
                    if normalized is not None:
                        return normalized

            if item.get("type") == "text":
                scores = _parse_json_scores(item.get("text", ""))
                if scores:
                    return scores
    except (KeyError, IndexError, TypeError):
        pass
    return None


def extract_scores_from_record(
    record: dict[str, Any], provider: str
) -> tuple[str | None, dict[str, Any] | None]:
    """Extract (custom_id, scores) from a batch response record."""
    custom_id = _get_custom_id(record)
    if provider == "openai":
        scores = extract_scores_openai(record)
    elif provider == "google":
        scores = extract_scores_gemini(record)
    elif provider == "anthropic":
        scores = extract_scores_claude(record)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    return custom_id, scores


def extract_scores_from_jsonl(
    output_jsonl: Path, provider: str
) -> list[dict[str, Any]]:
    """Load a batch output JSONL and return a list of scores.

    Returns:
        [
          {
            "custom_id": ...,
            "instruction_adherence": ...,
            "content_preservation": ...,
            "overall_alignment_score": ...,
            "instruction_adherence_reason": ...,
            "content_preservation_reason": ...
          },
          ...
        ]
    """
    results: list[dict[str, Any]] = []
    with open(output_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            custom_id, scores = extract_scores_from_record(record, provider)
            if custom_id is None or scores is None:
                continue
            results.append({"custom_id": custom_id, **scores})
    return results
