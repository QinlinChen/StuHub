from flask import current_app, flash, redirect, render_template, url_for
from flask_sqlalchemy import get_debug_queries

from . import main
from ..email import send_email
from .forms import FeedbackForm


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        body = form.body.data
        send_email(current_app.config['APP_ADMIN'],
                   'Feedback', 'mail/feedback', body=body)
        flash('反馈成功')
        return redirect(url_for('.index'))
    return render_template('feedback.html', form=form)


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['APP_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response
