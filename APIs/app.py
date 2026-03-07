from flask import Flask, redirect, url_for, session
from db import close_db
from auth      import auth          
from equipment import equipment_bp  
from rental    import rental_bp     

app = Flask(__name__)

# App Configuration ─────────────────────────────────────────────
app.secret_key = 'umusaruro-link-secret-2026'   # Needed for sessions

# MySQL database settings — update these to match your machine
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'   # ← change this
app.config['MYSQL_DB']       = 'umusaruro_link'

# ── Register Blueprints ─────────────────────
app.register_blueprint(auth)
app.register_blueprint(equipment_bp)
app.register_blueprint(rental_bp)

# ── Clean up DB connection after every request ────────────────────
app.teardown_appcontext(close_db)


# ── Home redirect ─────────────────────────────────────────────────
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('equipment.equipment_list'))
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    app.run(debug=True)
