import pytest
from app import create_app
from models import db, Student, Course, CourseRegistration
from services.git_service import GitService

@pytest.fixture
def app():
    """Create and configure a clean testing app instance with an in-memory database."""
    app_instance = create_app('testing')
    with app_instance.app_context():
        db.create_all()
        yield app_instance
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_dashboard_loads(client):
    """Test that the application starts successfully and the dashboard renders."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Week 8" in response.data
    assert b"Student Management" in response.data

def test_student_creation(client, app):
    """Test creating a new student record."""
    student_data = {
        'name': 'Test Student',
        'roll_number': 'TEST-001',
        'email': 'test.student@example.edu',
        'phone': '9876543210',
        'department': 'Computer Science',
        'year_of_study': '3rd Year',
        'semester': '5th Semester',
        'gender': 'Male',
        'address': 'Test Campus Hostel',
        'admission_date': '2024-08-01'
    }
    response = client.post('/students/add', data=student_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"TEST-001" in response.data
    assert b"Test Student" in response.data

    with app.app_context():
        student = Student.query.filter_by(roll_number='TEST-001').first()
        assert student is not None
        assert student.name == 'Test Student'
        assert student.email == 'test.student@example.edu'

def test_student_listing_and_search(client, app):
    """Test student listing and search query."""
    with app.app_context():
        s = Student(
            name='Kavya Sharma',
            roll_number='CS2026-999',
            email='kavya.s@example.edu',
            phone='9123456789',
            department='Computer Science',
            year_of_study='2nd Year',
            semester='3rd Semester',
            gender='Female',
            address='Bengaluru',
            admission_date='2025-08-01'
        )
        db.session.add(s)
        db.session.commit()

    # Search for Kavya
    response = client.get('/students/?search=Kavya')
    assert response.status_code == 200
    assert b"Kavya Sharma" in response.data
    assert b"CS2026-999" in response.data

    # Search by roll number
    response_roll = client.get('/students/?search=CS2026-999')
    assert response_roll.status_code == 200
    assert b"Kavya Sharma" in response_roll.data

def test_student_editing(client, app):
    """Test editing existing student information."""
    with app.app_context():
        s = Student(
            name='Original Name',
            roll_number='EDIT-001',
            email='original@example.edu',
            phone='9123456780',
            department='Computer Science',
            year_of_study='1st Year',
            semester='1st Semester',
            gender='Male',
            address='Hostel',
            admission_date='2026-08-01'
        )
        db.session.add(s)
        db.session.commit()
        s_id = s.id

    updated_data = {
        'name': 'Updated Name',
        'roll_number': 'EDIT-001',
        'email': 'updated@example.edu',
        'phone': '9123456780',
        'department': 'Information Technology',
        'year_of_study': '2nd Year',
        'semester': '3rd Semester',
        'gender': 'Male',
        'address': 'New Address',
        'admission_date': '2026-08-01'
    }
    response = client.post(f'/students/{s_id}/edit', data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Updated Name" in response.data

    with app.app_context():
        updated_student = db.session.get(Student, s_id)
        assert updated_student.name == 'Updated Name'
        assert updated_student.email == 'updated@example.edu'
        assert updated_student.department == 'Information Technology'

def test_student_deletion(client, app):
    """Test deleting a student record."""
    with app.app_context():
        s = Student(
            name='Delete Me',
            roll_number='DEL-001',
            email='del@example.edu',
            phone='9000000000',
            department='Mechanical',
            year_of_study='1st Year',
            semester='1st Semester',
            gender='Male',
            address='Address',
            admission_date='2026-08-01'
        )
        db.session.add(s)
        db.session.commit()
        s_id = s.id

    response = client.post(f'/students/{s_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b"successfully deleted" in response.data

    with app.app_context():
        assert db.session.get(Student, s_id) is None

def test_duplicate_student_records_rejected(client, app):
    """Test that duplicate roll numbers and emails are rejected."""
    with app.app_context():
        s = Student(
            name='Existing Student',
            roll_number='DUP-001',
            email='dup@example.edu',
            phone='9111111111',
            department='Computer Science',
            year_of_study='1st Year',
            semester='1st Semester',
            gender='Female',
            address='Campus',
            admission_date='2026-08-01'
        )
        db.session.add(s)
        db.session.commit()

    # Attempt to add student with same roll number
    dup_roll_data = {
        'name': 'Another Student',
        'roll_number': 'DUP-001',
        'email': 'another@example.edu',
        'phone': '9222222222',
        'department': 'Computer Science',
        'year_of_study': '1st Year',
        'semester': '1st Semester',
        'gender': 'Male',
        'address': 'Campus',
        'admission_date': '2026-08-01'
    }
    response_roll = client.post('/students/add', data=dup_roll_data, follow_redirects=True)
    assert b"Roll Number &#39;DUP-001&#39; is already registered" in response_roll.data or b"already registered" in response_roll.data

    # Attempt to add student with same email
    dup_email_data = {
        'name': 'Different Roll',
        'roll_number': 'DIFF-001',
        'email': 'dup@example.edu',
        'phone': '9333333333',
        'department': 'Computer Science',
        'year_of_study': '1st Year',
        'semester': '1st Semester',
        'gender': 'Male',
        'address': 'Campus',
        'admission_date': '2026-08-01'
    }
    response_email = client.post('/students/add', data=dup_email_data, follow_redirects=True)
    assert b"already in use" in response_email.data

def test_course_listing_and_creation(client, app):
    """Test course creation and listing."""
    course_data = {
        'course_code': 'TEST101',
        'course_name': 'Automated Testing with Pytest',
        'department': 'Computer Science',
        'instructor': 'Prof. Test Instructor',
        'credits': '3',
        'max_seats': '25',
        'description': 'Comprehensive unit and integration testing.'
    }
    response = client.post('/courses/add', data=course_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"TEST101" in response.data
    assert b"Automated Testing with Pytest" in response.data

    list_resp = client.get('/courses/')
    assert list_resp.status_code == 200
    assert b"TEST101" in list_resp.data

def test_course_registration_and_seat_decrement(client, app):
    """Test registering a student for a course and verifying available seats decrease."""
    with app.app_context():
        student = Student(
            name='Reg Student',
            roll_number='REG-001',
            email='reg@example.edu',
            phone='9444444444',
            department='Computer Science',
            year_of_study='2nd Year',
            semester='3rd Semester',
            gender='Female',
            address='Hostel',
            admission_date='2025-08-01'
        )
        course = Course(
            course_code='REG101',
            course_name='Registration Test Course',
            department='Computer Science',
            credits=3,
            max_seats=2,
            available_seats=2,
            instructor='Dr. Instructor'
        )
        db.session.add(student)
        db.session.add(course)
        db.session.commit()

        s_id = student.id
        c_id = course.id

    reg_data = {'student_id': s_id, 'course_id': c_id}
    response = client.post('/courses/register', data=reg_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    with app.app_context():
        updated_course = db.session.get(Course, c_id)
        assert updated_course.available_seats == 1
        reg = CourseRegistration.query.filter_by(student_id=s_id, course_id=c_id).first()
        assert reg is not None
        assert reg.status == 'Active'

def test_duplicate_course_registration_prevented(client, app):
    """Test that registering the same student twice for the same course is blocked."""
    with app.app_context():
        student = Student(
            name='Dup Reg Student',
            roll_number='DUPREG-001',
            email='dupreg@example.edu',
            phone='9555555555',
            department='Computer Science',
            year_of_study='1st Year',
            semester='1st Semester',
            gender='Male',
            address='City',
            admission_date='2026-08-01'
        )
        course = Course(
            course_code='DUPREG101',
            course_name='Duplicate Check Course',
            department='Computer Science',
            credits=3,
            max_seats=10,
            available_seats=10,
            instructor='Dr. Check'
        )
        db.session.add(student)
        db.session.add(course)
        db.session.commit()

        s_id = student.id
        c_id = course.id

    reg_data = {'student_id': s_id, 'course_id': c_id}
    # First registration
    client.post('/courses/register', data=reg_data, follow_redirects=True)

    # Second registration attempt
    resp2 = client.post('/courses/register', data=reg_data, follow_redirects=True)
    assert b"already actively enrolled" in resp2.data

def test_course_capacity_enforced(client, app):
    """Test that registration is blocked when available_seats == 0."""
    with app.app_context():
        s1 = Student(
            name='Student One',
            roll_number='FULL-001',
            email='s1@example.edu',
            phone='9666666661',
            department='Computer Science',
            year_of_study='1st Year',
            semester='1st Semester',
            gender='Male',
            address='City',
            admission_date='2026-08-01'
        )
        s2 = Student(
            name='Student Two',
            roll_number='FULL-002',
            email='s2@example.edu',
            phone='9666666662',
            department='Computer Science',
            year_of_study='1st Year',
            semester='1st Semester',
            gender='Female',
            address='City',
            admission_date='2026-08-01'
        )
        course = Course(
            course_code='FULL101',
            course_name='Single Seat Course',
            department='Computer Science',
            credits=3,
            max_seats=1,
            available_seats=1,
            instructor='Dr. Limit'
        )
        db.session.add_all([s1, s2, course])
        db.session.commit()

        s1_id = s1.id
        s2_id = s2.id
        c_id = course.id

    # S1 registers -> takes the 1 seat
    resp1 = client.post('/courses/register', data={'student_id': s1_id, 'course_id': c_id}, follow_redirects=True)
    assert b"Registration successful" in resp1.data

    # S2 tries to register -> should be rejected because course is full
    resp2 = client.post('/courses/register', data={'student_id': s2_id, 'course_id': c_id}, follow_redirects=True)
    assert b"full" in resp2.data.lower()

def test_registration_cancellation_restores_capacity(client, app):
    """Test that cancelling a registration restores the course available seats."""
    with app.app_context():
        s = Student(
            name='Cancel Student',
            roll_number='CAN-001',
            email='can@example.edu',
            phone='9777777777',
            department='Electronics',
            year_of_study='3rd Year',
            semester='5th Semester',
            gender='Male',
            address='City',
            admission_date='2024-08-01'
        )
        c = Course(
            course_code='CAN101',
            course_name='Cancellation Test Course',
            department='Electronics',
            credits=3,
            max_seats=5,
            available_seats=5,
            instructor='Prof. Cancel'
        )
        db.session.add_all([s, c])
        db.session.commit()

        s_id = s.id
        c_id = c.id

    # Register
    client.post('/courses/register', data={'student_id': s_id, 'course_id': c_id}, follow_redirects=True)

    with app.app_context():
        course_after_reg = db.session.get(Course, c_id)
        assert course_after_reg.available_seats == 4
        reg = CourseRegistration.query.filter_by(student_id=s_id, course_id=c_id).first()
        reg_id = reg.id

    # Cancel registration
    cancel_resp = client.post(f'/courses/registrations/{reg_id}/cancel', follow_redirects=True)
    assert cancel_resp.status_code == 200
    assert b"cancelled" in cancel_resp.data.lower() or b"restored" in cancel_resp.data.lower()

    with app.app_context():
        course_after_cancel = db.session.get(Course, c_id)
        assert course_after_cancel.available_seats == 5
        updated_reg = db.session.get(CourseRegistration, reg_id)
        assert updated_reg.status == 'Cancelled'

def test_git_tutorial_pages_load(client):
    """Test that all Git workflow and branch tutorial pages render correctly."""
    resp_branches = client.get('/git/branches')
    assert resp_branches.status_code == 200
    assert b"Git Branch Management" in resp_branches.data

    resp_workflow = client.get('/git/workflow')
    assert resp_workflow.status_code == 200
    assert b"Git &amp; GitHub Remote Workflow" in resp_workflow.data or b"Git & GitHub" in resp_workflow.data

    resp_collab = client.get('/git/collaboration')
    assert resp_collab.status_code == 200
    assert b"Collaborative Development" in resp_collab.data

def test_practicals_page_loads(client):
    """Test that the dedicated Week-8 Practical Demonstrations page renders."""
    response = client.get('/practicals/')
    assert response.status_code == 200
    assert b"Week-8 Practical Demonstrations" in response.data
    assert b"Practical Question A" in response.data
    assert b"Practical Question B" in response.data
    assert b"Practical Question C" in response.data

def test_about_page_loads(client):
    """Test that the About and Help page renders."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b"System Architecture" in response.data

def test_git_service_branch_validation():
    """Test GitService branch name validation and safety restrictions."""
    service = GitService()
    valid, _ = service.validate_branch_name("feature-new-course")
    assert valid is True

    valid_slash, _ = service.validate_branch_name("feature/student-v2")
    assert valid_slash is True

    # Invalid names
    inv_empty, _ = service.validate_branch_name("")
    assert inv_empty is False

    inv_dash, _ = service.validate_branch_name("-invalid-leading-dash")
    assert inv_dash is False

    inv_space, _ = service.validate_branch_name("branch with space")
    assert inv_space is False

    inv_dots, _ = service.validate_branch_name("branch..traversal")
    assert inv_dots is False
