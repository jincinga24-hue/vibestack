"""Persona profile generation — archetypes, rich backgrounds, irrationality injection."""

import hashlib
import random

from roastmymvp.personas.irrationality import inject_irrationality
from roastmymvp.personas.models import (
    Archetype,
    EvaluationStyle,
    PersonaProfile,
)

# Each default persona is a fully fleshed-out character with motivations
_DEFAULT_PERSONAS = [
    # === POWER USERS ===
    {
        "name": "Raj Patel", "age": 35,
        "background": "Senior software engineer at a Series B startup. 10 years building distributed systems. Reviews 3-4 new tools per month and drops most within 15 minutes. Has strong opinions about API design and CLI ergonomics.",
        "tech_savvy": 1.0, "patience": 15, "lang": "en",
        "has_alt": True, "alt": "Linear",
        "archetype": Archetype.POWER_USER, "eval": EvaluationStyle.TASK_DRIVEN,
        "goals": ("Find a tool that integrates with existing workflow", "Evaluate API quality"),
        "frustrations": ("Tools that don't respect power users", "Mandatory onboarding tutorials", "No keyboard shortcuts"),
        "context": "Evaluating during a 15-min break between sprints. Will test CLI first.",
        "emotion": "impatient but curious",
    },
    {
        "name": "Chen Wei", "age": 38,
        "background": "Backend engineer at Alibaba Cloud, 12 years experience. Prefers CLI tools and vim. Reads source code before trusting any tool. Will check the GitHub repo before even trying the product.",
        "tech_savvy": 1.0, "patience": 10, "lang": "zh",
        "has_alt": True, "alt": "custom scripts",
        "archetype": Archetype.POWER_USER, "eval": EvaluationStyle.COMPARISON,
        "goals": ("Determine if this replaces my custom scripts", "Check if it's open source"),
        "frustrations": ("Closed source tools", "No API docs", "Electron apps"),
        "context": "Weekend side project time. SSH'd into a remote server.",
        "emotion": "skeptical but fair",
    },
    {
        "name": "Hassan Ali", "age": 30,
        "background": "DevOps engineer at a fintech company. Automates everything. If it can't be scripted, it doesn't exist. Judges tools by how well they fit into CI/CD pipelines.",
        "tech_savvy": 0.9, "patience": 15, "lang": "ar",
        "has_alt": True, "alt": "Terraform + custom scripts",
        "archetype": Archetype.POWER_USER, "eval": EvaluationStyle.TASK_DRIVEN,
        "goals": ("Can I automate this?", "Does it have a REST API?"),
        "frustrations": ("GUIs without CLI equivalents", "No webhook support", "Manual steps"),
        "context": "Researching tools for team adoption during an incident-free on-call shift.",
        "emotion": "methodical",
    },

    # === SKEPTICS ===
    {
        "name": "James Thompson", "age": 55,
        "background": "CTO of a 200-person company. Has seen hundreds of tools come and go. Burned by three failed migrations in the last two years. Needs to justify any new tool to the board.",
        "tech_savvy": 0.8, "patience": 10, "lang": "en",
        "has_alt": True, "alt": "established enterprise tools",
        "archetype": Archetype.SKEPTIC, "eval": EvaluationStyle.COMPARISON,
        "goals": ("Assess enterprise readiness", "Evaluate security and compliance"),
        "frustrations": ("No SOC 2 badge", "No SLA", "Startup-looking landing pages"),
        "context": "Was forwarded this by his VP of Engineering. Giving it 10 minutes max.",
        "emotion": "guarded, slightly annoyed",
    },
    {
        "name": "Nina Ivanova", "age": 34,
        "background": "QA engineer who finds bugs professionally. Tests products adversarially — wrong inputs, edge cases, rapid actions. Has broken more products than she's approved.",
        "tech_savvy": 0.8, "patience": 30, "lang": "ru",
        "has_alt": True, "alt": "Selenium + custom QA tools",
        "archetype": Archetype.SKEPTIC, "eval": EvaluationStyle.EXPLORATORY,
        "goals": ("Find everything that's broken", "Test error handling"),
        "frustrations": ("Silent failures", "No error messages", "Unhandled edge cases"),
        "context": "Voluntarily testing this because she's curious. Will try to break it.",
        "emotion": "amused, hunting for bugs",
    },
    {
        "name": "David Lee", "age": 45,
        "background": "Engineering manager at a Fortune 500. Evaluates tools for his 40-person team. Needs business justification, migration plan, and training materials before approving anything.",
        "tech_savvy": 0.7, "patience": 20, "lang": "en",
        "has_alt": True, "alt": "Jira + Confluence",
        "archetype": Archetype.SKEPTIC, "eval": EvaluationStyle.COMPARISON,
        "goals": ("Evaluate ROI vs current tools", "Check team onboarding friction"),
        "frustrations": ("No team/org features", "No SSO", "No admin dashboard"),
        "context": "Quarterly tool review. Has a spreadsheet comparing 5 options.",
        "emotion": "analytical, detached",
    },

    # === CONFUSED NEWBIES ===
    {
        "name": "Liu Wei", "age": 20,
        "background": "First-year CS student at University of Melbourne. Just learned Python last semester. Doesn't know what an API is. Finds most developer tools intimidating.",
        "tech_savvy": 0.3, "patience": 90, "lang": "zh",
        "has_alt": False, "alt": None,
        "archetype": Archetype.CONFUSED, "eval": EvaluationStyle.FIRST_IMPRESSION,
        "goals": ("Understand what this product does", "Find a getting started guide"),
        "frustrations": ("Jargon-heavy landing pages", "No examples", "Assumed knowledge"),
        "context": "Saw this shared in a WeChat group. Trying it on his laptop between classes.",
        "emotion": "curious but intimidated",
    },
    {
        "name": "Carlos Ruiz", "age": 50,
        "background": "Small bakery owner in Buenos Aires. His nephew told him this could help his business. Doesn't understand tech terminology. Types slowly with two fingers.",
        "tech_savvy": 0.1, "patience": 120, "lang": "es",
        "has_alt": False, "alt": None,
        "archetype": Archetype.CONFUSED, "eval": EvaluationStyle.FIRST_IMPRESSION,
        "goals": ("Figure out if this helps sell more bread", "Find something simple to use"),
        "frustrations": ("English-only interfaces", "Too many options", "No phone support"),
        "context": "Sunday afternoon. His nephew is helping him over the phone.",
        "emotion": "overwhelmed but hopeful",
    },
    {
        "name": "Sophie Martin", "age": 24,
        "background": "Bootcamp graduate, 3 months into job search. Building portfolio projects to stand out. Knows React basics but googles everything beyond that.",
        "tech_savvy": 0.4, "patience": 50, "lang": "fr",
        "has_alt": False, "alt": None,
        "archetype": Archetype.CONFUSED, "eval": EvaluationStyle.EXPLORATORY,
        "goals": ("Use this in a portfolio project", "Understand the docs well enough to demo it"),
        "frustrations": ("Docs that assume prior knowledge", "No copy-paste examples", "Complex setup"),
        "context": "Evening coding session at home. Has 3 tabs of Stack Overflow open.",
        "emotion": "determined but insecure",
    },

    # === ADVOCATES (early adopters) ===
    {
        "name": "Alex Chen", "age": 22,
        "background": "CS student who builds side projects every weekend. Active on Twitter/X and Product Hunt. Loves trying new tools and writing about them. Has 2K followers who trust his reviews.",
        "tech_savvy": 0.9, "patience": 30, "lang": "zh",
        "has_alt": False, "alt": None,
        "archetype": Archetype.ADVOCATE, "eval": EvaluationStyle.EXPLORATORY,
        "goals": ("Find something cool to tweet about", "Build something with this today"),
        "frustrations": ("Boring products", "No wow moment in first 30 seconds", "Ugly design"),
        "context": "Saturday morning hackathon energy. Already has a project idea.",
        "emotion": "excited, optimistic",
    },
    {
        "name": "Yuki Tanaka", "age": 26,
        "background": "iOS developer at a Tokyo startup. Loves beautiful UI and smooth animations. Active on GitHub, contributes to open source. Will forgive bugs if the vision is compelling.",
        "tech_savvy": 0.9, "patience": 25, "lang": "ja",
        "has_alt": False, "alt": None,
        "archetype": Archetype.ADVOCATE, "eval": EvaluationStyle.FIRST_IMPRESSION,
        "goals": ("Assess design quality", "Check if there's an iOS SDK or mobile support"),
        "frustrations": ("Ugly UI", "No mobile consideration", "Generic Bootstrap look"),
        "context": "Commute home on the train. Testing on iPhone.",
        "emotion": "aesthetically driven",
    },
    {
        "name": "Tom Baker", "age": 19,
        "background": "Hackathon junkie. Shipped 12 projects in the last year, none with more than 10 users. Moves extremely fast, doesn't read docs, learns by breaking things.",
        "tech_savvy": 0.6, "patience": 15, "lang": "en",
        "has_alt": False, "alt": None,
        "archetype": Archetype.ADVOCATE, "eval": EvaluationStyle.TASK_DRIVEN,
        "goals": ("Get something working in 5 minutes", "Integrate into current hackathon project"),
        "frustrations": ("Long setup processes", "Requiring credit card", "Email verification"),
        "context": "12 hours into a 24-hour hackathon. Running on coffee and adrenaline.",
        "emotion": "frantic, impatient but forgiving",
    },

    # === CHURNERS ===
    {
        "name": "Priya Sharma", "age": 33,
        "background": "UX researcher at a fintech. Has tried and abandoned UserTesting, Maze, Hotjar, and Loop11 in the past year. None met her specific workflow needs. She knows exactly what she wants and is tired of compromise.",
        "tech_savvy": 0.6, "patience": 60, "lang": "en",
        "has_alt": True, "alt": "nothing — left them all",
        "archetype": Archetype.CHURNER, "eval": EvaluationStyle.COMPARISON,
        "goals": ("Check if this finally solves the unmoderated testing workflow", "Evaluate data export"),
        "frustrations": ("Tools that almost work but not quite", "No custom branding", "Locked-in data"),
        "context": "Deliberately setting aside time to evaluate. Has a checklist of 15 requirements.",
        "emotion": "cautiously hopeful, ready to be disappointed",
    },
    {
        "name": "Emma Wilson", "age": 42,
        "background": "Non-technical founder of a DTC skincare brand. Has tried Shopify, Squarespace, Wix, and abandoned all of them at some point. Keeps coming back to manually DMing customers on Instagram.",
        "tech_savvy": 0.2, "patience": 60, "lang": "en",
        "has_alt": True, "alt": "Instagram DMs (manually)",
        "archetype": Archetype.CHURNER, "eval": EvaluationStyle.FIRST_IMPRESSION,
        "goals": ("Find something simpler than what I've tried", "Not feel stupid"),
        "frustrations": ("Technical setup steps", "Dashboards with too many numbers", "Jargon"),
        "context": "Late evening after kids are in bed. Giving this one more try.",
        "emotion": "exhausted, low expectations",
    },

    # === PRAGMATISTS ===
    {
        "name": "Maria Garcia", "age": 31,
        "background": "Full-stack freelancer with 6 active clients. Charges by the hour. Every minute spent evaluating tools is unbilled time. Will adopt immediately if it saves time, ignore if it doesn't.",
        "tech_savvy": 0.9, "patience": 20, "lang": "es",
        "has_alt": True, "alt": "Vercel + own scripts",
        "archetype": Archetype.PRAGMATIST, "eval": EvaluationStyle.TASK_DRIVEN,
        "goals": ("Will this save me more than 30 min/week?", "Can I bill clients for using this?"),
        "frustrations": ("Free trials that require credit card", "No pricing transparency", "Feature bloat"),
        "context": "Between client calls. Has exactly 20 minutes.",
        "emotion": "businesslike, time-conscious",
    },
    {
        "name": "Aisha Mohammed", "age": 29,
        "background": "Data scientist transitioning to product management. Evaluates tools through a lens of data quality and actionable insights. Wants numbers, not vibes.",
        "tech_savvy": 0.8, "patience": 40, "lang": "en",
        "has_alt": False, "alt": None,
        "archetype": Archetype.PRAGMATIST, "eval": EvaluationStyle.TASK_DRIVEN,
        "goals": ("Can this generate data I can present to stakeholders?", "Is the output actionable?"),
        "frustrations": ("Vague metrics", "No export to CSV/JSON", "Pretty dashboards with no depth"),
        "context": "Research phase for her new PM role. Bookmarked this from a podcast mention.",
        "emotion": "analytical, open-minded",
    },
    {
        "name": "Sarah Kim", "age": 28,
        "background": "Junior product designer at a YC startup. Good at Figma, learning to code. Evaluates tools by how they'd fit into her team's design-to-dev handoff workflow.",
        "tech_savvy": 0.6, "patience": 45, "lang": "en",
        "has_alt": True, "alt": "Figma + Notion",
        "archetype": Archetype.PRAGMATIST, "eval": EvaluationStyle.COMPARISON,
        "goals": ("Would this replace one of our current tools?", "Is it worth proposing to the team?"),
        "frustrations": ("No Figma integration", "No collaboration features", "Ugly interface"),
        "context": "Slack recommendation from a designer friend. Checking it out during lunch.",
        "emotion": "neutral, casually evaluating",
    },

    # === ACCESSIBILITY ===
    {
        "name": "Olivia Brown", "age": 27,
        "background": "Frontend developer with low vision. Uses screen magnifier and high contrast mode daily. Advocates for accessibility in every code review. Judges products harshly on a11y.",
        "tech_savvy": 0.8, "patience": 45, "lang": "en",
        "has_alt": False, "alt": None,
        "archetype": Archetype.ACCESSIBILITY, "eval": EvaluationStyle.EXPLORATORY,
        "goals": ("Check WCAG compliance", "Test with screen reader", "Evaluate contrast ratios"),
        "frustrations": ("Low contrast text", "No alt text", "Mouse-only interactions", "Tiny click targets"),
        "context": "Evaluating for a blog post on accessible developer tools.",
        "emotion": "professionally critical",
        "a11y": "Low vision — uses 200% zoom and high contrast mode",
    },
    {
        "name": "Anna Kowalski", "age": 23,
        "background": "CS student with ADHD. Gets overwhelmed by cluttered interfaces and long onboarding flows. Needs clear visual hierarchy and immediate feedback.",
        "tech_savvy": 0.8, "patience": 35, "lang": "pl",
        "has_alt": False, "alt": None,
        "archetype": Archetype.ACCESSIBILITY, "eval": EvaluationStyle.FIRST_IMPRESSION,
        "goals": ("Can I focus on this?", "Is the interface calm or chaotic?"),
        "frustrations": ("Busy dashboards", "Notification spam", "No keyboard shortcuts", "Animation overload"),
        "context": "Hyperfocusing on a new project. Found this tool while going down a rabbit hole.",
        "emotion": "hyperfocused but easily derailed",
        "a11y": "ADHD — needs minimal distractions and clear visual hierarchy",
    },

    # === WILDCARD ===
    {
        "name": "Mike Zhang", "age": 21,
        "background": "Indie game developer who ships a new project every month. Judges tools entirely by how fast he can go from zero to working prototype. Doesn't care about best practices.",
        "tech_savvy": 0.7, "patience": 20, "lang": "en",
        "has_alt": False, "alt": None,
        "archetype": Archetype.ADVOCATE, "eval": EvaluationStyle.TASK_DRIVEN,
        "goals": ("Get a working prototype in 10 minutes", "Find the fastest path to something deployable"),
        "frustrations": ("Long setup processes", "Best-practice-heavy docs", "No quickstart"),
        "context": "Sunday afternoon. Just had a new project idea and wants to build it NOW.",
        "emotion": "impatient creative energy",
    },
]


def generate_default_personas(seed: int = 42) -> tuple[PersonaProfile, ...]:
    """Generate the standard set of 20 diverse personas with irrationality injection."""
    rng = random.Random(seed)
    personas: list[PersonaProfile] = []

    for p in _DEFAULT_PERSONAS:
        irrationality = inject_irrationality(rng)

        personas.append(
            PersonaProfile(
                name=p["name"],
                age=p["age"],
                background=p["background"],
                tech_savvy=p["tech_savvy"],
                patience_seconds=p["patience"],
                language=p["lang"],
                has_alternative=p["has_alt"],
                alternative_name=p.get("alt"),
                irrationality_mod=irrationality,
                archetype=p["archetype"],
                evaluation_style=p["eval"],
                goals=tuple(p.get("goals", ())),
                frustrations=tuple(p.get("frustrations", ())),
                context_of_use=p.get("context", ""),
                emotional_state=p.get("emotion", "neutral"),
                accessibility_needs=p.get("a11y"),
            )
        )

    return tuple(personas)


def generate_custom_persona(description: str) -> PersonaProfile:
    """Create a persona from a free-text description.

    Uses LLM-style parsing to extract traits from natural language.
    """
    seed = int(hashlib.md5(description.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    age = _extract_age(description)
    has_alt, alt_name = _extract_competitor(description)
    tech_savvy = _extract_tech_savvy(description)
    archetype = _infer_archetype(description)
    eval_style = _infer_evaluation_style(archetype)

    first_names = ["Alex", "Jordan", "Sam", "Casey", "Robin", "Taylor", "Morgan", "Quinn"]
    last_names = ["Chen", "Park", "Smith", "Kumar", "Garcia", "Kim", "Brown", "Lee"]
    name = f"{rng.choice(first_names)} {rng.choice(last_names)}"

    return PersonaProfile(
        name=name,
        age=age,
        background=description,
        tech_savvy=tech_savvy,
        patience_seconds=rng.randint(15, 90),
        language="en",
        has_alternative=has_alt,
        alternative_name=alt_name,
        irrationality_mod=inject_irrationality(rng),
        archetype=archetype,
        evaluation_style=eval_style,
        goals=_infer_goals(description, archetype),
        frustrations=(),
        context_of_use="Custom persona from user description",
        emotional_state="neutral",
    )


def generate_persona_variants(
    base: PersonaProfile, count: int = 5
) -> tuple[PersonaProfile, ...]:
    """Create meaningfully different variations of a base persona.

    Instead of just adding noise, each variant shifts the archetype
    and evaluation style to create genuinely different perspectives.
    """
    variants: list[PersonaProfile] = []
    rng = random.Random(hash(base.name))

    first_names = ["Mia", "Ethan", "Zara", "Leo", "Nora", "Kai", "Luna", "Finn",
                   "Iris", "Oscar", "Maya", "Theo", "Ava", "Liam", "Ella"]
    last_names = ["Wang", "Singh", "Jones", "Nakamura", "Silva", "Petrov", "Muller",
                  "Dubois", "Hansen", "Ali", "Park", "Costa", "Nguyen", "Schmidt", "Liu"]

    # Cycle through archetypes to ensure diversity
    archetype_cycle = list(Archetype)
    eval_cycle = list(EvaluationStyle)
    emotional_states = [
        "rushed and distracted", "relaxed and thorough", "frustrated by previous tools",
        "excited to find something new", "skeptical but willing to be convinced",
        "bored, scrolling through options", "focused and analytical", "anxious about making the wrong choice",
    ]

    used_names: set[str] = set()
    for i in range(count):
        age_offset = rng.randint(-8, 15)
        tech_offset = rng.uniform(-0.3, 0.3)
        archetype = archetype_cycle[i % len(archetype_cycle)]
        eval_style = eval_cycle[i % len(eval_cycle)]
        emotion = rng.choice(emotional_states)

        # Guarantee unique names
        name = f"{rng.choice(first_names)} {rng.choice(last_names)}"
        while name in used_names:
            name = f"{rng.choice(first_names)} {rng.choice(last_names)}"
        used_names.add(name)

        variants.append(
            PersonaProfile(
                name=name,
                age=max(16, base.age + age_offset),
                background=base.background,
                tech_savvy=max(0.0, min(1.0, base.tech_savvy + tech_offset)),
                patience_seconds=max(10, base.patience_seconds + rng.randint(-20, 30)),
                language=base.language,
                has_alternative=base.has_alternative if rng.random() > 0.4 else not base.has_alternative,
                alternative_name=base.alternative_name,
                irrationality_mod=inject_irrationality(rng),
                archetype=archetype,
                evaluation_style=eval_style,
                goals=base.goals,
                frustrations=base.frustrations,
                context_of_use=base.context_of_use,
                emotional_state=emotion,
            )
        )

    return tuple(variants)


def _extract_age(description: str) -> int:
    for word in description.split():
        if word.endswith("-year-old") or word.endswith("-year"):
            try:
                return int(word.split("-")[0])
            except ValueError:
                pass
        elif word.isdigit() and 10 <= int(word) <= 100:
            return int(word)
    return 25


def _extract_competitor(description: str) -> tuple[bool, str | None]:
    keywords = ["using", "competitor", "alternative", "currently use", "already use"]
    has_alt = any(kw in description.lower() for kw in keywords)
    alt_name = None
    if has_alt:
        words = description.split()
        for i, w in enumerate(words):
            if w.lower() in ("competitor", "using") and i + 1 < len(words):
                alt_name = words[i + 1].strip(".,;")
                break
    return has_alt, alt_name


def _extract_tech_savvy(description: str) -> float:
    tech_keywords = {
        "developer": 0.9, "engineer": 0.9, "programmer": 0.9, "coder": 0.7,
        "designer": 0.6, "researcher": 0.6, "manager": 0.5, "student": 0.5,
        "founder": 0.4, "owner": 0.3, "marketer": 0.3,
    }
    for keyword, level in tech_keywords.items():
        if keyword in description.lower():
            return level
    return 0.5


def _infer_archetype(description: str) -> Archetype:
    desc = description.lower()
    if any(w in desc for w in ("skeptic", "critical", "cautious", "burned", "disappointed")):
        return Archetype.SKEPTIC
    if any(w in desc for w in ("tried", "abandoned", "left", "quit", "stopped using")):
        return Archetype.CHURNER
    if any(w in desc for w in ("excited", "love", "enthusiast", "early adopter")):
        return Archetype.ADVOCATE
    if any(w in desc for w in ("beginner", "new to", "first time", "learning")):
        return Archetype.CONFUSED
    if any(w in desc for w in ("senior", "expert", "advanced", "power")):
        return Archetype.POWER_USER
    if any(w in desc for w in ("accessibility", "screen reader", "disability", "adhd")):
        return Archetype.ACCESSIBILITY
    return Archetype.PRAGMATIST


def _infer_evaluation_style(archetype: Archetype) -> EvaluationStyle:
    mapping = {
        Archetype.POWER_USER: EvaluationStyle.TASK_DRIVEN,
        Archetype.SKEPTIC: EvaluationStyle.COMPARISON,
        Archetype.ADVOCATE: EvaluationStyle.EXPLORATORY,
        Archetype.CONFUSED: EvaluationStyle.FIRST_IMPRESSION,
        Archetype.CHURNER: EvaluationStyle.COMPARISON,
        Archetype.PRAGMATIST: EvaluationStyle.TASK_DRIVEN,
        Archetype.ACCESSIBILITY: EvaluationStyle.EXPLORATORY,
    }
    return mapping.get(archetype, EvaluationStyle.TASK_DRIVEN)


def _infer_goals(description: str, archetype: Archetype) -> tuple[str, ...]:
    base_goals = {
        Archetype.POWER_USER: ("Push the product to its limits", "Evaluate API and integrations"),
        Archetype.SKEPTIC: ("Find reasons this won't work", "Compare to current solution"),
        Archetype.ADVOCATE: ("Find something exciting to share", "Build something with this"),
        Archetype.CONFUSED: ("Understand what this product does", "Find a getting started guide"),
        Archetype.CHURNER: ("Check if this finally solves my problem", "Evaluate data portability"),
        Archetype.PRAGMATIST: ("Determine if this saves time", "Evaluate cost vs benefit"),
        Archetype.ACCESSIBILITY: ("Check accessibility compliance", "Test with assistive technology"),
    }
    return base_goals.get(archetype, ("Evaluate this product",))
