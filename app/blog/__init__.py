from flask import Blueprint

blog = Blueprint('blog', __name__)

from . import views
from ..models import Permission


@blog.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
