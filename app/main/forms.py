from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class FeedbackForm(FlaskForm):
    body = TextAreaField('吐槽一下吧', validators=[DataRequired()])
    submit = SubmitField('提交')
