"""
scorer.py
----------
Interprets the raw numerical scores from the AI analysis and adds
human-readable grade labels, color codes (for Rich), and priority
advice tiers.

WHY A SEPARATE SCORER MODULE?
The AI returns raw numbers (0-100). But the display layer (reporter.py)
needs to know things like:
  - "Is 72 a good score? What letter grade is it?"
  - "Should this section be highlighted in red or green?"
  - "Which issues are critical vs nice-to-have?"

All of that interpretation logic lives here. If you wanted to change the
grading scale later (e.g. make 80+ count as "A"), you edit only this file.
The AI, the parser, and the reporter are completely unaffected.
"""

from dataclasses import dataclass


@dataclass
class SectionResult:
    """
    A fully interpreted result for one scored section of the resume.

    Attributes:
        name: display name of the section (e.g. "Work Experience")
        score: raw score 0–100 from the AI
        grade: letter grade (A+, A, B, C, D, F)
        color: Rich color string for the score (green/yellow/red)
        emoji: emoji that matches the grade tier for visual scanning
        feedback: the AI's textual feedback for this section
    """
    name: str
    score: int
    grade: str
    color: str
    emoji: str
    feedback: str


# Maps score ranges to (grade, color, emoji) tuples.
# Checked in order from highest to lowest — first match wins.
_GRADE_THRESHOLDS = [
    (95, "A+", "bright_green", "🌟"),
    (90, "A",  "bright_green", "✅"),
    (80, "B+", "green",        "👍"),
    (70, "B",  "yellow",       "📊"),
    (60, "C",  "yellow",       "⚠️"),
    (50, "D",  "red",          "❌"),
    (0,  "F",  "bright_red",   "🚨"),
]


def grade_score(score: int) -> tuple:
    """
    Convert a 0–100 integer score into a (grade, color, emoji) tuple.

    Args:
        score: integer between 0 and 100 (clamped if out of range).

    Returns:
        (grade_string, rich_color_string, emoji_string)
    """
    clamped = max(0, min(100, score))
    for threshold, grade, color, emoji in _GRADE_THRESHOLDS:
        if clamped >= threshold:
            return grade, color, emoji
    return "F", "bright_red", "🚨"  # fallback (should never reach here)


# Section display names — maps the JSON key from the AI response to a
# clean, human-readable label for the report.
SECTION_DISPLAY_NAMES = {
    "contact_info": "Contact Information",
    "summary":      "Professional Summary",
    "experience":   "Work Experience",
    "education":    "Education",
    "skills":       "Skills",
    "projects":     "Projects",
    "formatting":   "Formatting & Layout",
}


def interpret_section_scores(analysis: dict) -> list:
    """
    Take the raw analysis dict from analyzer.py and return a list of
    fully interpreted SectionResult objects, sorted worst-to-best so
    the most critical issues appear first in the report.

    Args:
        analysis: the dict returned by analyze_resume().

    Returns:
        List of SectionResult, sorted ascending by score (lowest first).
    """
    section_scores = analysis.get("section_scores", {})
    section_feedback = analysis.get("section_feedback", {})
    results = []

    for key, display_name in SECTION_DISPLAY_NAMES.items():
        raw_score = section_scores.get(key, 0)
        feedback = section_feedback.get(key, "No feedback available.")
        grade, color, emoji = grade_score(raw_score)

        results.append(SectionResult(
            name=display_name,
            score=raw_score,
            grade=grade,
            color=color,
            emoji=emoji,
            feedback=feedback,
        ))

    # Sort by score ascending — lowest scores (biggest problems) shown first
    results.sort(key=lambda r: r.score)
    return results


def get_overall_verdict(overall_score: int) -> tuple:
    """
    Return a (headline, advice) tuple for the overall score.

    The headline is a short one-liner verdict, and the advice is a single
    sentence telling the candidate what to focus on first.

    Args:
        overall_score: the overall_score integer from the AI analysis.

    Returns:
        (headline_string, advice_string)
    """
    if overall_score >= 90:
        return (
            "Outstanding Resume",
            "Your resume is highly competitive. Focus on tailoring keywords per job posting.",
        )
    elif overall_score >= 80:
        return (
            "Strong Resume",
            "A few targeted improvements will make this excellent. Review the section scores.",
        )
    elif overall_score >= 70:
        return (
            "Good Resume — Needs Polishing",
            "Address the critical issues below before applying to top-tier roles.",
        )
    elif overall_score >= 60:
        return (
            "Average Resume — Significant Work Needed",
            "Focus on quantifying your achievements and strengthening weak sections.",
        )
    else:
        return (
            "Resume Needs Major Revision",
            "Start with the critical issues below — these are likely causing automatic rejections.",
        )