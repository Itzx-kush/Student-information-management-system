import re
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, abort
from routes import students_bp
from models import db, Student, CourseRegistration

EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
PHONE_REGEX = re.compile(r'^\+?[0-9\s\-]{7,15}$')

def validate_student_form(form, student_id=None):
    """Validate student form fields and check uniqueness constraints."""
    errors = []
    name = form.get('name', '').strip()
    roll_number = form.get('roll_number', '').strip().upper()
    email = form.get('email', '').strip().lower()
    phone = form.get('phone', '').strip()
    department = form.get('department', '').strip()
    year_of_study = form.get('year_of_study', '').strip()
    semester = form.get('semester', '').strip()
    gender = form.get('gender', '').strip()
    address = form.get('address', '').strip()
    admission_date = form.get('admission_date', '').strip()

    if not name or len(name) < 2:
        errors.append("Full Name is required and must be at least 2 characters long.")
    if not roll_number:
        errors.append("Roll Number is required.")
    if not email or not EMAIL_REGEX.match(email):
        errors.append("A valid Email Address is required.")
    if not phone or not PHONE_REGEX.match(phone):
        errors.append("A valid Phone Number is required (7 to 15 digits).")
    if not department:
        errors.append("Department is required.")
    if not year_of_study:
        errors.append("Year of Study is required.")
    if not semester:
        errors.append("Semester is required.")
    if not gender:
        errors.append("Gender is required.")
    if not admission_date:
        errors.append("Date of Admission is required.")

    # Check unique roll number
    query_roll = Student.query.filter_by(roll_number=roll_number)
    if student_id:
        query_roll = query_roll.filter(Student.id != student_id)
    if query_roll.first():
        errors.append(f"Roll Number '{roll_number}' is already registered with another student.")

    # Check unique email
    query_email = Student.query.filter_by(email=email)
    if student_id:
        query_email = query_email.filter(Student.id != student_id)
    if query_email.first():
        errors.append(f"Email '{email}' is already in use by another student.")

    cleaned_data = {
        'name': name,
        'roll_number': roll_number,
        'email': email,
        'phone': phone,
        'department': department,
        'year_of_study': year_of_study,
        'semester': semester,
        'gender': gender,
        'address': address,
        'admission_date': admission_date
    }
    return errors, cleaned_data


@students_bp.route('/')
def list_students():
    """Display all students with search and filter capabilities."""
    search_query = request.args.get('search', '').strip()
    dept_filter = request.args.get('department', '').strip()

    query = Student.query

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Student.name.ilike(search_term)) | (Student.roll_number.ilike(search_term))
        )

    if dept_filter:
        query = query.filter(Student.department == dept_filter)

    students = query.order_by(Student.roll_number.asc()).all()

    # Get distinct departments for filter dropdown
    departments = [d[0] for d in db.session.query(Student.department).distinct().order_by(Student.department).all() if d[0]]

    return render_template(
        'students/list.html',
        students=students,
        search_query=search_query,
        dept_filter=dept_filter,
        departments=departments,
        total_count=len(students)
    )


@students_bp.route('/add', methods=['GET', 'POST'])
def add_student():
    """Add a new student record."""
    if request.method == 'POST':
        errors, data = validate_student_form(request.form)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('students/add.html', form_data=request.form)

        try:
            student = Student(
                name=data['name'],
                roll_number=data['roll_number'],
                email=data['email'],
                phone=data['phone'],
                department=data['department'],
                year_of_study=data['year_of_study'],
                semester=data['semester'],
                gender=data['gender'],
                address=data['address'],
                admission_date=data['admission_date']
            )
            db.session.add(student)
            db.session.commit()
            flash(f"Student '{student.name}' (Roll No: {student.roll_number}) successfully added!", 'success')
            return redirect(url_for('students.view_student', student_id=student.id))
        except Exception as ex:
            db.session.rollback()
            flash(f"An error occurred while saving student: {str(ex)}", 'danger')
            return render_template('students/add.html', form_data=request.form)

    # Defaults for form
    default_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('students/add.html', form_data={'admission_date': default_date})


@students_bp.route('/<int:student_id>')
def view_student(student_id):
    """View detailed information about a single student and enrolled courses."""
    student = Student.query.get_or_404(student_id)
    registrations = CourseRegistration.query.filter_by(student_id=student.id).all()
    return render_template('students/details.html', student=student, registrations=registrations)


@students_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit existing student details."""
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        errors, data = validate_student_form(request.form, student_id=student.id)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('students/edit.html', student=student, form_data=request.form)

        try:
            student.name = data['name']
            student.roll_number = data['roll_number']
            student.email = data['email']
            student.phone = data['phone']
            student.department = data['department']
            student.year_of_study = data['year_of_study']
            student.semester = data['semester']
            student.gender = data['gender']
            student.address = data['address']
            student.admission_date = data['admission_date']

            db.session.commit()
            flash(f"Student details for '{student.name}' successfully updated!", 'success')
            return redirect(url_for('students.view_student', student_id=student.id))
        except Exception as ex:
            db.session.rollback()
            flash(f"An error occurred while updating student: {str(ex)}", 'danger')
            return render_template('students/edit.html', student=student, form_data=request.form)

    return render_template('students/edit.html', student=student, form_data=student.__dict__)


@students_bp.route('/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    """Delete a student record and restore seats for any active course registrations."""
    student = Student.query.get_or_404(student_id)
    student_name = student.name
    roll_num = student.roll_number

    try:
        # Restore available seats for active registrations before deletion
        for reg in student.registrations:
            if reg.status == 'Active' and reg.course:
                reg.course.available_seats = min(reg.course.max_seats, reg.course.available_seats + 1)

        db.session.delete(student)
        db.session.commit()
        flash(f"Student record '{student_name}' ({roll_num}) successfully deleted.", 'success')
    except Exception as ex:
        db.session.rollback()
        flash(f"Failed to delete student: {str(ex)}", 'danger')

    return redirect(url_for('students.list_students'))
