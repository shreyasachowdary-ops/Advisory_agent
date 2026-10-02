"""Deterministic play-based activity plan generator."""

from typing import Any

PLAN_TEMPLATES: dict[str, dict[str, Any]] = {
    "turn_taking_during_play": {
        "title": "Turn-Taking During Play",
        "setup": "Pair of identical toys (blocks, cars, or cups) and a sand timer or visual timer.",
        "adult_language": [
            "My turn… your turn.",
            "You waited — thank you for waiting.",
            "The timer shows when it's your turn.",
        ],
        "steps": [
            "Day 1–2: Adult models turn-taking with a 30-second timer during a favourite game.",
            "Day 3: Child and peer take turns with adult coaching; celebrate waiting.",
            "Day 4: Introduce a 'waiting mat' — child holds a card while waiting.",
            "Day 5: Short cooperative game (rolling a ball back and forth) with minimal prompts.",
        ],
        "observation_prompt": "Note how long the child can wait before needing a prompt. Record one success each day.",
    },
    "morning_routine": {
        "title": "Gentle Morning Routine",
        "setup": "Picture schedule with 3–4 steps (wake up, wash, dress, bag).",
        "adult_language": [
            "First we… then we…",
            "You did the first step — what's next on our pictures?",
            "We have time; let's do this together.",
        ],
        "steps": [
            "Day 1: Walk through picture schedule together; child points to each step.",
            "Day 2: Child completes one step independently (e.g. putting on shoes).",
            "Day 3: Add a 'ready song' or chime when the routine starts.",
            "Day 4–5: Practise the sequence with fewer reminders; praise specific efforts.",
        ],
        "observation_prompt": "Which step causes the most difficulty? Note mood at drop-off after the routine.",
    },
    "sharing_toys": {
        "title": "Learning to Share",
        "setup": "Duplicate toys and a 'sharing timer' (2-minute visual timer).",
        "adult_language": [
            "When the timer rings, it's time to swap.",
            "You can ask: 'Can I have a turn when you're done?'",
            "Sharing means we both get to play.",
        ],
        "steps": [
            "Day 1: Adult models asking for a turn and waiting.",
            "Day 2: Use timer for short turns with popular toys.",
            "Day 3: Teach phrase: 'Can I play when you're finished?'",
            "Day 4–5: Peer play with timer; adult coaches conflict moments.",
        ],
        "observation_prompt": "Does the child use words or physical grabbing? Note one positive sharing moment daily.",
    },
    "separation_anxiety": {
        "title": "Easing Separation at Drop-Off",
        "setup": "Small comfort object (if school allows), goodbye ritual card.",
        "adult_language": [
            "I will come back after [activity].",
            "Your teachers will keep you safe.",
            "One hug, then I'll wave from the door.",
        ],
        "steps": [
            "Day 1: Establish a consistent 3-step goodbye ritual (hug, wave, phrase).",
            "Day 2: Keep goodbye brief and confident; teacher engages child immediately.",
            "Day 3: Child holds comfort object during first activity.",
            "Day 4–5: Gradually reduce time at door; teacher sends a brief 'settled' update.",
        ],
        "observation_prompt": "How many minutes until the child engages in an activity? Track each morning.",
    },
    "default": {
        "title": "Play-Based Learning Plan",
        "setup": "Simple open-ended materials (blocks, crayons, containers, natural items).",
        "adult_language": [
            "I wonder what you could make…",
            "Tell me about your idea.",
            "You worked hard on that.",
        ],
        "steps": [
            "Day 1: Free exploration with one material; adult narrates child's actions.",
            "Day 2: Introduce a simple goal (build a tower, draw a circle).",
            "Day 3: Add a social element — build together or side by side.",
            "Day 4–5: Child leads the play; adult asks open questions.",
        ],
        "observation_prompt": "What does the child choose to do? Note engagement time and one new skill.",
    },
}


def create_activity_plan(
    age_band: str,
    goal: str,
    available_minutes_per_day: int = 15,
    days: int = 5,
    setting: str = "home",
) -> dict[str, Any]:
    """Generate a deterministic, editable play-based plan."""
    template = PLAN_TEMPLATES.get(goal, PLAN_TEMPLATES["default"])
    setting_note = (
        "Adapt materials to classroom centres and group size."
        if setting == "classroom"
        else "Use everyday home materials and routines."
    )

    daily_plan = []
    for day in range(1, min(days, 5) + 1):
        step_idx = min(day - 1, len(template["steps"]) - 1)
        daily_plan.append(
            {
                "day": day,
                "duration_minutes": available_minutes_per_day,
                "activity": template["steps"][step_idx],
            }
        )

    return {
        "plan_id": f"plan_{goal}_{age_band}",
        "title": template["title"],
        "age_band": age_band,
        "goal": goal,
        "setting": setting,
        "setting_note": setting_note,
        "setup": template["setup"],
        "adult_language": template["adult_language"],
        "daily_plan": daily_plan,
        "observation_prompt": template["observation_prompt"],
        "editable": True,
        "generated_by": "deterministic_template",
    }
