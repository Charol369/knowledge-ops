"""Prompt Injection 检测（防御纵深第 1 层）

Day6 04_guardrails.py 已演示。这里抽出来给业务调用。

生产防御纵深（6 层，详见 notes/day6/NOTES.md）：
  1. 输入层关键词（本文件）
  2. Prompt 层 XML 隔离
  3. 模型层低温度 + 强 system prompt
  4. 输出层 LLM-as-judge
  5. 业务层审计 trace
  6. 持续维护攻击库
"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal
import re
import unicodedata

from src.observability.metrics import business_metrics

DANGER_PATTERNS = [
    "ignore previous", "ignore above", "disregard previous", "disregard the above",
    "forget your instructions",
    "你忘记之前的指令", "忽略之前的指令", "忽略上面的",
    "现在你是", "请重新扮演", "重置你的角色",
    "system prompt is", "what is your system prompt", "你的 system prompt",
]

_CONFUSABLE_TRANSLATION = str.maketrans(
    {
        "а": "a",
        "А": "A",
        "е": "e",
        "Е": "E",
        "і": "i",
        "І": "I",
        "о": "o",
        "О": "O",
        "р": "p",
        "Р": "P",
        "с": "c",
        "С": "C",
        "х": "x",
        "Х": "X",
        "у": "y",
        "У": "Y",
    }
)


@dataclass(frozen=True)
class InjectionDetectionResult:
    is_injection: bool
    reason: str = ""
    level: Literal["local", "model_judge"] = "local"
    normalized_text: str = ""
    blocked_reason: str | None = None


def normalize_guardrail_text(text: str) -> str:
    """Normalize user input before local guardrail matching."""
    normalized = unicodedata.normalize("NFKC", text).translate(_CONFUSABLE_TRANSLATION)
    normalized = normalized.casefold()
    return re.sub(r"\s+", " ", normalized).strip()


def detect_injection(user_input: str) -> tuple[bool, str]:
    """关键词层注入检测。返回 (是否注入, 命中关键词)"""
    lower = normalize_guardrail_text(user_input)
    for p in DANGER_PATTERNS:
        normalized_pattern = normalize_guardrail_text(p)
        if normalized_pattern in lower:
            return True, p
    return False, ""


def detect_injection_two_level(
    user_input: str,
    model_judge: Callable[[str], tuple[bool, str] | bool] | None = None,
    require_model_judge: bool = False,
    trace_id: str | None = None,
) -> InjectionDetectionResult:
    """Run local guardrail first, then optional injected model-judge callable.

    Sprint 4 local acceptance must not require a real model/API key. The second
    level is therefore dependency-injected and reports a precise blocked reason
    when explicitly requested without a local callable.
    """
    normalized = normalize_guardrail_text(user_input)
    is_local_injection, reason = detect_injection(user_input)
    if is_local_injection:
        business_metrics.record_guardrail_decision(
            is_injection=True,
            level="local",
            blocked=True,
            trace_id=trace_id,
        )
        return InjectionDetectionResult(
            is_injection=True,
            reason=reason,
            level="local",
            normalized_text=normalized,
        )

    if model_judge is None:
        if require_model_judge:
            business_metrics.record_guardrail_decision(
                is_injection=False,
                level="model_judge",
                blocked=True,
                trace_id=trace_id,
            )
            return InjectionDetectionResult(
                is_injection=False,
                level="model_judge",
                normalized_text=normalized,
                blocked_reason=(
                    "Model judge unavailable: no local judge callable was provided and "
                    "no real API key is required for Sprint 4."
                ),
            )
        business_metrics.record_guardrail_decision(
            is_injection=False,
            level="local",
            blocked=False,
            trace_id=trace_id,
        )
        return InjectionDetectionResult(
            is_injection=False,
            level="local",
            normalized_text=normalized,
        )

    judge_result = model_judge(normalized)
    if isinstance(judge_result, tuple):
        is_injection, judge_reason = judge_result
    else:
        is_injection, judge_reason = bool(judge_result), ""
    business_metrics.record_guardrail_decision(
        is_injection=bool(is_injection),
        level="model_judge",
        blocked=bool(is_injection),
        trace_id=trace_id,
    )
    return InjectionDetectionResult(
        is_injection=bool(is_injection),
        reason=str(judge_reason),
        level="model_judge",
        normalized_text=normalized,
    )
