from flask import (current_app, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from . import info
from .. import db
from ..models import Course
from .forms import CourseForm


@info.route('/courses', methods=['GET', 'POST'])
@login_required
def courses():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(name=form.name.data,
                        term=form.term.data,
                        type_id=form.type_id.data,
                        credit=form.credit.data,
                        score=form.score.data,
                        user=current_user._get_current_object())
        db.session.add(course)
        db.session.commit()
        form.name.data = ''
        form.credit.data = 0
        form.score.data = 0
    courses_per_page = current_app.config['APP_COURSES_PER_PAGE']
    page = request.args.get('page', 1, type=int)
    pagination = current_user.courses.order_by(Course.term.desc()).paginate(
        page, per_page=courses_per_page, error_out=False)
    courses = pagination.items
    return render_template('/info/courses.html', form=form,
                           courses=courses, pagination=pagination)


@info.route('/statistics', methods=['GET', 'POST'])
@login_required
def statistics():
    return render_template('/info/statistics.html')
