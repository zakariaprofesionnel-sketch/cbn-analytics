"""Orchestrator for Agent IA CBN."""

from __future__ import annotations

from typing import Dict, Any, List

from .context import build_agent_context
from .rules import generate_recommendations


def run_decision_agent() -> Dict[str, Any]:
    """Build context, generate recommendations, return a structured payload."""
    context = build_agent_context()
    if context.get("status") != "ok":
        return {
            "status": context.get("status", "error"),
            "message": context.get("message", "Contexte indisponible."),
            "signals": {},
            "recommendations": [],
        }

    recommendations = generate_recommendations(context)

    return {
        "status": "ok",
        "message": "Recommandations générées.",
        "signals": context["signals"],
        "recommendations": recommendations,
    }

