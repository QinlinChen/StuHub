from flask_wtf import FlaskForm
from wtforms import (FloatField, IntegerField, SelectField, StringField,
                     SubmitField)
from wtforms.validators import (DataRequired, InputRequired, NumberRange,
                                ValidationError)

from ..models import course_type_name


class CourseForm(FlaskForm):
    name = StringField("Course name", validators=[DataRequired()])
    term = SelectField('Term', coerce=int, choices=[
                       (index, '第%d学期' % index) for index in range(1, 9)])
    type_id = SelectField('Course type', coerce=int, choices=[
                          (index, lable) for index, lable in course_type_name.items()])
    credit = IntegerField("Credit", validators=[
                          InputRequired(), NumberRange(0, 150)])
    score = FloatField("Score", validators=[
                       InputRequired(), NumberRange(0.0, 100.0)])
    submit = SubmitField('Submit')


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
    term_from = SelectField('Term from', validators=[LessEqualTo('term_to')],
                            coerce=int, choices=[
                            (index, '第%d学期' % index) for index in range(1, 9)])
    term_to = SelectField('Term to', coerce=int, choices=[
                          (index, '第%d学期' % index) for index in range(1, 9)])
    submit = SubmitField('Submit')
