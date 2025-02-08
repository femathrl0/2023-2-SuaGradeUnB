# api/views/generate_schedule.py
from rest_framework.decorators import APIView
from rest_framework import status, request, response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.schedule_generator import ScheduleGenerator
from api.serializers import ClassSerializerSchedule
from api.views.utils import handle_400_error

class GenerateSchedule(APIView):
    @swagger_auto_schema(
        operation_description="Gera possíveis horários de acordo com as aulas escolhidas com preferência de turno",
        security=[],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="body",
            required=['classes'],
            properties={
                'classes': openapi.Schema(
                    description="Lista de ids de aulas escolhidas",
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        description="Id da aula",
                        type=openapi.TYPE_INTEGER
                    )
                ),
                'preference': openapi.Schema(
                    description="Lista de preferências (manhã, tarde, noite)",
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        description="Define o peso de cada turno",
                        type=openapi.TYPE_INTEGER,
                        enum=[1, 2, 3]
                    )
                )
            }
        ),
        responses={
            200: serializers.GenerateSchedulesSerializer(many=True),
            **Errors([400]).retrieve_erros()
        }
    )
    def post(self, request: request.Request, *args, **kwargs) -> response.Response:
        """
        View para gerar horários.
        Funcionamento: Recebe uma lista de ids de classes e uma lista de preferências
        e verifica se as classes e preferências são válidas.
        Caso sejam válidas, gera os horários e retorna uma lista de horários.
        """

        classes_id = request.data.get('classes', None)
        preference = request.data.get('preference', None)
        preference_valid = preference is not None and isinstance(preference, list) and all(
            isinstance(x, int) for x in preference) and len(preference) == 3
        classes_valid = classes_id is not None and isinstance(
            classes_id, list) and all(isinstance(x, int) for x in classes_id) and len(classes_id) > 0

        if preference is not None and not preference_valid:
            """Retorna um erro caso a preferência não seja uma lista de 3 inteiros"""
            return response.Response(
                {
                    "errors": "preference must be a list of 3 integers"
                }, status.HTTP_400_BAD_REQUEST)

        if not classes_valid:
            """Retorna um erro caso a lista de ids de classes não seja enviada"""
            return response.Response(
                {
                    "errors": "classes is required and must be a list of integers with at least one element"
                }, status.HTTP_400_BAD_REQUEST)

        try:
            schedule_generator = ScheduleGenerator(classes_id, preference)
            generated_data = schedule_generator.generate()
        except Exception as error:
            """Retorna um erro caso ocorra algum erro ao criar o gerador de horários"""

            message_error = "An internal error has occurred."

            if type(error) is ValueError:
                message_error = str(error)
            else:  # pragma: no cover
                print_exception(error)

            return response.Response(
                {
                    "errors": message_error
                }, status.HTTP_400_BAD_REQUEST)

        schedules = generated_data.get("schedules", [])
        message = generated_data.get("message", "")
        data = []

        for schedule in schedules[:MAXIMUM_RETURNED_SCHEDULES]:
            data.append(
                list(map(lambda x: serializers.ClassSerializerSchedule(x).data, schedule)))
        
        return response.Response({
            'message': message,
            'schedules': data
        }, status.HTTP_200_OK)
