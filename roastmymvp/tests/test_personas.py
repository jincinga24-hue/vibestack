"""Tests for persona generator, irrationality, and template loader."""

import pytest

from roastmymvp.personas.models import (
    Archetype,
    EvaluationStyle,
    PersonaProfile,
)
from roastmymvp.personas.generator import (
    generate_default_personas,
    generate_custom_persona,
    generate_persona_variants,
)
from roastmymvp.personas.irrationality import inject_irrationality
from roastmymvp.personas.template_loader import list_templates, load_template
import random


class TestGenerateDefaultPersonas:
    def test_returns_20_personas(self):
        personas = generate_default_personas()
        assert len(personas) == 20

    def test_all_frozen(self):
        personas = generate_default_personas()
        for p in personas:
            with pytest.raises(AttributeError):
                p.name = "Changed"

    def test_diverse_ages(self):
        personas = generate_default_personas()
        ages = {p.age for p in personas}
        assert len(ages) >= 8

    def test_diverse_tech_savvy(self):
        personas = generate_default_personas()
        levels = {round(p.tech_savvy, 1) for p in personas}
        assert len(levels) >= 4

    def test_all_archetypes_represented(self):
        personas = generate_default_personas()
        archetypes = {p.archetype for p in personas}
        assert len(archetypes) >= 5  # at least 5 of 7 archetypes

    def test_diverse_evaluation_styles(self):
        personas = generate_default_personas()
        styles = {p.evaluation_style for p in personas}
        assert len(styles) >= 3

    def test_some_have_irrationality(self):
        personas = generate_default_personas()
        irrational = [p for p in personas if p.irrationality_mod is not None]
        # With seed=42 and 30% rate, expect roughly 6
        assert 2 <= len(irrational) <= 12

    def test_all_have_goals(self):
        personas = generate_default_personas()
        for p in personas:
            assert len(p.goals) >= 1

    def test_all_have_context(self):
        personas = generate_default_personas()
        for p in personas:
            assert len(p.context_of_use) > 0

    def test_all_have_emotional_state(self):
        personas = generate_default_personas()
        for p in personas:
            assert p.emotional_state != ""

    def test_backgrounds_are_rich(self):
        personas = generate_default_personas()
        for p in personas:
            # Rich backgrounds should be at least 50 chars
            assert len(p.background) >= 50, f"{p.name}'s background is too thin: {p.background}"

    def test_some_have_alternatives(self):
        personas = generate_default_personas()
        with_alt = [p for p in personas if p.has_alternative]
        without_alt = [p for p in personas if not p.has_alternative]
        assert len(with_alt) >= 5
        assert len(without_alt) >= 5

    def test_accessibility_personas_have_needs(self):
        personas = generate_default_personas()
        a11y = [p for p in personas if p.archetype == Archetype.ACCESSIBILITY]
        assert len(a11y) >= 1
        for p in a11y:
            assert p.accessibility_needs is not None


class TestGenerateCustomPersona:
    def test_creates_from_description(self):
        persona = generate_custom_persona(
            description="22-year-old actuarial student from China studying in Melbourne"
        )
        assert isinstance(persona, PersonaProfile)
        assert persona.age == 22

    def test_preserves_competitor(self):
        persona = generate_custom_persona(
            description="35-year-old product manager, already using competitor Notion"
        )
        assert persona.has_alternative is True
        assert persona.alternative_name is not None

    def test_infers_archetype_from_description(self):
        skeptic = generate_custom_persona("Skeptical CTO who's been burned by tools before")
        assert skeptic.archetype == Archetype.SKEPTIC

        advocate = generate_custom_persona("Excited early adopter who loves trying new things")
        assert advocate.archetype == Archetype.ADVOCATE

        confused = generate_custom_persona("Beginner who is new to programming")
        assert confused.archetype == Archetype.CONFUSED

    def test_has_goals(self):
        persona = generate_custom_persona("Senior engineer evaluating CI tools")
        assert len(persona.goals) >= 1

    def test_may_have_irrationality(self):
        # Run enough times that at least one should have irrationality
        has_irrational = False
        for i in range(20):
            p = generate_custom_persona(f"Test persona variant {i}")
            if p.irrationality_mod is not None:
                has_irrational = True
                break
        assert has_irrational


class TestGeneratePersonaVariants:
    def test_creates_n_variants(self):
        base = generate_custom_persona("25-year-old developer")
        variants = generate_persona_variants(base, count=5)
        assert len(variants) == 5

    def test_variants_have_unique_names(self):
        base = generate_custom_persona("25-year-old developer")
        variants = generate_persona_variants(base, count=5)
        names = {v.name for v in variants}
        assert len(names) == 5

    def test_variants_have_diverse_archetypes(self):
        base = generate_custom_persona("25-year-old developer")
        variants = generate_persona_variants(base, count=7)
        archetypes = {v.archetype for v in variants}
        assert len(archetypes) >= 3  # should cycle through archetypes

    def test_variants_have_diverse_emotions(self):
        base = generate_custom_persona("25-year-old developer")
        variants = generate_persona_variants(base, count=5)
        emotions = {v.emotional_state for v in variants}
        assert len(emotions) >= 2


class TestIrrationalityInjection:
    def test_returns_none_sometimes(self):
        rng = random.Random(0)
        results = [inject_irrationality(rng) for _ in range(100)]
        none_count = sum(1 for r in results if r is None)
        assert none_count > 50  # ~70% should be None

    def test_returns_string_sometimes(self):
        rng = random.Random(0)
        results = [inject_irrationality(rng) for _ in range(100)]
        str_count = sum(1 for r in results if r is not None)
        assert str_count > 15  # ~30% should be strings

    def test_custom_injection_rate(self):
        rng = random.Random(0)
        results = [inject_irrationality(rng, injection_rate=1.0) for _ in range(10)]
        assert all(r is not None for r in results)

    def test_zero_injection_rate(self):
        rng = random.Random(0)
        results = [inject_irrationality(rng, injection_rate=0.0) for _ in range(10)]
        assert all(r is None for r in results)


class TestTemplateLoader:
    def test_list_templates(self):
        templates = list_templates()
        assert "saas" in templates
        assert "ecommerce" in templates
        assert "education" in templates
        assert "game" in templates

    def test_load_saas_template(self):
        personas = load_template("saas")
        assert len(personas) >= 3
        for p in personas:
            assert isinstance(p, PersonaProfile)
            assert len(p.goals) >= 1
            assert len(p.frustrations) >= 1

    def test_load_ecommerce_template(self):
        personas = load_template("ecommerce")
        assert len(personas) >= 3

    def test_load_nonexistent_template_raises(self):
        with pytest.raises(FileNotFoundError) as exc_info:
            load_template("nonexistent")
        assert "Available:" in str(exc_info.value)

    def test_template_personas_have_archetypes(self):
        personas = load_template("game")
        archetypes = {p.archetype for p in personas}
        assert len(archetypes) >= 2
