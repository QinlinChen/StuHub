from flask import (current_app, flash, make_response, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from . import statistic
from .. import db
from ..models import Course
from .forms import CourseForm


@statistic.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(name=form.name.data,
                        type_id=form.type_id.data,
                        credit=form.credit.data,
                        score=form.score.data,
                        user=current_user._get_current_object())
        db.session.add(course)
        db.session.commit()
        form = CourseForm()
        form.type_id.data = course.type_id
    show_statistic = bool(request.cookies.get('show_statistic', ''))
    statistic = None
    courses = None
    pagination = None
    if show_statistic:
        pass
    else:
        courses_per_page = current_app.config['APP_COURSES_PER_PAGE']
        page = request.args.get('page', 1, type=int)
        pagination = current_user.courses.paginate(
            page, per_page=courses_per_page, error_out=False)
        courses = pagination.items
    return render_template('/statistic/index.html', form=form,
                           show_statistic=show_statistic, statistic=statistic,
                           courses=courses, pagination=pagination)


@statistic.route('/show-courses')
@login_required
def show_courses():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_statistic', '', max_age=30*24*60*60)
    return resp


@statistic.route('/show-statistic')
@login_required
def show_statistic():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_statistic', '1', max_age=30*24*60*60)
    return resp
