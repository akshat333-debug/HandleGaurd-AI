from __future__ import annotations

FORBIDDEN_IDENTITY = (
    "who is the worker",
    "employee name",
    "identify the person",
    "face of",
    "which employee",
    "worker id",
)
FORBIDDEN_DAMAGE = (
    "confirmed damage",
    "prove damage",
    "did it break",
    "guaranteed damage",
)
FORBIDDEN_PUNITIVE = (
    "fire them",
    "discipline",
    "write up the worker",
    "punish",
)


def blocked_reason(question: str) -> str | None:
    q = question.lower()
    if any(term in q for term in FORBIDDEN_IDENTITY):
        return (
            "I cannot identify workers. HandleGuard analyses behaviour and track IDs, not people."
        )
    if any(term in q for term in FORBIDDEN_DAMAGE):
        return (
            "Video risk events do not confirm product damage. A human must inspect the goods."
        )
    if any(term in q for term in FORBIDDEN_PUNITIVE):
        return "I cannot recommend disciplinary action. Use events as process-safety decision support only."
    return None
