"""Logging setup that enforces the security posture in ARCHITECTURE.md §7:

  - **No verbose access logging.** uvicorn's per-request access log is disabled
    (it would log method + path + client for every request).
  - **PII is scrubbed** from any log line. No log should contain task content,
    pantry, pasted scam content, spending/bill/goal details, lifeline message
    bodies, emails, phone numbers, or bearer tokens.

This is defense-in-depth: capability code must also avoid logging user content,
but if something slips through, the filter redacts common PII shapes before the
line reaches stdout (Cloud Run ships stdout to Cloud Logging).
"""

import logging
import re
from logging.config import dictConfig

# Simple (non-callable) redactions, applied first.
_PII_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]+"), "Bearer [REDACTED]"),
    (re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), "[EMAIL]"),
]

# Phone-like sequences. Matching candidates broadly then confirming by digit
# count avoids over-redacting dotted IPs (0.0.0.0), ports, and version strings —
# a real phone number carries 10–15 digits.
_PHONE_CANDIDATE = re.compile(r"\+?[\d][\d\s().\-]{7,}\d")


def _redact_phone(match: re.Match[str]) -> str:
    digits = re.sub(r"\D", "", match.group(0))
    return "[PHONE]" if 10 <= len(digits) <= 15 else match.group(0)


class PIIScrubFilter(logging.Filter):
    """Redacts common PII shapes from the formatted message and args."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True
        for pattern, repl in _PII_PATTERNS:
            msg = pattern.sub(repl, msg)
        msg = _PHONE_CANDIDATE.sub(_redact_phone, msg)
        record.msg = msg
        record.args = ()
        return True


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"pii": {"()": PIIScrubFilter}},
            "formatters": {
                "plain": {"format": "%(levelname)s %(name)s %(message)s"},
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "formatter": "plain",
                    "filters": ["pii"],
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"handlers": ["stdout"], "level": "INFO"},
            "loggers": {
                # Keep startup/error logs, drop per-request access logs entirely.
                "uvicorn.access": {"handlers": [], "level": "CRITICAL", "propagate": False},
                "uvicorn.error": {"handlers": ["stdout"], "level": "INFO", "propagate": False},
            },
        }
    )
