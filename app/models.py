import hashlib
from datetime import datetime

import bleach
from bs4 import BeautifulSoup
from flask import current_app, request
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    courses = db.relationship('Course', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['APP_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = User.generate_avatar_hash(self.email)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @staticmethod
    def generate_avatar_hash(email):
        return hashlib.md5(email.lower().encode('utf-8')).hexdigest()

    @staticmethod
    def on_changed_email(target, value, oldvalue, initiator):
        target.avatar_hash = User.generate_avatar_hash(value)

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or User.generate_avatar_hash(self.email)
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def __repr__(self):
        return '<User %r>' % self.username


db.event.listen(User.email, 'set', User.on_changed_email)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class CourseType:
    GENERAL = 1
    READING = 2
    PUBLIC_OPTIONAL = 3
    PUBLIC_BASIC = 4
    PUBLIC_BASIC_MATHS_PHYSICS = 5
    PRO_BASIC = 6
    PRO_CORE = 7
    PRO_OPTIONAL = 8

    @staticmethod
    def academic_type():
        return (
            CourseType.PUBLIC_BASIC_MATHS_PHYSICS,
            CourseType.PRO_BASIC,
            CourseType.PRO_CORE,
            CourseType.PRO_OPTIONAL
        )

    @staticmethod
    def postgraduate_recommandation_type():
        return (
            CourseType.PUBLIC_BASIC_MATHS_PHYSICS,
            CourseType.PRO_BASIC,
            CourseType.PRO_CORE
        )


course_type_name = {
    CourseType.GENERAL: '通识',
    CourseType.READING: '经典阅读',
    CourseType.PUBLIC_OPTIONAL: '公选',
    CourseType.PUBLIC_BASIC: '通修',
    CourseType.PUBLIC_BASIC_MATHS_PHYSICS: '数理通修',
    CourseType.PRO_BASIC: '专业平台',
    CourseType.PRO_CORE: '专业核心',
    CourseType.PRO_OPTIONAL: '专业选修'
}


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    type_id = db.Column(db.Integer, index=True)
    credit = db.Column(db.Integer)
    score = db.Column(db.Float)
    term = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def average_weighted_score_on_credit(courses):
        sum_score = 0.0
        sum_credit = 0
        for course in courses:
            sum_score += course.score * course.credit
            sum_credit += course.credit
        if sum_credit == 0:
            return 0
        return sum_score / sum_credit

    @staticmethod
    def comprehensive_gpa(courses):
        return Course.average_weighted_score_on_credit(courses) / 20

    @staticmethod
    def academic_gpa(courses):
        academic_courses = [course for course in courses
                            if course.type_id in CourseType.academic_type()]
        return Course.average_weighted_score_on_credit(academic_courses) / 20

    @staticmethod
    def postgraduate_recommandation_gpa(courses):
        pgr_courses = [course for course in courses
                       if course.type_id in CourseType.postgraduate_recommandation_type()]
        return Course.average_weighted_score_on_credit(pgr_courses) / 20

    @staticmethod
    def have_fullfilled_reading_requirement(courses):
        reading_courses = [course for course in courses
                           if course.type_id == CourseType.READING]
        return len(reading_courses) >= 6

    @staticmethod
    def get_reading_credit(courses):
        if Course.have_fullfilled_reading_requirement(courses):
            return 2
        return 0

    @staticmethod
    def total_credit(courses):
        return sum([course.credit for course in courses]) + \
            Course.get_reading_credit(courses)

    @staticmethod
    def general_course_credit(courses):
        return sum([course.credit for course in courses
                    if course.type_id == CourseType.GENERAL]) +\
            Course.get_reading_credit(courses)

    def guess_type_id(self, type_name):
        if type_name == '通识':
            return CourseType.GENERAL
        if type_name == '通修':
            return CourseType.PUBLIC_BASIC
        if type_name == '平台':
            return CourseType.PRO_BASIC
        if type_name == '核心':
            return CourseType.PRO_CORE
        if type_name == '选修':
            return CourseType.GENERAL

    @staticmethod
    def parse_courses(markup):
        soup = BeautifulSoup(markup, features='lxml')
        courses = []
        for tr in soup.select('table table:nth-of-type(2) tr')[1:]:
            tds = tr.find_all('td')
            course = Course(name=tds[2].get_text().strip(),
                            credit=int(tds[5].get_text().strip()),
                            score=float(tds[6].get_text().strip()))
            type_name = tds[4].get_text().strip()
            course.type_id = course.guess_type_id(type_name)
            courses.append(course)
        return courses
