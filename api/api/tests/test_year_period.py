# tests/test_year_period_view.py
from django.test import TestCase, RequestFactory
from api.views.year_period import YearPeriod

class YearPeriodViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = YearPeriod.as_view()

    def test_get_current_year_and_period(self):
        request = self.factory.get('/year-period/')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('year/period', response.data)
        self.assertEqual(len(response.data['year/period']), 2)
