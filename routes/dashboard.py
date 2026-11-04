from flask import render_template
from routes import dashboard_bp
from models import Student, Course, CourseRegistration

@dashboard_bp.route('/')
def index():
    """Landing dashboard with metrics, recent activity, and quick access."""
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_registrations = CourseRegistration.query.filter_by(status='Active').count()
    available_courses_count = Course.query.filter(Course.available_seats > 0).count()

    recent_registrations = CourseRegistration.query.order_by(
        CourseRegistration.registration_date.desc()
    ).limit(6).all()

    recent_students = Student.query.order_by(
        Student.id.desc()
    ).limit(5).all()

    return render_template(
        'dashboard.html',
        total_students=total_students,
        total_courses=total_courses,
        total_registrations=total_registrations,
        available_courses_count=available_courses_count,
        recent_registrations=recent_registrations,
        recent_students=recent_students
    )

@dashboard_bp.route('/about')
def about():
    """About the application, Git concepts, and technical guide."""
    return render_template('about.html')
