import os

from flask_wtf import FlaskForm
from wtforms import (FileField, FloatField, IntegerField, SelectField,
                     StringField, SubmitField)
from wtforms.validators import (DataRequired, InputRequired, NumberRange,
                                Regexp, ValidationError)

from ..models import course_type_name


class CourseForm(FlaskForm):
    name = StringField("课程名称", validators=[DataRequired()])
    term = SelectField('学期', coerce=int, choices=[
                       (index, '第%d学期' % index) for index in range(1, 9)])
    type_id = SelectField('课程类型', coerce=int, choices=[
                          (index, lable) for index, lable in course_type_name.items()])
    credit = IntegerField("学分", validators=[
                          InputRequired(), NumberRange(0, 150)])
    score = FloatField("成绩", validators=[
                       InputRequired(), NumberRange(0.0, 100.0)])
    submit = SubmitField('提交')


class LessEqualTo(object):

    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext(
                "Invalid field name '%s'.") % self.fieldname)
        if field.data > other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            message = self.message
            if message is None:
                message = field.gettext(
                    'Field must be less or equal to %(other_name)s.')

            raise ValidationError(message % d)


class TermRangeForm(FlaskForm):
    term_from = SelectField('开始学期', validators=[LessEqualTo('term_to')],
                            coerce=int, choices=[
                            (index, '第%d学期' % index) for index in range(1, 9)])
    term_to = SelectField('结束学期', coerce=int, choices=[
                          (index, '第%d学期' % index) for index in range(1, 9)])
    submit = SubmitField('提交')


class ImportCourseForm(FlaskForm):
    term = SelectField('学期', coerce=int, choices=[
                       (index, '第%d学期' % index) for index in range(1, 9)])
    file = FileField('文件', validators=[DataRequired()])
    SubmitField = SubmitField('提交')

    def validate_file(self, field):
        if os.path.splitext(field.data.filename)[-1] != '.html':
            raise ValidationError('You should upload html file.')
