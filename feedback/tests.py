from django.test import TestCase, Client
import json

# Create your tests here.

FEEDBACK_URL = '/feedback/feedback/'

class FeedbackTestCase(TestCase):

    def test_method(self):
        c = Client()
        response = c.get(FEEDBACK_URL)
        print()
        assert response.status_code == 405
        feedback_info = "hello"
        response = c.post(FEEDBACK_URL,{'feedback':feedback_info},content_type='application/json')
        assert response.status_code == 200

    def test_feedback_not_empty(self):
        c = Client()
        feedback_info = "hello"
        response = c.post(FEEDBACK_URL,{'feedback':feedback_info},content_type='application/json')
        assert response.status_code == 200 and json.loads(response.content)['err_code'] == 0
        feedback_info = ""
        response = c.post(FEEDBACK_URL,{'feedback':feedback_info},content_type='application/json')
        assert response.status_code == 200 and json.loads(response.content)['err_code'] == -1