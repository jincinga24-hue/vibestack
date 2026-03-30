"""Apply evolved genes back into live personas.

This is where evolution meets reality — mutated genes replace default
traits so each run uses the latest evolved version of each persona.
"""

from roastmymvp.evolution.genes import GenePool, PersonaGenome
from roastmymvp.vc.models import VCPersona, VCArchetype
from roastmymvp.vc.personas import DEFAULT_VC_PANEL
from roastmymvp.personas.models import (
    Archetype,
    EvaluationStyle,
    PersonaProfile,
)
from roastmymvp.personas.generator import generate_default_personas


def get_evolved_vc_panel() -> tuple[VCPersona, ...]:
    """Get the VC panel with evolved genes applied.

    If a VC has evolved genes, use those. Otherwise fall back to defaults.
    Dead VCs are replaced by evolved offspring.
    """
    pool = GenePool()
    evolved: list[VCPersona] = []

    for default_vc in DEFAULT_VC_PANEL:
        genome = pool.get(default_vc.name)

        if genome and genome.alive:
            # Apply evolved genes
            evolved.append(_apply_vc_genes(default_vc, genome))
        elif genome and not genome.alive:
            # This VC was killed — skip it
            continue
        else:
            # No gene data — use default
            evolved.append(default_vc)

    # Add any evolved offspring (born from crossover)
    for genome in pool.all_alive(role="vc"):
        if genome.persona_id.startswith("evolved_"):
            offspring = _build_vc_from_genome(genome)
            if offspring:
                evolved.append(offspring)

    # Ensure at least 3 VCs
    if len(evolved) < 3:
        for vc in DEFAULT_VC_PANEL:
            if vc.name not in {v.name for v in evolved}:
                evolved.append(vc)
            if len(evolved) >= 5:
                break

    return tuple(evolved[:7])  # Cap at 7 VCs max


def get_evolved_community_personas(
    count: int = 20,
) -> tuple[PersonaProfile, ...]:
    """Get community personas with evolved genes applied.

    Evolved frustrations, patience modifiers, and evaluation styles
    replace the defaults for personas that have gene data.
    """
    pool = GenePool()
    defaults = generate_default_personas()
    evolved: list[PersonaProfile] = []

    for persona in defaults:
        genome = pool.get(persona.name)

        if genome and genome.alive:
            evolved.append(_apply_community_genes(persona, genome))
        elif genome and not genome.alive:
            continue
        else:
            evolved.append(persona)

    # Add evolved offspring
    for genome in pool.all_alive(role="community"):
        if genome.persona_id.startswith("evolved_") and len(evolved) < count:
            child = _build_community_from_genome(genome)
            if child:
                evolved.append(child)

    return tuple(evolved[:count])


def _apply_vc_genes(vc: VCPersona, genome: PersonaGenome) -> VCPersona:
    """Replace a VC's traits with evolved gene values."""
    # Extract evolved kill questions
    kill_qs = []
    for key, gene in sorted(genome.genes.items()):
        if gene.name.startswith("kill_question"):
            kill_qs.append(gene.value)
    if not kill_qs:
        kill_qs = list(vc.kill_questions)

    # Extract evolved pet peeves
    peeves = []
    for key, gene in sorted(genome.genes.items()):
        if gene.name.startswith("pet_peeve"):
            peeves.append(gene.value)
    if not peeves:
        peeves = list(vc.pet_peeves)

    # Extract evolved tone
    tone = genome.genes.get("tone")
    evolved_tone = tone.value if tone else vc.tone

    return VCPersona(
        name=vc.name,
        title=vc.title,
        fund=vc.fund,
        archetype=vc.archetype,
        background=vc.background,
        check_size=vc.check_size,
        portfolio=vc.portfolio,
        pet_peeves=tuple(peeves),
        kill_questions=tuple(kill_qs),
        tone=evolved_tone,
    )


def _build_vc_from_genome(genome: PersonaGenome) -> VCPersona | None:
    """Build a new VC persona entirely from an evolved genome."""
    kill_qs = tuple(
        g.value for k, g in sorted(genome.genes.items())
        if g.name.startswith("kill_question")
    )
    peeves = tuple(
        g.value for k, g in sorted(genome.genes.items())
        if g.name.startswith("pet_peeve")
    )
    tone_gene = genome.genes.get("tone")
    tone = tone_gene.value if tone_gene else "brutally honest"

    if not kill_qs:
        return None

    return VCPersona(
        name=f"Evolved VC (Gen {genome.generation})",
        title="AI-Evolved Partner",
        fund="Natural Selection Capital",
        archetype=VCArchetype.SHARK,
        background=f"This VC was bred from the best-performing critics over {genome.generation} generations. "
                   f"Its kill questions have been battle-tested and refined through user feedback.",
        check_size="$1M-$10M",
        portfolio=("Whatever survives the roast",),
        pet_peeves=peeves or ("Weak pitches", "No data"),
        kill_questions=kill_qs,
        tone=tone,
    )


def _apply_community_genes(
    persona: PersonaProfile, genome: PersonaGenome,
) -> PersonaProfile:
    """Replace a community persona's traits with evolved gene values."""
    # Extract evolved frustrations
    frustrations = []
    for key, gene in sorted(genome.genes.items()):
        if gene.name.startswith("frustration"):
            frustrations.append(gene.value)

    # Extract patience modifier
    patience_gene = genome.genes.get("patience_modifier")
    patience_mod = float(patience_gene.value) if patience_gene else 1.0

    return PersonaProfile(
        name=persona.name,
        age=persona.age,
        background=persona.background,
        tech_savvy=persona.tech_savvy,
        patience_seconds=int(persona.patience_seconds * patience_mod),
        language=persona.language,
        has_alternative=persona.has_alternative,
        alternative_name=persona.alternative_name,
        irrationality_mod=persona.irrationality_mod,
        archetype=persona.archetype,
        evaluation_style=persona.evaluation_style,
        goals=persona.goals,
        frustrations=tuple(frustrations) if frustrations else persona.frustrations,
        context_of_use=persona.context_of_use,
        emotional_state=persona.emotional_state,
        accessibility_needs=persona.accessibility_needs,
    )


def _build_community_from_genome(genome: PersonaGenome) -> PersonaProfile | None:
    """Build a community persona from an evolved genome."""
    archetype_gene = genome.genes.get("archetype")
    eval_gene = genome.genes.get("eval_style")

    archetype_map = {a.value: a for a in Archetype}
    eval_map = {e.value: e for e in EvaluationStyle}

    archetype = archetype_map.get(
        archetype_gene.value if archetype_gene else "pragmatist",
        Archetype.PRAGMATIST,
    )
    eval_style = eval_map.get(
        eval_gene.value if eval_gene else "task_driven",
        EvaluationStyle.TASK_DRIVEN,
    )

    frustrations = tuple(
        g.value for k, g in sorted(genome.genes.items())
        if g.name.startswith("frustration")
    )

    return PersonaProfile(
        name=f"Evolved Persona (Gen {genome.generation})",
        age=30,
        background=f"AI-evolved community tester, generation {genome.generation}. "
                   f"Bred from top-performing critics through user feedback selection.",
        tech_savvy=0.7,
        patience_seconds=30,
        language="en",
        has_alternative=False,
        archetype=archetype,
        evaluation_style=eval_style,
        goals=("Find the most impactful issues",),
        frustrations=frustrations,
        context_of_use="Evolved through natural selection of critique quality",
        emotional_state="calibrated by feedback",
    )
