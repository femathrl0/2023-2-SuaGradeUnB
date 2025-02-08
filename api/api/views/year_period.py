# api/views/year_period.py
from rest_framework.decorators import APIView
from rest_framework import status, request, response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.sessions import get_current_year_and_period, get_next_period

class YearPeriod(APIView):
    @swagger_auto_schema(
        operation_description="Retorna o ano e período atual, e o próximo ano e período letivos válidos para pesquisa.",
        security=[],
        responses={
            200: openapi.Response('OK', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'year/period': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_STRING
                        )
                    )
                }
            ), examples={
                'application/json': {
                    'year/period': ['2020/1', '2020/2']
                }
            })
        }
    )
    def get(self, request: request.Request, *args, **kwargs) -> response.Response:
        year, period = get_current_year_and_period()
        next_year, next_period = get_next_period()

        data = {
            'year/period': [f'{year}/{period}', f'{next_year}/{next_period}'],
        }

        return response.Response(data, status.HTTP_200_OK)
