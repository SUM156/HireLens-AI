"""
Tests for scorer.py — grading logic, color thresholds, and section result
interpretation. No AI calls here; all inputs are manually constructed dicts.
"""

import unittest

from src.scorer import (
    grade_score, interpret_section_scores,
    get_overall_verdict,
)


class TestGradeScore(unittest.TestCase):
    def test_perfect_score_is_a_plus(self):
        grade, color, emoji = grade_score(100)
        self.assertEqual(grade, "A+")
        self.assertIn("green", color)

    def test_90_is_a(self):
        grade, _, _ = grade_score(90)
        self.assertEqual(grade, "A")

    def test_75_is_b_plus(self):
        grade, _, _ = grade_score(82)
        self.assertEqual(grade, "B+")

    def test_55_is_d(self):
        grade, _, _ = grade_score(55)
        self.assertEqual(grade, "D")

    def test_zero_is_f(self):
        grade, color, _ = grade_score(0)
        self.assertEqual(grade, "F")
        self.assertIn("red", color)

    def test_score_above_100_clamped(self):
        # Scores > 100 should behave the same as 100
        grade, _, _ = grade_score(120)
        self.assertEqual(grade, "A+")

    def test_score_below_0_clamped(self):
        grade, _, _ = grade_score(-10)
        self.assertEqual(grade, "F")


class TestInterpretSectionScores(unittest.TestCase):
    def _make_analysis(self):
        """Build a minimal valid analysis dict for testing."""
        return {
            "section_scores": {
                "contact_info": 90,
                "summary": 40,
                "experience": 70,
                "education": 85,
                "skills": 60,
                "projects": 55,
                "formatting": 95,
            },
            "section_feedback": {
                "contact_info": "Good.",
                "summary": "Too vague.",
                "experience": "Needs quantification.",
                "education": "Solid.",
                "skills": "Average.",
                "projects": "Too brief.",
                "formatting": "Excellent.",
            },
        }

    def test_returns_list_of_section_results(self):
        results = interpret_section_scores(self._make_analysis())
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_sorted_lowest_first(self):
        results = interpret_section_scores(self._make_analysis())
        scores = [r.score for r in results]
        self.assertEqual(scores, sorted(scores))

    def test_worst_section_is_summary(self):
        results = interpret_section_scores(self._make_analysis())
        self.assertEqual(results[0].score, 40)  # summary at 40 should be first

    def test_all_seven_sections_returned(self):
        results = interpret_section_scores(self._make_analysis())
        self.assertEqual(len(results), 7)

    def test_missing_section_defaults_to_zero(self):
        analysis = self._make_analysis()
        del analysis["section_scores"]["summary"]
        del analysis["section_feedback"]["summary"]
        results = interpret_section_scores(analysis)
        summary_result = next(r for r in results if r.name == "Professional Summary")
        self.assertEqual(summary_result.score, 0)


class TestGetOverallVerdict(unittest.TestCase):
    def test_90_plus_is_outstanding(self):
        headline, _ = get_overall_verdict(95)
        self.assertIn("Outstanding", headline)

    def test_80_range_is_strong(self):
        headline, _ = get_overall_verdict(83)
        self.assertIn("Strong", headline)

    def test_below_60_is_major_revision(self):
        headline, _ = get_overall_verdict(45)
        self.assertIn("Major Revision", headline)

    def test_returns_tuple_of_two_strings(self):
        result = get_overall_verdict(70)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], str)


if __name__ == "__main__":
    unittest.main()