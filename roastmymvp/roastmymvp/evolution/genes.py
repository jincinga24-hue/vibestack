"""Gene encoding for VC and community personas.

Each persona's traits are encoded as mutable genes. After each run,
user feedback determines which genes survive and which get mutated.

Inspired by EvoMap's Genome Evolution Protocol (GEP):
  Scan → Signal → Intent → Mutate → Validate → Solidify
"""

import json
import os
import random
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

GENES_DIR = Path(__file__).parent.parent.parent / "memory" / "genes"


@dataclass
class Gene:
    """A single mutable trait of a persona."""
    name: str
    value: str
    fitness: float = 0.5       # 0.0 = useless, 1.0 = killer insight generator
    mutations: int = 0         # How many times this gene has been mutated
    origin: str = "default"    # "default", "mutated", "crossover", "user_injected"


@dataclass
class PersonaGenome:
    """Full genome of a persona — all traits as genes."""
    persona_id: str
    role: str                  # "vc" or "community"
    genes: dict[str, Gene] = field(default_factory=dict)
    generation: int = 0
    total_runs: int = 0
    avg_usefulness: float = 0.5
    alive: bool = True         # Dead genes get replaced

    def to_dict(self) -> dict:
        return {
            "persona_id": self.persona_id,
            "role": self.role,
            "genes": {k: {"name": v.name, "value": v.value, "fitness": v.fitness,
                          "mutations": v.mutations, "origin": v.origin}
                      for k, v in self.genes.items()},
            "generation": self.generation,
            "total_runs": self.total_runs,
            "avg_usefulness": self.avg_usefulness,
            "alive": self.alive,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PersonaGenome":
        genes = {}
        for k, v in data.get("genes", {}).items():
            genes[k] = Gene(**v)
        return cls(
            persona_id=data["persona_id"],
            role=data["role"],
            genes=genes,
            generation=data.get("generation", 0),
            total_runs=data.get("total_runs", 0),
            avg_usefulness=data.get("avg_usefulness", 0.5),
            alive=data.get("alive", True),
        )


def encode_vc_genes(vc_name: str, kill_questions: tuple[str, ...],
                     pet_peeves: tuple[str, ...], tone: str) -> PersonaGenome:
    """Encode a VC persona's traits as a genome."""
    genes = {}

    for i, q in enumerate(kill_questions):
        genes[f"kill_q_{i}"] = Gene(name=f"kill_question_{i}", value=q)

    for i, p in enumerate(pet_peeves):
        genes[f"peeve_{i}"] = Gene(name=f"pet_peeve_{i}", value=p)

    genes["tone"] = Gene(name="tone", value=tone)
    genes["aggression"] = Gene(name="aggression", value="0.7")
    genes["specificity"] = Gene(name="specificity", value="0.8")
    genes["founder_focus"] = Gene(name="founder_focus", value="0.5")

    return PersonaGenome(persona_id=vc_name, role="vc", genes=genes)


def encode_community_genes(persona_name: str, archetype: str,
                            evaluation_style: str, frustrations: tuple[str, ...]) -> PersonaGenome:
    """Encode a community persona's traits as a genome."""
    genes = {}

    genes["archetype"] = Gene(name="archetype", value=archetype)
    genes["eval_style"] = Gene(name="evaluation_style", value=evaluation_style)
    genes["patience_modifier"] = Gene(name="patience_modifier", value="1.0")
    genes["detail_focus"] = Gene(name="detail_focus", value="0.6")

    for i, f in enumerate(frustrations[:5]):
        genes[f"frustration_{i}"] = Gene(name=f"frustration_{i}", value=f)

    return PersonaGenome(persona_id=persona_name, role="community", genes=genes)


class GenePool:
    """Persistent gene pool — survives between runs, evolves over time."""

    def __init__(self, pool_dir: Path | None = None):
        self._dir = pool_dir or GENES_DIR
        self._dir.mkdir(parents=True, exist_ok=True)
        self._pool_file = self._dir / "gene_pool.json"
        self._history_file = self._dir / "evolution_history.jsonl"
        self._pool: dict[str, PersonaGenome] = {}
        self._load()

    def _load(self):
        if self._pool_file.exists():
            data = json.loads(self._pool_file.read_text())
            for pid, genome_data in data.items():
                self._pool[pid] = PersonaGenome.from_dict(genome_data)

    def save(self):
        self._pool_file.write_text(json.dumps(
            {pid: g.to_dict() for pid, g in self._pool.items()},
            indent=2,
        ))

    def get(self, persona_id: str) -> PersonaGenome | None:
        return self._pool.get(persona_id)

    def put(self, genome: PersonaGenome):
        self._pool[genome.persona_id] = genome

    def all_alive(self, role: str = "") -> list[PersonaGenome]:
        return [g for g in self._pool.values()
                if g.alive and (not role or g.role == role)]

    def record_feedback(self, persona_id: str, usefulness: float):
        """Record user feedback on a persona's critique (0.0 = useless, 1.0 = killer)."""
        genome = self._pool.get(persona_id)
        if not genome:
            return

        genome.total_runs += 1
        # Exponential moving average
        alpha = 0.3
        genome.avg_usefulness = alpha * usefulness + (1 - alpha) * genome.avg_usefulness

        # Update gene fitness based on persona usefulness
        for gene in genome.genes.values():
            gene.fitness = alpha * usefulness + (1 - alpha) * gene.fitness

        # Log to history
        self._log_event("feedback", persona_id, {
            "usefulness": usefulness,
            "new_avg": genome.avg_usefulness,
        })

        self.save()

    def evolve(self, rng: random.Random | None = None) -> list[str]:
        """Run one evolution cycle on the gene pool.

        Returns list of mutation descriptions.
        """
        rng = rng or random.Random()
        mutations: list[str] = []

        alive = [g for g in self._pool.values() if g.alive]
        if len(alive) < 2:
            return mutations

        # Kill low-fitness personas (bottom 20% after enough runs)
        for genome in alive:
            if genome.total_runs >= 3 and genome.avg_usefulness < 0.3:
                genome.alive = False
                mutations.append(f"KILLED: {genome.persona_id} (fitness {genome.avg_usefulness:.2f})")
                self._log_event("kill", genome.persona_id, {
                    "reason": "low_fitness",
                    "fitness": genome.avg_usefulness,
                })

        # Mutate mid-tier personas (40-70% fitness)
        for genome in alive:
            if 0.3 <= genome.avg_usefulness <= 0.7 and genome.alive:
                mutated_gene = self._mutate_random_gene(genome, rng)
                if mutated_gene:
                    mutations.append(
                        f"MUTATED: {genome.persona_id}.{mutated_gene} (gen {genome.generation})"
                    )

        # Crossover: breed top 2 to create a new persona
        top = sorted(alive, key=lambda g: g.avg_usefulness, reverse=True)
        if len(top) >= 2 and top[0].avg_usefulness > 0.6:
            child = self._crossover(top[0], top[1], rng)
            self._pool[child.persona_id] = child
            mutations.append(
                f"BORN: {child.persona_id} from {top[0].persona_id} x {top[1].persona_id}"
            )

        for genome in self._pool.values():
            if genome.alive:
                genome.generation += 1

        self.save()
        return mutations

    def _mutate_random_gene(self, genome: PersonaGenome, rng: random.Random) -> str | None:
        """Mutate a random gene in the genome."""
        mutable = [k for k, g in genome.genes.items()
                   if g.name.startswith(("kill_q", "peeve", "frustration"))]
        if not mutable:
            return None

        key = rng.choice(mutable)
        gene = genome.genes[key]

        # Mutation strategies
        strategies = [
            lambda v: v + " — and be more specific about WHY this matters",
            lambda v: v.replace("?", "? Give me numbers."),
            lambda v: f"Follow up on: {v}",
            lambda v: v + " (check their GitHub to verify)",
        ]
        gene.value = rng.choice(strategies)(gene.value)
        gene.mutations += 1
        gene.origin = "mutated"
        genome.generation += 1

        self._log_event("mutate", genome.persona_id, {
            "gene": key, "new_value": gene.value[:100],
        })

        return key

    def _crossover(self, parent_a: PersonaGenome, parent_b: PersonaGenome,
                   rng: random.Random) -> PersonaGenome:
        """Breed two genomes to create a child."""
        child_id = f"evolved_{int(time.time())}"
        child_genes = {}

        # Take best genes from each parent
        all_keys = set(parent_a.genes.keys()) | set(parent_b.genes.keys())
        for key in all_keys:
            gene_a = parent_a.genes.get(key)
            gene_b = parent_b.genes.get(key)

            if gene_a and gene_b:
                # Pick the higher fitness gene
                winner = gene_a if gene_a.fitness >= gene_b.fitness else gene_b
                child_genes[key] = Gene(
                    name=winner.name, value=winner.value,
                    fitness=(gene_a.fitness + gene_b.fitness) / 2,
                    origin="crossover",
                )
            elif gene_a:
                child_genes[key] = Gene(name=gene_a.name, value=gene_a.value,
                                        fitness=gene_a.fitness, origin="crossover")
            elif gene_b:
                child_genes[key] = Gene(name=gene_b.name, value=gene_b.value,
                                        fitness=gene_b.fitness, origin="crossover")

        self._log_event("crossover", child_id, {
            "parent_a": parent_a.persona_id,
            "parent_b": parent_b.persona_id,
        })

        return PersonaGenome(
            persona_id=child_id, role=parent_a.role,
            genes=child_genes, generation=max(parent_a.generation, parent_b.generation) + 1,
        )

    def _log_event(self, event_type: str, persona_id: str, data: dict):
        entry = {
            "timestamp": time.time(),
            "event": event_type,
            "persona_id": persona_id,
            **data,
        }
        with open(self._history_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def stats(self) -> dict:
        alive = [g for g in self._pool.values() if g.alive]
        dead = [g for g in self._pool.values() if not g.alive]
        return {
            "total": len(self._pool),
            "alive": len(alive),
            "dead": len(dead),
            "avg_fitness": sum(g.avg_usefulness for g in alive) / max(len(alive), 1),
            "max_generation": max((g.generation for g in alive), default=0),
            "total_mutations": sum(
                sum(g.mutations for g in genome.genes.values())
                for genome in alive
            ),
        }
