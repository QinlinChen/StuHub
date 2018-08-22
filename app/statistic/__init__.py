from flask import Blueprint

statistic = Blueprint('statistic', __name__)

from . import forms, views