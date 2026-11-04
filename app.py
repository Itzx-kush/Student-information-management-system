import os
import secrets
from flask import Flask, render_template, session, request, abort
from config import config_by_name
from models import db, seed_initial_data

def create_app(config_name=None):
    """Application factory for the Week 8 Flask Student Management & Git Workflow Lab."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)

    # Ensure the instance directory exists for SQLite database storage
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)

    # Built-in CSRF Protection
    @app.before_request
    def csrf_protect():
        # Ensure session contains a CSRF token
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)

        # Skip CSRF check in testing if disabled
        if not app.config.get('WTF_CSRF_ENABLED', True):
            return

        # Check state-changing HTTP methods
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            token = (
                request.form.get('csrf_token') or
                request.headers.get('X-CSRFToken') or
                request.headers.get('X-CSRF-Token')
            )
            expected_token = session.get('csrf_token')

            # Allow API / JSON requests if specifically authenticated, otherwise require CSRF
            if not token or not expected_token or not secrets.compare_digest(token, expected_token):
                abort(400, description="Invalid or missing CSRF security token.")

    @app.context_processor
    def inject_csrf_and_globals():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return {
            'csrf_token': session['csrf_token'],
            'app_name': "Week 8 — Student Management & Git Workflow Lab",
            'repo_url': "https://github.com/Itzx-kush/Student-information-management-system"
        }

    # Register blueprints
    from routes import dashboard_bp, students_bp, courses_bp, git_bp, practicals_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(git_bp)
    app.register_blueprint(practicals_bp)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html', error=e), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html', error=e), 500

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/404.html', error_title="400 - Bad Request", error=e), 400

    # Initialize Database and Seed Sample Data
    with app.app_context():
        db.create_all()
        # Seed initial courses and demo data only if database is empty
        seed_initial_data(db)

    return app

app = create_app()

if __name__ == '__main__':
    # Local Windows execution default: 127.0.0.1:5000
    app.run(host='127.0.0.1', port=5000, debug=True)
