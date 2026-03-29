# ================================================================
# FILE        : app.py
# MEMBER      : All Members — Connect everything together
# PURPOSE     : Main Flask app. Registers all 4 modules.
#               Run this file to start the server.
#
# HOW TO RUN:
#   1. Run database.sql in MySQL first      (Member 1)
#   2. pip install flask mysql-connector-python bcrypt
#   3. python -m APIs.app  (or python APIs/app.py from root)
#   4. Open http://127.0.0.1:5000
# ================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, redirect, url_for, session, render_template
from database.db import close_db

# ── Import configuration ──────────────────────────────────────────
from config import *

# ── Import each member's module ───────────────────────────────────
from authentication.auth import auth
from equipment.equipment import equipment_bp
from rental.rental import rental_bp
from farmers import farmers_bp
from messages import messages_bp
from payments import payments_bp
from admin import admin_bp
from profile import profile_bp
from notifications import notifications_bp

# Set up template and static folders (point to root directory)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(root_dir, 'templates')
static_dir = os.path.join(root_dir, 'assets')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# ── App Configuration ─────────────────────────────────────────────
app.secret_key = SECRET_KEY

# MySQL database settings from config
app.config['MYSQL_HOST']     = MYSQL_HOST
app.config['MYSQL_USER']     = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB']       = MYSQL_DB

# File upload settings from config
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ── Register Blueprints (plug in each module) ─────────────────────
app.register_blueprint(auth)
app.register_blueprint(equipment_bp)
app.register_blueprint(rental_bp)
app.register_blueprint(farmers_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(notifications_bp)

# ── Error Handlers ────────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

# ── Clean up DB connection after every request ──────────────────
app.teardown_appcontext(close_db)

# ── Context processor for unread messages count ──────────────────
@app.context_processor
def inject_unread_count():
    if 'user_id' in session:
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM messages WHERE receiver_id = %s AND is_read = FALSE",
                (session['user_id'],)
            )
            unread_messages = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = FALSE",
                (session['user_id'],)
            )
            unread_notifications = cursor.fetchone()[0]
            return {'unread_messages_count': unread_messages, 'unread_notifications_count': unread_notifications}
        except:
            return {'unread_messages_count': 0, 'unread_notifications_count': 0}
    return {'unread_messages_count': 0, 'unread_notifications_count': 0}


# ── Home redirect ─────────────────────────────────────────────────
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('equipment.equipment_list'))
    return redirect(url_for('auth.login'))


# ── Debug: List uploaded images ──────────────────────────────────
@app.route('/debug/images')
def debug_images():
    """List all files in uploads folder (for debugging)"""
    import os
    uploads_dir = os.path.join(static_dir, 'uploads')
    try:
        files = os.listdir(uploads_dir)
        files = [f for f in files if f not in ['.gitkeep']]
        return f"""
        <h2>Uploaded Images ({len(files)} files)</h2>
        <ul>
        {''.join([f'<li><a href="/static/uploads/{f}">{f}</a></li>' for f in files])}
        </ul>
        """
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
