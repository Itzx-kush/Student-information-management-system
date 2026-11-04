from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash, abort
from routes import courses_bp
from models import db, Course, Student, CourseRegistration

@courses_bp.route('/')
def list_courses():
    """Display all courses with seat availability, department filter, and search."""
    search_query = request.args.get('search', '').strip()
    dept_filter = request.args.get('department', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Course.query

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Course.course_name.ilike(search_term)) |
            (Course.course_code.ilike(search_term)) |
            (Course.instructor.ilike(search_term))
        )

    if dept_filter:
        query = query.filter(Course.department == dept_filter)

    if status_filter == 'available':
        query = query.filter(Course.available_seats > 0)
    elif status_filter == 'full':
        query = query.filter(Course.available_seats <= 0)

    courses = query.order_by(Course.course_code.asc()).all()
    departments = [d[0] for d in db.session.query(Course.department).distinct().order_by(Course.department).all() if d[0]]

    return render_template(
        'courses/list.html',
        courses=courses,
        search_query=search_query,
        dept_filter=dept_filter,
        status_filter=status_filter,
        departments=departments,
        total_courses=len(courses)
    )


@courses_bp.route('/add', methods=['GET', 'POST'])
def add_course():
    """Add a new course to the catalog."""
    if request.method == 'POST':
        code = request.form.get('course_code', '').strip().upper()
        name = request.form.get('course_name', '').strip()
        description = request.form.get('description', '').strip()
        department = request.form.get('department', '').strip()
        credits_raw = request.form.get('credits', '3').strip()
        max_seats_raw = request.form.get('max_seats', '40').strip()
        instructor = request.form.get('instructor', '').strip()

        errors = []
        if not code:
            errors.append("Course Code is required.")
        if not name:
            errors.append("Course Name is required.")
        if not department:
            errors.append("Department is required.")
        if not instructor:
            errors.append("Instructor Name is required.")

        try:
            credits = int(credits_raw)
            if credits < 1 or credits > 10:
                errors.append("Credits must be an integer between 1 and 10.")
        except ValueError:
            errors.append("Credits must be a valid number.")

        try:
            max_seats = int(max_seats_raw)
            if max_seats < 1 or max_seats > 500:
                errors.append("Maximum seats must be between 1 and 500.")
        except ValueError:
            errors.append("Maximum seats must be a valid number.")

        # Check unique course code
        if Course.query.filter_by(course_code=code).first():
            errors.append(f"A course with code '{code}' already exists.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('courses/add.html', form_data=request.form)

        try:
            course = Course(
                course_code=code,
                course_name=name,
                description=description,
                department=department,
                credits=credits,
                max_seats=max_seats,
                available_seats=max_seats,
                instructor=instructor
            )
            db.session.add(course)
            db.session.commit()
            flash(f"Course '{course.course_code} - {course.course_name}' created successfully!", 'success')
            return redirect(url_for('courses.view_course', course_id=course.id))
        except Exception as ex:
            db.session.rollback()
            flash(f"Failed to create course: {str(ex)}", 'danger')
            return render_template('courses/add.html', form_data=request.form)

    return render_template('courses/add.html', form_data={})


@courses_bp.route('/<int:course_id>')
def view_course(course_id):
    """View course details and roster of enrolled students."""
    course = Course.query.get_or_404(course_id)
    active_registrations = CourseRegistration.query.filter_by(
        course_id=course.id, status='Active'
    ).join(Student).order_by(Student.roll_number.asc()).all()

    cancelled_registrations = CourseRegistration.query.filter_by(
        course_id=course.id, status='Cancelled'
    ).join(Student).order_by(CourseRegistration.registration_date.desc()).all()

    all_students = Student.query.order_by(Student.name.asc()).all()

    return render_template(
        'courses/details.html',
        course=course,
        active_registrations=active_registrations,
        cancelled_registrations=cancelled_registrations,
        all_students=all_students
    )


@courses_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a student for a course with transactional seat checking and allocation."""
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        course_id = request.form.get('course_id', type=int)

        if not student_id or not course_id:
            flash("Please select both a student and a course.", 'danger')
            return redirect(url_for('courses.register', student_id=student_id, course_id=course_id))

        student = db.session.get(Student, student_id)
        if not student:
            flash("Selected student does not exist.", 'danger')
            return redirect(url_for('courses.register'))

        course = db.session.get(Course, course_id)
        if not course:
            flash("Selected course does not exist.", 'danger')
            return redirect(url_for('courses.register'))

        # Check existing registration
        existing_reg = CourseRegistration.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).first()

        if existing_reg and existing_reg.status == 'Active':
            flash(f"Student '{student.name}' is already actively enrolled in '{course.course_code} - {course.course_name}'.", 'warning')
            return redirect(url_for('courses.view_course', course_id=course.id))

        # Check seat availability
        if course.available_seats <= 0:
            flash(f"Cannot register: Course '{course.course_code}' is full (0 available seats).", 'danger')
            return redirect(url_for('courses.register', student_id=student.id, course_id=course.id))

        # Transactional registration and seat decrement
        try:
            now_utc = datetime.now(timezone.utc)
            if existing_reg and existing_reg.status == 'Cancelled':
                # Re-activate previous cancelled registration
                existing_reg.status = 'Active'
                existing_reg.registration_date = now_utc
            else:
                new_reg = CourseRegistration(
                    student_id=student.id,
                    course_id=course.id,
                    status='Active',
                    registration_date=now_utc
                )
                db.session.add(new_reg)

            # Decrement seats
            course.available_seats -= 1
            db.session.commit()

            flash(f"Registration successful! {student.name} is now enrolled in {course.course_code} ({course.course_name}).", 'success')
            return redirect(url_for('courses.view_course', course_id=course.id))

        except Exception as ex:
            db.session.rollback()
            flash(f"Registration failed due to a database error: {str(ex)}", 'danger')
            return redirect(url_for('courses.register', student_id=student_id, course_id=course_id))

    # GET request - show registration form
    preselected_student_id = request.args.get('student_id', type=int)
    preselected_course_id = request.args.get('course_id', type=int)

    students = Student.query.order_by(Student.name.asc()).all()
    courses = Course.query.order_by(Course.course_code.asc()).all()

    return render_template(
        'courses/register.html',
        students=students,
        courses=courses,
        selected_student_id=preselected_student_id,
        selected_course_id=preselected_course_id
    )


@courses_bp.route('/registrations')
def list_registrations():
    """View all course registrations in the system."""
    status_filter = request.args.get('status', '').strip()
    course_filter = request.args.get('course_id', type=int)
    student_filter = request.args.get('student_id', type=int)

    query = CourseRegistration.query.join(Student).join(Course)

    if status_filter:
        query = query.filter(CourseRegistration.status == status_filter)

    if course_filter:
        query = query.filter(CourseRegistration.course_id == course_filter)

    if student_filter:
        query = query.filter(CourseRegistration.student_id == student_filter)

    registrations = query.order_by(CourseRegistration.registration_date.desc()).all()
    courses = Course.query.order_by(Course.course_code.asc()).all()

    return render_template(
        'courses/registrations.html',
        registrations=registrations,
        courses=courses,
        status_filter=status_filter,
        course_filter=course_filter,
        student_filter=student_filter
    )


@courses_bp.route('/registrations/<int:reg_id>/cancel', methods=['POST'])
def cancel_registration(reg_id):
    """Cancel an active course registration and restore available seats."""
    registration = CourseRegistration.query.get_or_404(reg_id)

    if registration.status == 'Cancelled':
        flash("This registration is already cancelled.", 'info')
        return redirect(request.referrer or url_for('courses.list_registrations'))

    try:
        registration.status = 'Cancelled'
        course = registration.course
        if course:
            course.available_seats = min(course.max_seats, course.available_seats + 1)

        db.session.commit()
        student_name = registration.student.name if registration.student else 'Student'
        course_code = course.course_code if course else 'Course'
        flash(f"Registration for {student_name} in {course_code} has been cancelled. Seat capacity restored.", 'success')

    except Exception as ex:
        db.session.rollback()
        flash(f"Failed to cancel registration: {str(ex)}", 'danger')

    return redirect(request.referrer or url_for('courses.list_registrations'))
