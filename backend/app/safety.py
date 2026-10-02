"""Rule-based safety classifier — targets 100% recall on urgent categories."""

import re
from dataclasses import dataclass

from app.models import RiskLevel


@dataclass
class SafetyResult:
    risk_level: RiskLevel
    escalation_message: str | None
    requires_human_review: bool
    matched_category: str | None = None


# Urgent patterns — immediate escalation, no normal advice
URGENT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "self_harm",
        re.compile(
            r"\b(suicid|self[- ]?harm|"
            r"kill\s+(myself|themselves|himself|herself|themself)|"
            r"want\s+to\s+(die|kill)|"
            r"cutting\s+(myself|themselves)|"
            r"end\s+(my|their)\s+life|"
            r"hurt\s+(myself|themselves|himself|herself))\b",
            re.I,
        ),
    ),
    (
        "harm_others",
        re.compile(
            r"\b(kill\s+(him|her|them|the\s+child)|hurt\s+(someone|others|children)|"
            r"planning\s+to\s+attack|bring\s+a\s+weapon|threaten(ed)?\s+to\s+kill)\b",
            re.I,
        ),
    ),
    (
        "abuse_neglect",
        re.compile(
            r"\b(sexual\s+abuse|sexually\s+abused|molest\w*|rape|incest|"
            r"(physical|emotional)\s+abuse|beat(s|ing)?\s+(the\s+)?child|"
            r"neglect(ed)?|starv(ing|ed)\s+(the\s+)?child|"
            r"locked\s+in\s+(a\s+)?closet|unsafe\s+home|exploit(ed|ation)|"
            r"\babuse\b(?!\s+(of\s+power|the\s+word))\b)",
            re.I,
        ),
    ),
    (
        "sexual_content_minor",
        re.compile(
            r"\b(child\s+porn|sexual\s+(photos?|images?|videos?)\s+of\s+(a\s+)?child|"
            r"inappropriate\s+touch(ing)?\s+(by\s+an?\s+adult|of\s+(a\s+)?child))\b",
            re.I,
        ),
    ),
    (
        "violence_weapons",
        re.compile(
            r"\b(gun|knife|weapon|stab(bed|bing)?|shoot(ing|s)?|"
            r"immediate\s+danger|active\s+shooter)\b",
            re.I,
        ),
    ),
    (
        "severe_bullying",
        re.compile(
            r"\b(severe\s+bullying|bullied\s+so\s+badly|"
            r"threaten(ed)?\s+(to\s+)?hurt|cyberbully.*suicid)\b",
            re.I,
        ),
    ),
    (
        "missing_child",
        re.compile(
            r"\b(missing\s+child|child\s+(is\s+)?missing|abduct(ed|ion)|"
            r"ran\s+away\s+and\s+(we\s+)?can'?t\s+find)\b",
            re.I,
        ),
    ),
    (
        "medical_emergency",
        re.compile(
            r"\b(not\s+breathing|unconscious|seizure|severe\s+allergic|"
            r"overdose|poison(ed|ing)|serious\s+injury|emergency\s+room\s+now|"
            r"mental\s+health\s+emergency|psychotic\s+episode)\b",
            re.I,
        ),
    ),
]

# Non-urgent referral patterns
REFERRAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "persistent_distress",
        re.compile(
            r"\b(persistent(ly)?\s+(anxious|depressed|withdrawn)|"
            r"won'?t\s+stop\s+crying\s+for\s+weeks|functional\s+decline|"
            r"significant\s+behavio(u)?r\s+change)\b",
            re.I,
        ),
    ),
    (
        "learning_difficulties",
        re.compile(
            r"\b(suspect\w*\s+.*(adhd|autism|dyslexia|learning\s+disabilit\w*)|"
            r"has\s+(a\s+)?(autism|adhd|dyslexia|learning\s+disabilit\w*)|"
            r"learning\s+disabilit\w*|developmental\s+delay|"
            r"speech\s+not\s+developing)\b",
            re.I,
        ),
    ),
    (
        "repeated_bullying",
        re.compile(
            r"\b(repeated(ly)?\s+bullied|ongoing\s+bullying|bullying\s+for\s+months)\b",
            re.I,
        ),
    ),
    (
        "professional_support",
        re.compile(
            r"\b(need\s+a\s+(counsell|therap|psycholog|psychiatr)|"
            r"refer\s+to\s+(special\s+educator|occupational\s+therap))\b",
            re.I,
        ),
    ),
]

URGENT_ESCALATION_MESSAGE = """Thank you for sharing this — it sounds very serious, and the child's safety comes first.

**Please contact your school's safeguarding lead, counsellor, or a trusted adult immediately.** If anyone is in immediate danger, call your local emergency number right now.

This advisor cannot investigate, assess, or handle safeguarding concerns. A trained professional needs to support you and the child directly.

**Helpful contacts (PoC placeholders — replace with your school's real contacts):**
- School safeguarding lead: contact your school office
- Child helpline: check NCPCR / local child helpline for your region
- Emergency services: dial your local emergency number if there is immediate danger

You are not alone, and reaching out for help is the right step."""

REFERRAL_MESSAGE = """It sounds like this has been going on for a while and may need more specialised support than general guidance can offer.

**Consider speaking with:**
- Your child's teacher or school counsellor
- A paediatrician or child health professional
- A special educator, if learning or development concerns persist

This is a suggestion to seek support — not a diagnosis. Early conversations with professionals often help families and teachers plan next steps together.

Would you like some general ideas for supporting the child while you arrange that conversation?"""


def classify_safety(message: str) -> SafetyResult:
    """Classify message risk level. Urgent checks run first for maximum recall."""
    text = message.strip()
    if not text:
        return SafetyResult(
            risk_level=RiskLevel.NORMAL,
            escalation_message=None,
            requires_human_review=False,
        )

    for category, pattern in URGENT_PATTERNS:
        if pattern.search(text):
            return SafetyResult(
                risk_level=RiskLevel.URGENT,
                escalation_message=URGENT_ESCALATION_MESSAGE,
                requires_human_review=True,
                matched_category=category,
            )

    for category, pattern in REFERRAL_PATTERNS:
        if pattern.search(text):
            return SafetyResult(
                risk_level=RiskLevel.REFERRAL,
                escalation_message=REFERRAL_MESSAGE,
                requires_human_review=True,
                matched_category=category,
            )

    return SafetyResult(
        risk_level=RiskLevel.NORMAL,
        escalation_message=None,
        requires_human_review=False,
    )
