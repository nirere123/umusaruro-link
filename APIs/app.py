# ================================================================
# FILE        : app.py
# MEMBER      : All Members — Connect everything together
# PURPOSE     : Main Flask app. Registers all 4 modules.
#               Run this file to start the server.
#
# HOW TO RUN:
#   1. Run database.sql in MySQL first      (Member 1)
#   2. pip install flask mysql-connector-python bcrypt
#   3. python app.py
#   4. Open http://127.0.0.1:5000
# ================================================================

from flask import Flask, redirect, url_for, session
from db import close_db

# ── Import each member's module ───────────────────────────────────
from auth      import auth         
from equipment import equipment_bp  
from rental    import rental_bp     

app = Flask(__name__)

# ── App Configuration ─────────────────────────────────────────────
app.secret_key = 'umusaruro-link-secret-2026'   # Needed for sessions

# MySQL database settings — update these to match your machine
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = 'Benjamin@32'   
app.config['MYSQL_DB']       = 'umusaruro_link'

#Register Blueprints (plug in each module)
app.register_blueprint(auth)
app.register_blueprint(equipment_bp)
app.register_blueprint(rental_bp)

# ── Clean up DB connection after every request ──────────────────
app.teardown_appcontext(close_db)


# ── Home redirect ─────────────────────────────────────────────────
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('equipment.equipment_list'))
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    app.run(debug=True)
