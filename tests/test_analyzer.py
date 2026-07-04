"""
Tests for analyzer.py — covers JSON parsing, schema validation,
and error handling. The actual Claude API call is always mocked
so tests run instantly and never cost API credits.
"""

import json
import unittest
from unittest.mock import patch, MagicMock

from src.analyzer import analyze_resume, _parse_json_response, AnalysisError


# A realistic fake analysis dict that Claude would return
FAKE_ANALYSIS = {
    "overall_score": 72,
    "ats_score": 65,
    "section_scores": {
        "contact_info": 85, "summary": 50, "experience": 70,
        "education": 90, "skills": 80, "projects": 60, "formatting": 75,
    },
    "strengths": ["Good education section", "Relevant skills listed"],
    "critical_issues": ["Experience bullets lack quantification", "Summary is generic"],
    "ats_keywords_found": ["Python", "Machine Learning"],
    "ats_keywords_missing": ["TensorFlow", "PyTorch", "Data Pipeline"],
    "improved_bullets": [
        {
            "original": "Worked on machine learning models",
            "improved": "Developed and deployed 3 ML classification models using scikit-learn, achieving 94% accuracy on test data",
        }
    ],
    "section_feedback": {
        "contact_info": "Good.", "summary": "Too vague.",
        "experience": "Add numbers.", "education": "Excellent.",
        "skills": "Good list.", "projects": "Add links.", "formatting": "Clean.",
    },
    "one_line_verdict": "A promising AI student resume that needs quantified achievements.",
}


class TestParseJsonResponse(unittest.TestCase):
    def test_parses_valid_json(self):
        raw = json.dumps(FAKE_ANALYSIS)
        result = _parse_json_response(raw)
        self.assertEqual(result["overall_score"], 72)

    def test_strips_markdown_json_fences(self):
        # Claude sometimes wraps output in ```json ... ``` even when asked not to
        raw = f"```json\n{json.dumps(FAKE_ANALYSIS)}\n```"
        result = _parse_json_response(raw)
        self.assertEqual(result["ats_score"], 65)

    def test_strips_plain_code_fences(self):
        raw = f"```\n{json.dumps(FAKE_ANALYSIS)}\n```"
        result = _parse_json_response(raw)
        self.assertIn("section_scores", result)

    def test_invalid_json_raises_analysis_error(self):
        with self.assertRaises(AnalysisError):
            _parse_json_response("{this is not valid json}")

    def test_empty_string_raises_analysis_error(self):
        with self.assertRaises(AnalysisError):
            _parse_json_response("")


class TestAnalyzeResume(unittest.TestCase):
    def test_empty_text_raises(self):
        with self.assertRaises(AnalysisError):
            analyze_resume("")

    def test_too_short_text_raises(self):
        with self.assertRaises(AnalysisError):
            analyze_resume("Hi")

    @patch("src.analyzer._call_claude_api", return_value=json.dumps(FAKE_ANALYSIS))
    def test_valid_analysis_returns_dict(self, mock_call):
        result = analyze_resume("Sumair Ahmed\n" + "Python ML engineer " * 20)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["overall_score"], 72)

    @patch("src.analyzer._call_claude_api", return_value=json.dumps(FAKE_ANALYSIS))
    def test_all_required_keys_present(self, mock_call):
        result = analyze_resume("Resume text " * 10)
        for key in ["overall_score", "ats_score", "section_scores",
                    "strengths", "critical_issues", "section_feedback"]:
            self.assertIn(key, result)

    @patch("src.analyzer._call_claude_api", return_value='{"overall_score": 80}')
    def test_missing_required_keys_raises(self, mock_call):
        # Response is valid JSON but missing required fields — should raise
        with self.assertRaises(AnalysisError):
            analyze_resume("Resume text " * 10)

    @patch("src.analyzer._call_claude_api", side_effect=AnalysisError("network down"))
    def test_api_failure_propagates(self, mock_call):
        with self.assertRaises(AnalysisError):
            analyze_resume("Resume text " * 10)

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key_raises(self):
        # When ANTHROPIC_API_KEY is not set, the call should fail immediately
        import os
        os.environ.pop("ANTHROPIC_API_KEY", None)
        with self.assertRaises(AnalysisError):
            analyze_resume("Resume text " * 10)


if __name__ == "__main__":
    unittest.main()