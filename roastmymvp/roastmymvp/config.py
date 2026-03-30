"""YAML config loader for .ai-beta-test.yaml."""

import os
from dataclasses import dataclass, field

import yaml


@dataclass(frozen=True)
class Config:
    personas: int = 20
    custom_personas: tuple[str, ...] = field(default_factory=tuple)
    max_concurrent: int = 5
    output_file: str = "FEEDBACK-REPORT.md"


def load_config(config_path: str | None = None) -> Config:
    """Load config from YAML file, falling back to defaults."""
    path = config_path or ".ai-beta-test.yaml"

    if not os.path.exists(path):
        return Config()

    with open(path) as f:
        data = yaml.safe_load(f) or {}

    return Config(
        personas=data.get("personas", 20),
        custom_personas=tuple(data.get("custom_personas", ())),
        max_concurrent=data.get("max_concurrent", 5),
        output_file=data.get("output_file", "FEEDBACK-REPORT.md"),
    )
