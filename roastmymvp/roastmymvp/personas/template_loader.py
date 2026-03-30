"""Load industry-specific persona templates from YAML files."""

import os
from pathlib import Path

import yaml

from roastmymvp.personas.models import (
    Archetype,
    EvaluationStyle,
    PersonaProfile,
)
from roastmymvp.personas.irrationality import inject_irrationality
import random

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_ARCHETYPE_MAP = {a.value: a for a in Archetype}
_EVAL_MAP = {e.value: e for e in EvaluationStyle}


def list_templates() -> tuple[str, ...]:
    """List available industry template names."""
    return tuple(
        p.stem for p in _TEMPLATES_DIR.glob("*.yaml")
    )


def load_template(
    name: str, seed: int = 42
) -> tuple[PersonaProfile, ...]:
    """Load personas from an industry template YAML file."""
    path = _TEMPLATES_DIR / f"{name}.yaml"
    if not path.exists():
        available = ", ".join(list_templates())
        raise FileNotFoundError(
            f"Template '{name}' not found. Available: {available}"
        )

    with open(path) as f:
        data = yaml.safe_load(f)

    rng = random.Random(seed)
    personas: list[PersonaProfile] = []

    for p in data.get("personas", []):
        archetype = _ARCHETYPE_MAP.get(p.get("archetype", "pragmatist"), Archetype.PRAGMATIST)
        eval_style = _EVAL_MAP.get(p.get("evaluation_style", "task_driven"), EvaluationStyle.TASK_DRIVEN)

        personas.append(
            PersonaProfile(
                name=p["name"],
                age=p["age"],
                background=p["background"],
                tech_savvy=p["tech_savvy"],
                patience_seconds=p["patience"],
                language=p.get("language", "en"),
                has_alternative=p.get("has_alternative", False),
                alternative_name=p.get("alternative_name"),
                irrationality_mod=inject_irrationality(rng),
                archetype=archetype,
                evaluation_style=eval_style,
                goals=tuple(p.get("goals", ())),
                frustrations=tuple(p.get("frustrations", ())),
                context_of_use=p.get("context_of_use", ""),
                emotional_state=p.get("emotional_state", "neutral"),
            )
        )

    return tuple(personas)
