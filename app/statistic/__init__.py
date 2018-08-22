from flask import Blueprint

statistic = Blueprint('statistic', __name__)

from . import forms, views
from ..models import course_type_name


@statistic.app_context_processor
def inject_course_type():
    return dict(course_type_name=course_type_name)
