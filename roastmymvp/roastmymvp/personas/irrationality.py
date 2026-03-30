"""Irrationality injection — makes ~30% of personas behave non-rationally.

Real users aren't rational. They abandon products for weird reasons,
fixate on irrelevant details, or refuse to read instructions.
This module injects realistic irrational behaviors.
"""

import random

# Each modifier is a behavioral constraint that changes how the persona evaluates
_IRRATIONALITY_MODIFIERS = (
    "You refuse to sign up or create an account for anything. If it requires signup, you leave immediately.",
    "You are in a terrible rush. You give everything exactly 10 seconds before moving on.",
    "You are deeply suspicious of any product that looks too polished — you assume it's a scam.",
    "You obsessively check for a dark mode. If there's no dark mode, you lose 3 points of enthusiasm.",
    "You judge every product primarily by its loading speed. If it takes more than 2 seconds, it's garbage.",
    "You refuse to read any text longer than one sentence. You navigate entirely by buttons and visuals.",
    "You just had a bad experience with a similar product and are primed to hate this one.",
    "You are testing this product while commuting on a crowded train with spotty internet.",
    "You have strong opinions about typography. Bad font choices ruin your entire experience.",
    "You immediately try to break things — weird inputs, rapid clicks, back button spam.",
    "You are comparing this to a product you loved that shut down. Nothing will ever be as good.",
    "You only trust products recommended by friends. You found this randomly and are extra skeptical.",
    "You care more about the about page and team info than the actual product.",
    "You have decision fatigue and will choose whichever option requires the fewest clicks.",
    "You are distracted — you keep switching tabs and forgetting what you were doing.",
    "You are testing this for your boss and need to write a report. You're looking for reasons to reject it.",
    "You will only use this product if it works perfectly on mobile. Desktop is irrelevant to you.",
    "You're a privacy hawk. You check for cookie banners, privacy policies, and tracking scripts first.",
    "You refuse to use any product that uses AI/ML buzzwords in its marketing.",
    "You evaluate products by trying the most advanced feature first, ignoring onboarding entirely.",
)


def inject_irrationality(
    rng: random.Random,
    injection_rate: float = 0.3,
) -> str | None:
    """Return an irrationality modifier with ~30% probability."""
    if rng.random() < injection_rate:
        return rng.choice(_IRRATIONALITY_MODIFIERS)
    return None
