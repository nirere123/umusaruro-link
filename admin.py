# ================================================================
# FILE        : admin.py
# PURPOSE     : Admin dashboard and admin-only controls
# ================================================================

from flask import Blueprint, render_template, redirect, url_for, session, flash
from database.db import get_db
from equipment.equipment import login_required
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('equipment.equipment_list'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()['total_users']

    cursor.execute("SELECT COUNT(*) AS total_rentals FROM rentals")
    total_rentals = cursor.fetchone()['total_rentals']

    cursor.execute("SELECT COUNT(*) AS total_payments FROM payments")
    total_payments = cursor.fetchone()['total_payments']

    cursor.execute("SELECT COUNT(*) AS total_equipment FROM equipment")
    total_equipment = cursor.fetchone()['total_equipment']

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_rentals=total_rentals,
                           total_payments=total_payments,
                           total_equipment=total_equipment)
