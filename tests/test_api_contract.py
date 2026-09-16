import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.schemas import ScheduleRequest, TaskAnalysisRequest
from backend.app.scheduler import Scheduler
from backend.app.service import AnalysisService, clean_priority_text


class FakeRuntime:
    def predict_context(self, task_title, list_title):
        return {
            'input_text': f'{task_title} [SEP] {list_title}',
            'time_slots': [{'label': 'WD-morning', 'probability': 0.8}],
            'location': {'label': 'home', 'probability': 0.9},
        }

    def predict_priority(self, text):
        return {
            'label': 'Major',
            'probability': 0.7,
            'probabilities': [
                {'label': 'Major', 'probability': 0.7},
                {'label': 'Minor', 'probability': 0.3},
            ],
        }

    def predict_effort(self, text):
        return {
            'status': 'ready',
            'bucket': 'M',
            'difficulty': 'medium',
            'probability': 0.65,
            'probabilities': [
                {'label': 'M', 'probability': 0.65},
                {'label': 'S', 'probability': 0.2},
                {'label': 'L', 'probability': 0.15},
            ],
            'estimated_minutes': 90,
            'estimated_range_minutes': {'low': 60, 'high': 120},
            'source': 'jira_effort_bucket_model',
            'proxy_domain': 'Jira software issues',
        }


class APIContractTests(unittest.TestCase):
    def setUp(self):
        self.service = AnalysisService(runtime=FakeRuntime())

    def test_priority_preprocessing_masks_leakage(self):
        cleaned = clean_priority_text('Fix a critical outage', 'Deploy ASAP after review')
        self.assertNotIn('critical', cleaned.lower())
        self.assertNotIn('asap', cleaned.lower())
        self.assertEqual(cleaned.count('[MASK]'), 2)

    def test_analysis_preserves_user_deadline_and_duration(self):
        request = TaskAnalysisRequest(
            task_title='Finish report', list_title='university', description='Submit PDF',
            importance=True, deadline=datetime(2026, 10, 18, 17, tzinfo=timezone.utc),
            duration_override_minutes=90,
        )
        response = self.service.analyze(request)
        self.assertEqual(response.temporal.deadline_source, 'user')
        self.assertEqual(response.temporal.duration_source, 'user_override')
        self.assertEqual(response.quadrant, 'Q2 - Schedule')
        self.assertEqual(response.priority.label, 'Major')

    def test_scheduler_uses_explicit_user_duration(self):
        request = ScheduleRequest(
            tasks=[TaskAnalysisRequest(task_title='Write report', duration_override_minutes=60, importance=True)],
            horizon='day', available_hours_per_day=2, preferred_start_time='09:00',
            start_date=datetime(2026, 9, 16, tzinfo=timezone.utc),
        )
        result = Scheduler(self.service).schedule(request)
        self.assertEqual(len(result.sessions), 1)
        self.assertEqual(result.sessions[0].duration_minutes, 60)
        self.assertEqual(result.sessions[0].duration_source, 'user_override')

    def test_effort_candidate_becomes_effective_duration(self):
        response = self.service.analyze(TaskAnalysisRequest(task_title='Prepare presentation'))
        self.assertEqual(response.effort['status'], 'ready')
        self.assertEqual(response.effort['bucket'], 'M')
        self.assertEqual(response.effort['difficulty'], 'medium')
        self.assertEqual(response.temporal.duration_source, 'effort_model')
        self.assertEqual(response.temporal.duration_override_minutes, 90)
        self.assertNotIn('Effort is a coarse Jira transfer/proxy estimate', ' '.join(response.warnings))

    def test_model_duration_is_split_across_available_days(self):
        request = ScheduleRequest(
            tasks=[TaskAnalysisRequest(task_title='Prepare presentation', importance=True)],
            horizon='week', available_hours_per_day=1, preferred_start_time='09:00',
            start_date=datetime(2026, 9, 16, tzinfo=timezone.utc),
        )
        result = Scheduler(self.service).schedule(request)
        self.assertEqual([item.duration_minutes for item in result.sessions], [60, 30])
        self.assertTrue(all(item.duration_source == 'effort_model' for item in result.sessions))


if __name__ == '__main__':
    unittest.main()
