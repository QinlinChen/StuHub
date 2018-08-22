from flask import render_template

from . import statistic


@statistic.route('/index')
def index():
    return render_template('/statistic/index.html')
