from utils.db_handler import filter_disciplines_by_name, filter_disciplines_by_code, filter_disciplines_by_year_and_period
from rest_framework.decorators import APIView
from .serializers import DisciplineSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

MAXIMUM_RETURNED_DISCIPLINES = 5

class Search(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        name = request.GET.get('search', None)
        year = request.GET.get('year', None)
        period = request.GET.get('period', None)
        
        if name is None or year is None or period is None:
            return Response(
                {
                    "errors": "no valid argument found for 'search', 'year' or 'period'"
                }, status.HTTP_400_BAD_REQUEST)

        disciplines = filter_disciplines_by_name(name=name) | filter_disciplines_by_code(code=name)
        filtered_disciplines = filter_disciplines_by_year_and_period(year=year, period=period, disciplines=disciplines)
        data = DisciplineSerializer(filtered_disciplines, many=True).data

        return Response(data[:MAXIMUM_RETURNED_DISCIPLINES], status.HTTP_200_OK)
    