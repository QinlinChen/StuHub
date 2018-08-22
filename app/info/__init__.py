from flask import Blueprint

info = Blueprint('info', __name__)

from . import forms, views
from ..models import course_type_name


@info.app_context_processor
def inject_course_type():
    return dict(course_type_name=course_type_name)
