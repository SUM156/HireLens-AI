"""
analyzer.py (FREE MODE)
----------------------
Offline resume analyzer (no Anthropic API required).
Returns structured analysis compatible with scorer.py and reporter.py.
"""

import json


class AnalysisError(Exception):
    pass


def _call_claude_api(resume_text: str) -> str:
    """
    FREE MODE: Generates fake AI response locally
    """
    fake_response = {
        "overall_score": 80,
        "ats_score": 75,
        "section_scores": {
            "contact_info": 85,
            "summary": 70,
            "experience": 80,
            "education": 78,
            "skills": 76,
            "projects": 82,
            "formatting": 80
        },
        "strengths": [
            "Clear structure and formatting",
            "Relevant technical experience",
            "Good project explanations"
        ],
        "critical_issues": [
            "Lack of measurable achievements",
            "Weak action verbs",
            "Missing ATS keywords"
        ],
        "ats_keywords_found": ["Python", "SQL", "Git"],
        "ats_keywords_missing": ["Docker", "AWS", "CI/CD"],
        "improved_bullets": [
            {
                "original": "Worked on backend system",
                "improved": "Built and optimized backend system improving performance by 30%"
            }
        ],
        "section_feedback": {
            "contact_info": "Good but can include LinkedIn profile",
            "summary": "Needs stronger impact statement",
            "experience": "Relevant but not quantified",
            "education": "Satisfactory",
            "skills": "Missing modern tools",
            "projects": "Good but needs metrics",
            "formatting": "Clean and readable"
        },
        "one_line_verdict": "Strong entry-level resume with room for improvement."
    }

    return json.dumps(fake_response)


def _parse_json_response(raw_text: str) -> dict:
    """
    Convert JSON string → Python dict
    """
    try:
        return json.loads(raw_text)
    except Exception as e:
        raise AnalysisError(f"Invalid JSON response: {e}")


def analyze_resume(resume_text: str) -> dict:
    """
    Main function used by cli.py
    """
    if not resume_text or len(resume_text.strip()) < 50:
        raise AnalysisError("Resume text too short")

    raw_response = _call_claude_api(resume_text)
    analysis = _parse_json_response(raw_response)

    # Basic validation
    required_keys = [
        "overall_score",
        "ats_score",
        "section_scores",
        "strengths",
        "critical_issues",
        "section_feedback"
    ]

    missing = [k for k in required_keys if k not in analysis]
    if missing:
        raise AnalysisError(f"Missing keys: {missing}")

    return analysis