from flask_wtf import FlaskForm
from wtforms import (FloatField, IntegerField, SelectField, StringField,
                     SubmitField)
from wtforms.validators import DataRequired, NumberRange, InputRequired

from ..models import course_type_name


class CourseForm(FlaskForm):
    name = StringField("Course name", validators=[DataRequired()])
    type_id = SelectField('Course type', coerce=int, choices=[
                          (index, lable) for index, lable in course_type_name.items()])
    credit = IntegerField("Credit", validators=[
                          InputRequired(), NumberRange(0, 150)])
    score = FloatField("Score", validators=[
                       InputRequired(), NumberRange(0.0, 100.0)])
    submit = SubmitField('Submit')
