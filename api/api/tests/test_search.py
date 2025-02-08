# tests/test_search_view.py
from django.test import TestCase, RequestFactory
from api.views.search import Search
from api.models import Discipline
from api.serializers import DisciplineSerializer

class SearchViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = Search.as_view()
        self.discipline = Discipline.objects.create(
            unicode_name="Matemática",
            code="MAT101",
            year=2023,
            period=1
        )

    def test_search_by_name(self):
        request = self.factory.get('/search/?search=Matemática&year=2023&period=1')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['unicode_name'], "Matemática")

    def test_search_by_code(self):
        request = self.factory.get('/search/?search=MAT101&year=2023&period=1')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], "MAT101")
