import json
from pathlib import Path

from django.test import TestCase, Client
from django.conf import settings


class DevTrackAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self._reset_json('reporters.json')
        self._reset_json('issues.json')

    def _reset_json(self, filename):
        path = settings.BASE_DIR / filename
        path.write_text('[]', encoding='utf-8')

    def test_create_reporter(self):
        response = self.client.post(
            '/api/reporters/',
            data=json.dumps({
                'id': 1,
                'name': 'Alice',
                'email': 'alice@team.com',
                'team': 'backend',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'Alice')

    def test_reporter_validation_failure(self):
        response = self.client.post(
            '/api/reporters/',
            data=json.dumps({
                'id': 1,
                'name': '',
                'email': 'alice@team.com',
                'team': 'backend',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Name cannot be empty')

    def test_get_reporter_by_id(self):
        self.client.post(
            '/api/reporters/',
            data=json.dumps({
                'id': 1, 'name': 'Bob', 'email': 'bob@x.com', 'team': 'devops',
            }),
            content_type='application/json',
        )
        response = self.client.get('/api/reporters/?id=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], 1)

    def test_reporter_not_found(self):
        response = self.client.get('/api/reporters/?id=99')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Reporter not found')

    def test_create_critical_issue(self):
        response = self.client.post(
            '/api/issues/',
            data=json.dumps({
                'id': 1,
                'title': 'Login button not working on mobile',
                'description': 'Users on iOS 17 cannot tap the login button',
                'status': 'open',
                'priority': 'critical',
                'reporter_id': 1,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(
            body['message'],
            '[URGENT] Login button not working on mobile — needs immediate attention',
        )

    def test_create_low_priority_issue(self):
        response = self.client.post(
            '/api/issues/',
            data=json.dumps({
                'id': 2,
                'title': 'Typo in footer',
                'description': 'Minor text fix',
                'status': 'open',
                'priority': 'low',
                'reporter_id': 1,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('low priority', response.json()['message'])

    def test_create_high_priority_uses_base_issue(self):
        response = self.client.post(
            '/api/issues/',
            data=json.dumps({
                'id': 3,
                'title': 'API timeout',
                'description': 'Slow response',
                'status': 'open',
                'priority': 'high',
                'reporter_id': 1,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'API timeout [high]')

    def test_issue_validation_failure(self):
        response = self.client.post(
            '/api/issues/',
            data=json.dumps({
                'id': 1,
                'title': '',
                'description': 'x',
                'status': 'open',
                'priority': 'high',
                'reporter_id': 1,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Title cannot be empty')

    def test_get_issue_by_id(self):
        self.client.post(
            '/api/issues/',
            data=json.dumps({
                'id': 1, 'title': 'Bug', 'description': 'd',
                'status': 'open', 'priority': 'medium', 'reporter_id': 1,
            }),
            content_type='application/json',
        )
        response = self.client.get('/api/issues/?id=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], 1)

    def test_issue_not_found(self):
        response = self.client.get('/api/issues/?id=99')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], 'Issue not found')

    def test_filter_issues_by_status(self):
        self.client.post(
            '/api/issues/',
            data=json.dumps({
                'id': 1, 'title': 'Open bug', 'description': 'd',
                'status': 'open', 'priority': 'low', 'reporter_id': 1,
            }),
            content_type='application/json',
        )
        self.client.post(
            '/api/issues/',
            data=json.dumps({
                'id': 2, 'title': 'Closed bug', 'description': 'd',
                'status': 'closed', 'priority': 'low', 'reporter_id': 1,
            }),
            content_type='application/json',
        )
        response = self.client.get('/api/issues/?status=open')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['status'], 'open')
