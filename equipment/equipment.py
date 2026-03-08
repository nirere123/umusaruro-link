# ================================================================
# FILE        : equipment.py
# MEMBER      : Aliya — Equipment Management
# PURPOSE     : Equipment owners add/edit/delete equipment.
#               Farmers browse and view equipment details.
# ================================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from functools import wraps

equipment_bp = Blueprint('equipment', __name__)


# ── LOGIN REQUIRED DECORATOR ─────────────────────────────────────
# Any route decorated with @login_required will redirect to login
# if the user is not in the session. This is an access control tool.
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def owner_required(f):
    """Only equipment owners can access this route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_role') != 'equip_owner':
            flash('Only equipment owners can do this.', 'error')
            return redirect(url_for('equipment.equipment_list'))
        return f(*args, **kwargs)
    return decorated


# ── LIST EQUIPMENT (public) ───────────────────────────────────────
@equipment_bp.route('/')
@equipment_bp.route('/equipment')
@login_required
def equipment_list():
    """
    Shows all available equipment to farmers.
    Farmers use this to find equipment to rent.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Optional filter by location from search bar
    location_filter = request.args.get('location', '')

    if location_filter:
        cursor.execute(
            "SELECT e.*, u.name AS owner_name FROM equipment e "
            "JOIN users u ON e.owner_id = u.id "
            "WHERE e.availability = 'available' AND e.location LIKE %s",
            (f'%{location_filter}%',)
        )
    else:
        cursor.execute(
            "SELECT e.*, u.name AS owner_name FROM equipment e "
            "JOIN users u ON e.owner_id = u.id "
            "WHERE e.availability = 'available'"
        )

    equipment_items = cursor.fetchall()
    return render_template('equipment_list.html',
                           equipment=equipment_items,
                           location_filter=location_filter)


# ── MY EQUIPMENT (owner only) ─────────────────────────────────────
@equipment_bp.route('/my-equipment')
@login_required
@owner_required
def my_equipment():
    """Equipment owner sees all their own listings."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM equipment WHERE owner_id = %s ORDER BY created_at DESC",
        (session['user_id'],)
    )
    my_items = cursor.fetchall()
    return render_template('my_equipment.html', equipment=my_items)


# ── ADD EQUIPMENT ─────────────────────────────────────────────────
@equipment_bp.route('/add-equipment', methods=['GET', 'POST'])
@login_required
@owner_required
def add_equipment():
    """
    GET  → show the add equipment form
    POST → save new equipment to MySQL
    """
    if request.method == 'POST':
        name        = request.form['name'].strip()
        description = request.form['description'].strip()
        price       = request.form['price']
        location    = request.form['location'].strip()

        if not name or not price:
            flash('Name and price are required.', 'error')
            return render_template('add_equipment.html')

        db = get_db()
        cursor = db.cursor()

        # Prepared statement — %s prevents SQL injection
        cursor.execute(
            "INSERT INTO equipment (owner_id, name, description, price, location) "
            "VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], name, description, float(price), location)
        )
        db.commit()
        flash(f'"{name}" added successfully!', 'success')
        return redirect(url_for('equipment.my_equipment'))

    return render_template('add_equipment.html')


# ── EDIT EQUIPMENT ────────────────────────────────────────────────
@equipment_bp.route('/edit-equipment/<int:equipment_id>', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_equipment(equipment_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Only the owner of this equipment can edit it
    cursor.execute(
        "SELECT * FROM equipment WHERE id = %s AND owner_id = %s",
        (equipment_id, session['user_id'])
    )
    item = cursor.fetchone()
    if not item:
        flash('Equipment not found or not yours.', 'error')
        return redirect(url_for('equipment.my_equipment'))

    if request.method == 'POST':
        name        = request.form['name'].strip()
        description = request.form['description'].strip()
        price       = request.form['price']
        location    = request.form['location'].strip()

        cursor.execute(
            "UPDATE equipment SET name=%s, description=%s, price=%s, location=%s "
            "WHERE id=%s AND owner_id=%s",
            (name, description, float(price), location, equipment_id, session['user_id'])
        )
        db.commit()
        flash('Equipment updated!', 'success')
        return redirect(url_for('equipment.my_equipment'))

    return render_template('edit_equipment.html', item=item)


# ── DELETE EQUIPMENT ──────────────────────────────────────────────
@equipment_bp.route('/delete-equipment/<int:equipment_id>', methods=['POST'])
@login_required
@owner_required
def delete_equipment(equipment_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM equipment WHERE id = %s AND owner_id = %s",
        (equipment_id, session['user_id'])
    )
    db.commit()
    flash('Equipment deleted.', 'info')
    return redirect(url_for('equipment.my_equipment'))


# ── VIEW DETAIL ───────────────────────────────────────────────────
@equipment_bp.route('/equipment/<int:equipment_id>')
@login_required
def equipment_detail(equipment_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT e.*, u.name AS owner_name, u.phone AS owner_phone "
        "FROM equipment e JOIN users u ON e.owner_id = u.id "
        "WHERE e.id = %s",
        (equipment_id,)
    )
    item = cursor.fetchone()
    if not item:
        flash('Equipment not found.', 'error')
        return redirect(url_for('equipment.equipment_list'))
    return render_template('equipment_detail.html', item=item)
