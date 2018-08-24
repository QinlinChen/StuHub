# StuHub

StuHub is a flask web application designed to store the students' course infomation
and show some statistic results such as GPA based on those infomation.
It now only supports the course infomation format for Nanjing University.
However, it is not difficult to be extended for more universities.

Besides, StuHub also provides a blog module for students to communicate
with each other. This module came from the book 
_Flask Web Development: Developing Web Applications with Python_.

## How to Setup
If you are willing to try this code, 
here are some steps for you to set it up for running.

1. You may as well configure a virtual python environment first by command 
   `virtualenv --no-site-package venv` and run the script `./venv/Script/active`
   according to your shell as to enter the virtual environment.

2. Use `pip install -r requirements.txt` to install dependencies for the project.
   
3. Config the following environment variables:

    * `FLASK_APP`: It is required by FLASK that indicates which module
the Flask app instance locates.
In this project, it is created in `stuhub.py`,
so you have to set `FLASK_APP` with the value `stuhub`. 

    * `FLASK_ENV`: It is required by FLASK
which is usually set as `developemnt` or `production`.
You can leran more from offical flask document.

    * `APP_CONFIG`: It indicates which set of configuration to uses.
It can be `development`, `production`, `heroku` and `unix`.
Learn more by reading `config.py`

    * `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME` and `MAIL_PASSWORD`:
They are used for server to send emails.

    * `SECRET_KEY`: A hard to guess string used to encrpty data.

    * `APP_ADMIN`: The administrator's email.
  
    * You can see other less important configurations in `config.py`

4. Use the command `flask deploy` to deploy database and `flask run` to run.

5. For unit tests, use `flask test` command.
