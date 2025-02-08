# api/views/search.py
from rest_framework.decorators import APIView
from rest_framework import status, request, response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.sessions import get_current_year_and_period, get_next_period
from utils.schedule_generator import ScheduleGenerator
from utils.db_handler import get_best_similarities_by_name, filter_disciplines_by_teacher, filter_disciplines_by_year_and_period, filter_disciplines_by_code
from utils.search import SearchTool
from api.models import Discipline
from api.serializers import DisciplineSerializer
from api.views.utils import handle_400_error

class Search(APIView):
    def treat_string(self, string: str | None) -> str | None:
        if string is not None:
            string = string.strip()
        return string

    def filter_disciplines(self, request: request.Request, name: str) -> QuerySet[Discipline]:
        search_handler = SearchTool(Discipline)
        search_fields = ['unicode_name', 'code']
        result = search_handler.filter_by_search_result(
            request=request,
            search_str=name,
            search_fields=search_fields
        )
        return result

    def retrieve_disciplines_by_similarity(self, request: request.Request, name: str) -> QuerySet[Discipline]:
        disciplines = self.filter_disciplines(request, name)
        disciplines = get_best_similarities_by_name(name, disciplines)

        if not disciplines.count():
            disciplines = filter_disciplines_by_code(code=name[0])
            for term in name[1:]:
                disciplines &= filter_disciplines_by_code(code=term)
            disciplines = filter_disciplines_by_code(name)

        return disciplines

    def get_disciplines_and_search_flag(self, request, name):
        disciplines = self.retrieve_disciplines_by_similarity(request, name)
        search_by_teacher = False
        if not disciplines.count():
            disciplines = filter_disciplines_by_teacher(name)
            search_by_teacher = True
        return disciplines, search_by_teacher

    def get_serialized_data(self, filter_params: dict, search_by_teacher: bool, name: str) -> list:
        filtered_disciplines = filter_disciplines_by_year_and_period(**filter_params)
        if search_by_teacher:
            data = serializers.DisciplineSerializer(filtered_disciplines, many=True, context={'teacher_name': name}).data
        else:
            data = serializers.DisciplineSerializer(filtered_disciplines, many=True).data
        return data

    def get_request_parameters(self, request):
        name = self.treat_string(request.GET.get('search', None))
        year = self.treat_string(request.GET.get('year', None))
        period = self.treat_string(request.GET.get('period', None))
        return name, year, period

    @swagger_auto_schema(
        operation_description="Busca disciplinas por nome ou código. O ano e período são obrigatórios.",
        security=[],
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Termo de pesquisa (Nome/Código)", type=openapi.TYPE_STRING),
            openapi.Parameter('year', openapi.IN_QUERY, description="Ano", type=openapi.TYPE_INTEGER),
            openapi.Parameter('period', openapi.IN_QUERY, description="Período", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response('OK', serializers.DisciplineSerializer),
            **Errors([400]).retrieve_erros()
        }
    )
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        name, year, period = self.get_request_parameters(request)

        if not all((name, year, period)):
            return handle_400_error(ERROR_MESSAGE)

        if len(name) < MINIMUM_SEARCH_LENGTH:
            return handle_400_error(ERROR_MESSAGE_SEARCH_LENGTH)

        disciplines, search_by_teacher = self.get_disciplines_and_search_flag(request, name)

        data = self.get_serialized_data(
            filter_params={'year': year, 'period': period, 'disciplines': disciplines},
            search_by_teacher=search_by_teacher,
            name=name
        )
        return response.Response(data[:MAXIMUM_RETURNED_DISCIPLINES], status.HTTP_200_OK)
