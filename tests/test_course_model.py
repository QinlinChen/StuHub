import unittest

from app import create_app, db
from app.models import Course, User, CourseType


class CourseModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        db.session.add(Course(credit=1, score=90,
                              type_id=CourseType.GENERAL))
        db.session.add(Course(credit=2, score=75,
                              type_id=CourseType.GENERAL))
        db.session.add(Course(credit=1, score=80,
                              type_id=CourseType.PRO_BASIC))
        db.session.add(Course(credit=2, score=35,
                              type_id=CourseType.PRO_BASIC))
        db.session.add(Course(credit=1, score=90,
                              type_id=CourseType.PRO_OPTIONAL))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_statistics(self):
        courses = Course.query.all()
        comprehensive_gpa = Course.comprehensive_gpa(courses)
        self.assertTrue(abs(comprehensive_gpa - 3.428) < 1e-2)
        academic_gpa = Course.academic_gpa(courses)
        self.assertTrue(abs(academic_gpa - 3.0) < 1e-2)
        pg_rec_gpa = Course.postgraduate_recommandation_gpa(courses)
        self.assertTrue(abs(pg_rec_gpa - 2.5) < 1e-2)
        self.assertTrue(Course.total_credit(courses) == 7)
        self.assertTrue(Course.general_course_credit(courses) == 3)
        for i in range(0, 6):
            courses.append(Course(credit=0, type_id=CourseType.READING))
        self.assertTrue(Course.total_credit(courses) == 9)
        self.assertTrue(Course.general_course_credit(courses) == 5)