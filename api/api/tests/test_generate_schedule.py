# tests/test_generate_schedule_view.py
from django.test import TestCase, RequestFactory
from api.views.generate_schedule import GenerateSchedule
from api.models import Class

class GenerateScheduleViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = GenerateSchedule.as_view()
        self.class1 = Class.objects.create(name="Class 1", schedule="08:00-10:00")
        self.class2 = Class.objects.create(name="Class 2", schedule="10:00-12:00")

    def test_generate_schedule(self):
        request = self.factory.post(
            '/generate-schedule/',
            {'classes': [self.class1.id, self.class2.id], 'preference': [1, 2, 3]},
            content_type='application/json'
        )
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('schedules', response.data)
        self.assertIn('message', response.data)
