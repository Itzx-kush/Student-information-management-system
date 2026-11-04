from flask import render_template
from routes import practicals_bp

@practicals_bp.route('/')
def list_practicals():
    """Week-8 Practical Demonstrations laboratory guide covering Practicals A, B, and C."""
    return render_template('practicals.html')
