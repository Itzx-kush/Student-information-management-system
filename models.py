from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_utc_now():
    return datetime.now(timezone.utc)

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    year_of_study = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=True)
    admission_date = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    registrations = db.relationship('CourseRegistration', backref='student', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Student {self.roll_number}: {self.name}>'

    def active_registrations_count(self):
        return sum(1 for reg in self.registrations if reg.status == 'Active')


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    course_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    department = db.Column(db.String(50), nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=3)
    max_seats = db.Column(db.Integer, nullable=False, default=40)
    available_seats = db.Column(db.Integer, nullable=False, default=40)
    instructor = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    registrations = db.relationship('CourseRegistration', backref='course', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Course {self.course_code}: {self.course_name}>'

    def is_full(self):
        return self.available_seats <= 0

    def enrolled_count(self):
        return self.max_seats - self.available_seats


class CourseRegistration(db.Model):
    __tablename__ = 'course_registrations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    registration_date = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)  # 'Active', 'Cancelled'

    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='uq_student_course_registration'),
    )

    def __repr__(self):
        return f'<Registration Student:{self.student_id} Course:{self.course_id} Status:{self.status}>'


def seed_initial_data(db_instance):
    """
    Inserts sample data only when relevant tables are empty.
    Never overwrites or deletes existing user data.
    """
    # Check if courses table is empty
    if Course.query.first() is None:
        sample_courses = [
            Course(
                course_code="CS101",
                course_name="Data Structures & Algorithms",
                description="Fundamental abstract data types, sorting algorithms, trees, and graph algorithms.",
                department="Computer Science",
                credits=4,
                max_seats=40,
                available_seats=39,
                instructor="Dr. Ramesh Sharma"
            ),
            Course(
                course_code="CS102",
                course_name="Database Management Systems",
                description="Relational database design, SQL querying, normalization, indexing, and ACID transactions.",
                department="Computer Science",
                credits=4,
                max_seats=35,
                available_seats=34,
                instructor="Prof. Ananya Sen"
            ),
            Course(
                course_code="CS103",
                course_name="Web Applications with Flask",
                description="Building full-stack web applications using Python Flask, Jinja2, REST APIs, and SQLite.",
                department="Information Technology",
                credits=3,
                max_seats=30,
                available_seats=29,
                instructor="Dr. Arvind Varma"
            ),
            Course(
                course_code="CS104",
                course_name="Software Engineering & Version Control",
                description="Agile principles, Git branch management, GitHub collaboration, PR reviews, and CI/CD.",
                department="Computer Science",
                credits=3,
                max_seats=45,
                available_seats=44,
                instructor="Prof. Neha Gupta"
            ),
            Course(
                course_code="CS105",
                course_name="Artificial Intelligence & Machine Learning",
                description="Introduction to supervised and unsupervised learning, neural networks, and model evaluation.",
                department="Artificial Intelligence",
                credits=4,
                max_seats=30,
                available_seats=30,
                instructor="Dr. Vikram Rao"
            ),
            Course(
                course_code="EC201",
                course_name="Digital Signal Processing",
                description="Discrete-time signals, Z-transforms, discrete Fourier transform (DFT), and filter design.",
                department="Electronics",
                credits=3,
                max_seats=30,
                available_seats=30,
                instructor="Prof. Kavita Pillai"
            )
        ]
        db_instance.session.add_all(sample_courses)
        db_instance.session.commit()

    # Check if students table is empty
    if Student.query.first() is None:
        sample_students = [
            Student(
                name="Aarav Sharma",
                roll_number="CS2026-001",
                email="aarav.sharma@example.edu",
                phone="9876543210",
                department="Computer Science",
                year_of_study="3rd Year",
                semester="5th Semester",
                gender="Male",
                address="Flat 402, Green Valley Apartments, Tech Park Road, Bengaluru",
                admission_date="2024-08-10"
            ),
            Student(
                name="Priya Patel",
                roll_number="IT2026-015",
                email="priya.patel@example.edu",
                phone="9812345678",
                department="Information Technology",
                year_of_study="2nd Year",
                semester="3rd Semester",
                gender="Female",
                address="B-12, Nilgiri Heights, MG Road, Pune",
                admission_date="2025-08-12"
            ),
            Student(
                name="Rohan Nair",
                roll_number="AI2026-008",
                email="rohan.nair@example.edu",
                phone="9745612389",
                department="Artificial Intelligence",
                year_of_study="1st Year",
                semester="1st Semester",
                gender="Male",
                address="15/2, Sunrise Residency, Jubilee Hills, Hyderabad",
                admission_date="2026-08-01"
            )
        ]
        db_instance.session.add_all(sample_students)
        db_instance.session.commit()

        # Add initial sample registrations to match course seat counts
        s1 = Student.query.filter_by(roll_number="CS2026-001").first()
        s2 = Student.query.filter_by(roll_number="IT2026-015").first()
        c1 = Course.query.filter_by(course_code="CS101").first()
        c2 = Course.query.filter_by(course_code="CS102").first()
        c3 = Course.query.filter_by(course_code="CS103").first()
        c4 = Course.query.filter_by(course_code="CS104").first()

        sample_regs = []
        if s1 and c1:
            sample_regs.append(CourseRegistration(student_id=s1.id, course_id=c1.id, status='Active'))
        if s1 and c4:
            sample_regs.append(CourseRegistration(student_id=s1.id, course_id=c4.id, status='Active'))
        if s2 and c2:
            sample_regs.append(CourseRegistration(student_id=s2.id, course_id=c2.id, status='Active'))
        if s2 and c3:
            sample_regs.append(CourseRegistration(student_id=s2.id, course_id=c3.id, status='Active'))

        if sample_regs:
            db_instance.session.add_all(sample_regs)
            db_instance.session.commit()
