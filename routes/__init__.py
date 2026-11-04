from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__)
students_bp = Blueprint('students', __name__, url_prefix='/students')
courses_bp = Blueprint('courses', __name__, url_prefix='/courses')
git_bp = Blueprint('git', __name__, url_prefix='/git')
practicals_bp = Blueprint('practicals', __name__, url_prefix='/practicals')

from routes import dashboard, students, courses, git_workflow, practicals
