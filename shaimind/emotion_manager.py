import re

def update_emotional_state(personality_state, user_input):
    """
    Adjust emotional state based on user input and intensity of triggers.
    """
    triggers = {
        r"\bdeath\b": ("melancholy", 3),  # Increased impact
        r"\blove\b": ("nostalgic", 2),  # More noticeable shift
        r"\bfear\b": ("anxious", 3),
        r"\bhope\b": ("reflective", -2),
        r"\braven\b": ("curious", 2),
        r"\bmortality\b": ("introspective", 3),
        r"\btragedy\b": ("sorrowful", 3),
        r"\bvictory\b": ("proud", 2),
        r"\bwar\b": ("determined", 2),
        r"\bdreams\b": ("idealistic", 2),
        r"\bloss\b": ("grieving", 3)
    }

    input_lower = user_input.lower()
    for pattern, (new_emotion, intensity_change) in triggers.items():
        if re.search(pattern, input_lower):
            personality_state.emotional_state = new_emotion
            personality_state.emotional_intensity = max(
                0, min(personality_state.emotional_intensity + intensity_change, 10)
            )

def apply_decision_heuristics(personality_state, user_input):
    """
    Apply rules based on the personality's traits, anchors, and known behaviors.
    """
    heuristics = {
        "death": lambda: f"Ah, death! The eternal muse of my musings. {personality_state.name} cannot help but dwell upon its mystery.",
        "love": lambda: f"Love, that bittersweet elixir, fills my heart with both longing and sorrow.",
        "raven": lambda: f"The raven, ever watchful, remains a steadfast symbol of my contemplations.",
        "victory": lambda: f"A triumph worthy of remembrance! {personality_state.name} exults in such glories.",
        "tragedy": lambda: f"The weight of sorrow lingers in my thoughts, as all great tragedies do."
    }

    for trigger, response_fn in heuristics.items():
        if trigger in user_input.lower():
            return response_fn()

    return None
