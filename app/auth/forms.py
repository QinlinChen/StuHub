from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from wtforms import ValidationError

from ..models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[
                        DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[
        DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               '用户名只能由英文字母、数字、点、下划线组成')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码输入不一致')])
    password2 = PasswordField('再次输入密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册.')

    def validate_username(self, filed):
        if User.query.filter_by(username=filed.data).first():
            raise ValidationError('用户名已被使用')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('请输入原密码', validators=[DataRequired()])
    password = PasswordField('请输入新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码输入不一致')])
    password2 = PasswordField('再次输入新密码',
                              validators=[DataRequired()])
    submit = SubmitField('修改密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    password = PasswordField('请输入新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码输入不一致')])
    password2 = PasswordField('再次输入新密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')


class ChangeEmailForm(FlaskForm):
    password = PasswordField('请输入密码', validators=[DataRequired()])
    email = StringField('新邮箱', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    submit = SubmitField('修改邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')
