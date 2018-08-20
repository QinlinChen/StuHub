import os

from flask_migrate import Migrate

from app import create_app, db
from app.models import Comment, Follow, Permission, Post, Role, User

app = create_app(os.getenv('APP_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.context_processor
def inject_app_name():
    return dict(app_name=app.config['APP_NAME'])


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission,
                Post=Post, Comment=Comment)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
