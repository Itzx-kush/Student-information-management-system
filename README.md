# Week 8 — Student Management & Git Workflow Lab

[![Flask](https://img.shields.io/badge/Flask-3.1.3-blue.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://sqlite.org/)
[![Tests](https://img.shields.io/badge/Pytest-15%20Passed-brightgreen.svg)](https://pytest.org/)
[![Git](https://img.shields.io/badge/VCS-Git%20%26%20GitHub-F05032.svg)](https://git-scm.com/)
[![License](https://img.shields.io/badge/License-Academic%20Lab-indigo.svg)](#)

A complete, polished, responsive Flask web application combining all three **Week 8** practical examination questions into a single unified academic platform.

- **GitHub Repository:** [https://github.com/Itzx-kush/Student-information-management-system](https://github.com/Itzx-kush/Student-information-management-system)
- **Repository Owner:** `Itzx-kush`
- **Default Branch:** `main`
- **Feature Branch:** `feature/week-8-flask-student-git-system`

---

## 1. Week-8 Practical Mapping

All three Week-8 practical questions are implemented in this single application:

| Question | Practical Title | Key Capabilities Implemented | Application Route |
| :--- | :--- | :--- | :--- |
| **Question A** | **Student Information Management System with Git Branch Management** | Complete Student CRUD operations; Git branch creation, branch switching, merging, and safe branch deletion (`git branch -d`). | `/students`<br>`/git/branches` |
| **Question B** | **Student Information Management System with Git & GitHub Workflow** | End-to-end Git & GitHub remote workflow: remote cloning, file modification, status checks, staging (`git add`), commits, remote tracking, and bidirectional push/pull operations. | `/students`<br>`/git/workflow` |
| **Question C** | **Online Student Course Registration System with Complete Git Workflow** | Transactional course enrollment, dynamic seat decrementation and restoration upon drop, duplicate prevention; collaborative Git (multi-developer branches, pull requests, merge conflict resolution). | `/courses`<br>`/git/collaboration` |

---

## 2. Technology Stack

- **Backend:** Python 3 (Tested with Python 3.10 - 3.14), Flask 3.1
- **Database & ORM:** SQLite 3, Flask-SQLAlchemy 3.1
- **Frontend:** Semantic HTML5, Custom Responsive CSS3 (Modern Dashboard in Blue & Indigo), Vanilla JavaScript
- **Templating Engine:** Jinja2
- **Testing Framework:** Pytest 9.2 (15 automated unit and integration tests)
- **Version Control:** Git 2.x & GitHub

---

## 3. Application Features

### Module A — Student Information Management System
- **Comprehensive Student Profile:** Automatically generated Student ID, Full Name, unique Roll Number, unique Email, Phone Number, Department, Year of Study, Semester, Gender, Address, and Date of Admission.
- **Full CRUD Functionality:** Create new students, list all registered students, search by student name or roll number, filter by department, view detailed student profile, edit information, and delete with interactive confirmation dialogs.
- **Validation & Integrity:** Server-side regex validation for emails, phone numbers, and required fields; strict uniqueness enforcement on Roll Number and Email Address with clear feedback alerts.
- **Relational Integrity:** Deleting a student cascades cleanly and restores open seats for any active course registrations.

### Module B — Online Student Course Registration System
- **Course Catalog:** Course ID, unique Course Code, Course Title, Syllabus Description, Department, Credits, Maximum Capacity, Available Seats, and Instructor Name.
- **Live Seat Availability:** Visual seat capacity indicators (`open`, `filling fast`, `class full`), preventing over-enrollment when seats reach 0.
- **Transactional Enrollment:** Atomic enrollment in SQLite transactions that decrements available seats upon registration and restores seats upon cancellation.
- **Duplicate Prevention:** Prevents duplicate active registrations for the same student-course combination.
- **Master Registrations Roster:** View all historical and active course enrollments with filterable status indicators and one-click cancellation.

### Module C — Git Branch Management (Question A)
- **Educational Guide:** Comprehensive explanations of Git repositories, pointers, feature branches, fast-forward/three-way merges, and branch cleanup.
- **Safe Live Control Panel:** Allows interacting with the local project repository (create branch, switch branch, merge into current, delete branch) via safe, parameterized Python subprocesses (no `shell=True`, timeout-enforced, protected against deleting `main`/`master`).
- **Real-Time Repo Inspection:** Displays current active branch, local branches list, and recent commit history (`git log --oneline`).

### Module D — Git & GitHub Workflow (Question B)
- **10-Step Interactive Guide:** Covers creating a repository, cloning, adding files, modifying files, `git status`, staging (`git add .`), committing (`git commit -m "..."`), remote inspection (`git remote -v`), pushing (`git push -u origin main`), and pulling updates (`git pull origin main`).
- **Step-by-Step Breakdown:** Command syntax, copy-to-clipboard buttons, architectural rationale, and real terminal output snippets.

### Module E — Complete Git Workflow & Collaborative Development (Question C)
- **Multi-Developer Simulation:** Step-by-step parallel development model featuring Developer 1 (`feature-student-management`) and Developer 2 (`feature-course-registration`) integrating on `main`.
- **Merge Conflict Laboratory:** Visual breakdown of Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) and a standard 3-step manual resolution algorithm.
- **Student Mastery Checklist:** Interactive session-backed Git skill tracker with dynamic progress bar.

### Academic Practical Demonstrations Section (`/practicals`)
- Dedicated examination laboratory document formatted specifically for university lab exams.
- Contains Aim, Software Requirements, Algorithms / Procedures, Flask Implementation Overviews, Git Command References, Sample Terminal Outputs, and Results for **Practicals A, B, and C**.

---

## 4. Project Structure

```text
Student-information-management-system/
│
├── app.py                          # Application factory, CSRF security, error handlers, seed trigger
├── config.py                       # Configuration classes (Development, Testing)
├── models.py                       # SQLAlchemy models: Student, Course, CourseRegistration, seed data
├── requirements.txt                # Production and testing dependencies
├── README.md                       # Comprehensive project documentation
├── .gitignore                      # Git exclusions (venv, instance db, caches, secrets)
│
├── instance/                       # Local SQLite database directory (git-ignored)
│   ├── .gitkeep
│   └── student_management.db       # Persistent SQLite database
│
├── routes/                         # Modular Flask Blueprints
│   ├── __init__.py                 # Blueprint exports
│   ├── dashboard.py                # Landing dashboard & About routes
│   ├── students.py                 # Student CRUD & search routes
│   ├── courses.py                  # Course catalog & registration routes
│   ├── git_workflow.py             # Git branching, workflow & collaboration routes
│   └── practicals.py               # Week-8 lab exam demonstrations
│
├── services/                       # Business logic services
│   ├── __init__.py
│   └── git_service.py              # Safe subprocess Git execution wrapper
│
├── templates/                      # Jinja2 HTML5 templates
│   ├── base.html                   # Common layout with responsive sidebar navigation
│   ├── dashboard.html              # Landing metrics, quick links, recent activity
│   ├── about.html                  # Architecture overview & FAQ
│   ├── practicals.html             # Laboratory demonstration writeups (A, B, C)
│   ├── students/
│   │   ├── list.html               # Student directory with search & department filter
│   │   ├── add.html                # Add student form
│   │   ├── edit.html               # Edit student form
│   │   └── details.html            # Individual profile & course enrollment card
│   ├── courses/
│   │   ├── list.html               # Course catalog & seat badges
│   │   ├── add.html                # Add course form
│   │   ├── details.html            # Course details & enrolled roster
│   │   ├── register.html           # Student course registration portal
│   │   └── registrations.html      # Master registration ledger
│   ├── git/
│   │   ├── branches.html           # Git branch management practical panel & guide
│   │   ├── github_workflow.html    # Step-by-step GitHub workflow tutorial
│   │   └── collaboration.html      # Collaborative workflows, conflicts, checklist
│   └── errors/
│       ├── 404.html                # Page not found error handler
│       └── 500.html                # Internal server error handler
│
├── static/                         # Static web assets
│   ├── css/
│   │   └── style.css               # Modern academic dashboard theme
│   └── js/
│       └── main.js                 # Modal confirmations, clipboard, dynamic seat checker
│
└── tests/                          # Automated Pytest suite
    ├── __init__.py
    └── test_app.py                 # 15 automated test cases with in-memory SQLite DB
```

---

## 5. Prerequisites

Before installing the application, ensure the following are installed on your Windows machine:
1. **Python 3.10 or newer** (Verify by typing `python --version` in PowerShell or Command Prompt).
2. **Git** (Verify by typing `git --version`).
3. Modern web browser (Chrome, Edge, Firefox).

---

## 6. Installation & Execution Guide (Windows)

Follow these exact steps in PowerShell or Command Prompt:

### Step 1: Clone the GitHub Repository
```powershell
git clone https://github.com/Itzx-kush/Student-information-management-system.git
cd Student-information-management-system
```

### Step 2: Create a Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment
On Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` or activate using standard Command Prompt: `venv\Scripts\activate.bat`)*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Start the Flask Application
```powershell
python app.py
```

### Step 6: Access the Application
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

### Stopping the Application
To shut down the local server, return to your terminal window and press:
```text
Ctrl + C
```

---

## 7. Database Initialization & Demonstration Data

The application uses **SQLite** located at:
```text
instance/student_management.db
```
- The database is created automatically upon first run.
- **Demonstration Seed Data:** When the database is newly initialized, the application automatically populates **6 academic demonstration courses** (Data Structures, DBMS, Web with Flask, Software Engineering, AI & Machine Learning, Digital Signal Processing) and **3 sample student profiles**.
- **Data Persistence:** Existing records are **never overwritten or deleted** on restart. All user additions, updates, registrations, and drops persist across sessions.

---

## 8. Running Automated Tests

A comprehensive test suite of 15 automated tests is included in `tests/test_app.py`. Tests execute against an isolated in-memory SQLite database (`sqlite:///:memory:`) to ensure development data is never modified.

To execute the test suite:
```powershell
pytest -v
```

Expected output:
```text
tests/test_app.py::test_dashboard_loads PASSED
tests/test_app.py::test_student_creation PASSED
tests/test_app.py::test_student_listing_and_search PASSED
tests/test_app.py::test_student_editing PASSED
tests/test_app.py::test_student_deletion PASSED
tests/test_app.py::test_duplicate_student_records_rejected PASSED
tests/test_app.py::test_course_listing_and_creation PASSED
tests/test_app.py::test_course_registration_and_seat_decrement PASSED
tests/test_app.py::test_duplicate_course_registration_prevented PASSED
tests/test_app.py::test_course_capacity_enforced PASSED
tests/test_app.py::test_registration_cancellation_restores_capacity PASSED
tests/test_app.py::test_git_tutorial_pages_load PASSED
tests/test_app.py::test_practicals_page_loads PASSED
tests/test_app.py::test_about_page_loads PASSED
tests/test_app.py::test_git_service_branch_validation PASSED

====================== 15 passed in 2.86s =======================
```

---

## 9. Git Commands Demonstrated

This project demonstrates all core Git operations required by university curricula:

```bash
# 1. Repository Initialization & Status
git init
git status
git log --oneline

# 2. File Staging & Commits
git add .
git commit -m "Your descriptive commit message"

# 3. Branch Management (Question A)
git branch
git branch feature-student
git switch feature-student
git switch main
git merge feature-student
git branch -d feature-student

# 4. Remote Operations & Tracking (Question B)
git remote -v
git remote add origin https://github.com/Itzx-kush/Student-information-management-system.git
git push -u origin main
git pull origin main

# 5. Collaborative Team Workflow (Question C)
git switch -c feature-course-registration
git push -u origin feature-course-registration
```

---

## 10. Screenshots & User Interface

### Landing Dashboard
*Displays summary counters for students, courses, registrations, quick access cards for Practicals A, B, and C, and the recent registrations ledger.*
```text
+-------------------------------------------------------------------------------+
|  Week 8 Academic Lab   |   Total Students: 3   |   Offered Courses: 6         |
|  Dashboard Overview    |   Active Regs: 4      |   Available Courses: 6       |
+-------------------------------------------------------------------------------+
|  [ Practical A Card ]       [ Practical B Card ]       [ Practical C Card ]   |
|  Student CRUD & Branching   Git & GitHub Remote        Courses & Collaboration|
+-------------------------------------------------------------------------------+
```

### Student Information Management (`/students`)
*Searchable table with roll numbers, departments, semesters, email links, and View / Edit / Delete actions with confirmation modals.*

### Course Registration Portal (`/courses/register`)
*Dropdowns for student and course selection, live seat counter badges (`open`, `filling fast`, `class full`), and atomic seat booking.*

### Git Branch Management Control Panel (`/git/branches`)
*Live branch operations directly executing safe, parameter-checked Git commands on the local repository alongside educational theory.*

---

## 11. Security & Quality Safeguards

1. **CSRF Protection:** State-changing HTTP verbs (`POST`, `PUT`, `DELETE`) are guarded by cryptographic session tokens injected via Jinja context processors.
2. **Safe Subprocess Execution:** Git operations use Python's `subprocess.run` with `shell=False`, strict argument arrays, and a 5-second timeout, completely preventing command injection.
3. **Protected Branches:** Branch deletion rules hard-block deleting `main`, `master`, or the currently checked-out branch.
4. **Parameterized Database Operations:** All database interactions utilize SQLAlchemy ORM with bound parameters, safeguarding against SQL injection.
5. **Clean Secrets Management:** Fallback development secret key with environment-variable override (`SECRET_KEY`).

---

## 12. Verification Checklist

- [x] Single consolidated Flask application satisfying Questions A, B, and C.
- [x] Student Information Management System with complete CRUD operations.
- [x] Input validation with unique roll number and email enforcement.
- [x] Online Course Registration with dynamic seat decrement/restoration.
- [x] Duplicate enrollment blocked; over-capacity registration blocked.
- [x] Safe Git branch management control panel (create, switch, merge, delete).
- [x] Git & GitHub remote workflow tutorial (10 steps).
- [x] Multi-developer collaborative workflow, PR review guide, and conflict resolution lab.
- [x] Dedicated Week-8 Practical Demonstrations examination page (`/practicals`).
- [x] SQLite database persists cleanly between restarts without data loss.
- [x] 15 automated pytest tests passing.
- [x] Modern, responsive dashboard design in blue and indigo.
- [x] Complete README with Windows setup instructions and commands.

---

## 13. License & Academic Attribution

Created for **Week 8 — Flask + Git + GitHub Practical Application** under university laboratory coursework guidelines. Developed and maintained by **Itzx-kush**.
