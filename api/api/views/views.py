from ..models import Discipline

from django.db.models.query import QuerySet

from rest_framework.decorators import APIView
from rest_framework import status, request, response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from utils.sessions import get_current_year_and_period, get_next_period
from utils.schedule_generator import ScheduleGenerator
from utils.db_handler import get_best_similarities_by_name, filter_disciplines_by_teacher, filter_disciplines_by_year_and_period, filter_disciplines_by_code
from utils.search import SearchTool

from .. import serializers
from api.swagger import Errors
from api.models import Discipline
from api.views.utils import handle_400_error

from traceback import print_exception

MAXIMUM_RETURNED_DISCIPLINES = 15
ERROR_MESSAGE = "no valid argument found for 'search', 'year' or 'period'"
MINIMUM_SEARCH_LENGTH = 4
ERROR_MESSAGE_SEARCH_LENGTH = f"search must have at least {MINIMUM_SEARCH_LENGTH} characters"
MAXIMUM_RETURNED_SCHEDULES = 5
