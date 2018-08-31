from flask import (current_app, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from . import info
from .. import db
from ..models import Course, CourseType
from .forms import CourseForm, ImportCourseForm, TermRangeForm


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
        return redirect(url_for('.courses', term=form.term.data,
                                type_id=form.type_id.data))
    form.term.data = request.args.get('term', 1, type=int)
    form.type_id.data = request.args.get(
        'type_id', CourseType.GENERAL, type=int)
    page = request.args.get('page', 1, type=int)
    courses_per_page = current_app.config['APP_COURSES_PER_PAGE']
    pagination = current_user.courses.order_by(Course.term.desc()).order_by(
        Course.type_id.asc()).paginate(page, per_page=courses_per_page, error_out=False)
    courses = pagination.items
    return render_template('/info/courses.html', form=form,
                           courses=courses, pagination=pagination)


@info.route('/edit-course/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    form = CourseForm()
    if form.validate_on_submit():
        course.name = form.name.data
        course.term = form.term.data
        course.type_id = form.type_id.data
        course.credit = form.credit.data
        course.score = form.score.data
        db.session.add(course)
        db.session.commit()
        flash('The course has been updated.')
        return redirect(url_for('.courses'))
    form.name.data = course.name
    form.term.data = course.term
    form.type_id.data = course.type_id
    form.credit.data = course.credit
    form.score.data = course.score
    return render_template('/info/edit_course.html', form=form)


@info.route('/delete-course/<int:id>', methods=['GET'])
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('.courses'))


@info.route('/delete-all-courses', methods=['GET'])
@login_required
def delete_all_courses():
    for course in current_user.courses.all():
        db.session.delete(course)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('.courses'))


@info.route('/import-course', methods=['GET', 'POST'])
@login_required
def import_courses():
    form = ImportCourseForm()
    if form.validate_on_submit():
        markup = request.files[form.file.name].read().decode('utf-8')
        for course in Course.fetch_courses(markup):
            course.term = form.term.data
            course.user = current_user._get_current_object()
            db.session.add(course)
        db.session.commit()
        return redirect(url_for('.courses'))
    return render_template('/info/import_courses.html', form=form)


@info.route('/import-courses-helper')
def import_courses_helper():
    return render_template('/info/import_courses_helper.html')


def get_statistics(user, terms):
    courses = user.courses.filter(Course.term.in_(terms)).all()
    return {
        '综合GPA': '%.3f' % Course.comprehensive_gpa(courses),
        '专业GPA': '%.3f' % Course.academic_gpa(courses),
        '保研GPA': '%.3f' % Course.postgraduate_recommandation_gpa(courses),
        '已完成经典阅读': '%d' % Course.reading_count(courses),
        '14通识学分': str(Course.general_course_credit(courses)),
        '总学分': str(Course.total_credit(courses))
    }


@info.route('/statistics', methods=['GET', 'POST'])
@login_required
def statistics():
    form = TermRangeForm()
    if form.validate_on_submit():
        return redirect(url_for('.statistics', term_from=form.term_from.data,
                                term_to=form.term_to.data))
    form.term_from.data = request.args.get('term_from', 1, type=int)
    form.term_to.data = request.args.get('term_to', 8, type=int)
    terms = list(range(form.term_from.data, form.term_to.data + 1))
    statistics = get_statistics(current_user, terms)
    return render_template('/info/statistics.html', form=form,
                           statistics=statistics)
