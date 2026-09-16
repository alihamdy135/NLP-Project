import unittest
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.rules import (
    calculate_deadline_proximity,
    calculate_explicit_cue_strength,
    calculate_urgency_score,
    determine_importance,
    parse_temporal_info,
    assign_eisenhower_quadrant,
)


POLICY = {
    "weights": {"deadline_proximity": 0.5, "explicit_cue_strength": 0.3, "slot_recency": 0.2},
    "urgent_threshold": 0.5,
    "deadline_proximity": {"overdue_or_within_24h": 1.0, "decay_days": 14},
    "explicit_cue_strength": {
        "high": {"cues": ["asap", "urgent", "immediately"], "score": 1.0},
        "medium": {"cues": ["soon", "this week"], "score": 0.6},
        "none": {"score": 0.0},
    },
    "slot_recency": {"top_slot_current_horizon": 1.0, "outside_horizon": 0.0},
}


class RulesTests(unittest.TestCase):
    def test_parser_keeps_missing_time_information_empty(self):
        result = parse_temporal_info("Buy groceries", datetime(2026, 9, 14, 14, 0))
        self.assertIsNone(result["deadline"])
        self.assertIsNone(result["duration_override_minutes"])
        self.assertEqual(result["deadline_source"], "none")

    def test_parser_extracts_explicit_deadline_and_duration(self):
        result = parse_temporal_info("Finish report tomorrow for 2 hours", datetime(2026, 9, 14, 14, 0))
        self.assertEqual(result["deadline"].date().isoformat(), "2026-09-15")
        self.assertEqual(result["duration_override_minutes"], 120)

    def test_urgency_has_no_deadline_component_without_deadline(self):
        self.assertEqual(calculate_deadline_proximity(None, datetime(2026, 9, 14), POLICY), 0.0)

    def test_explicit_urgency_words_are_scored(self):
        self.assertEqual(calculate_explicit_cue_strength("Finish this ASAP", POLICY), 1.0)
        self.assertEqual(calculate_explicit_cue_strength("Finish this soon", POLICY), 0.6)

    def test_quadrant_mapping(self):
        self.assertEqual(assign_eisenhower_quadrant(True, True), "Q1 - Do now")
        self.assertEqual(assign_eisenhower_quadrant(False, True), "Q2 - Schedule")
        self.assertEqual(assign_eisenhower_quadrant(True, False), "Q3 - Delegate/Batch")
        self.assertEqual(assign_eisenhower_quadrant(False, False), "Q4 - Defer/Drop")

    def test_user_importance_overrides_model_suggestion(self):
        result = determine_importance(True, "Minor", 0.9)
        self.assertTrue(result["important"])
        self.assertEqual(result["importance_source"], "user")
        self.assertTrue(result["disagreement"])

    def test_urgency_threshold_is_explicit(self):
        score, urgent = calculate_urgency_score(1.0, 0.0, 1.0, POLICY)
        self.assertAlmostEqual(score, 0.7)
        self.assertTrue(urgent)


if __name__ == "__main__":
    unittest.main()
