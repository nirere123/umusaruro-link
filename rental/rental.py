# ================================================================
# FILE        : rental.py
# MEMBER      : Member 4 — Rental System & Trust History
# PURPOSE     : Farmers request rentals. Owners approve/reject.
#               Trust score updates after each completed rental.
# ================================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db
from datetime import date, datetime
from equipment import login_required   # Reuse Member 3's decorator

rental_bp = Blueprint('rental', __name__)


# ── REQUEST RENTAL 
────────────────────────────────────────────────
@rental_bp.route('/rent-equipment/<int:equipment_id>', methods=['GET', 'POST'])
@login_required
def rent_equipment(equipment_id):
    """
    Farmer fills out a form to request renting a piece of equipment.
    GET  → show the rental form
    POST → save rental request to MySQL with status = 'pending'
    """
    if session.get('user_role') != 'farmer':
        flash('Only farmers can request rentals.', 'error')
        return redirect(url_for('equipment.equipment_list'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get equipment info to show on the form
    cursor.execute("SELECT * FROM equipment WHERE id = %s", (equipment_id,))
    item = cursor.fetchone()

    if not item or item['availability'] != 'available':
        flash('This equipment is not available.', 'error')
        return redirect(url_for('equipment.equipment_list'))

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date   = request.form['end_date']
        message    = request.form.get('message', '').strip()

        # ── Calculate total cost ──────────────────────────────────
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end   = datetime.strptime(end_date,   '%Y-%m-%d').date()

        if end <= start:
            flash('End date must be after start date.', 'error')
            return render_template('rent_equipment.html', item=item)

        days       = (end - start).days
        total_cost = item['price'] * days

        # ── Insert rental request ─────────────────────────────────
        cursor.execute(
            "INSERT INTO rentals "
            "(farmer_id, equipment_id, start_date, end_date, message, total_cost) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (session['user_id'], equipment_id,
             start_date, end_date, message, total_cost)
        )
        db.commit()

        flash('Rental request sent! Waiting for owner approval.', 'success')
        return redirect(url_for('rental.my_rentals'))

    return render_template('rent_equipment.html', item=item)


# ── MY RENTALS (farmer view) 
──────────────────────────────────────
@rental_bp.route('/my-rentals')
@login_required
def my_rentals():
    """Farmer sees all their rental requests and their status."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT r.*, e.name AS equip_name, e.location AS equip_location "
        "FROM rentals r "
        "JOIN equipment e ON r.equipment_id = e.id "
        "WHERE r.farmer_id = %s "
        "ORDER BY r.created_at DESC",
        (session['user_id'],)
    )
    rentals = cursor.fetchall()

    # Also get trust score to show on page
    cursor.execute(
        "SELECT score, completed_rentals, cancelled_rentals "
        "FROM trust_history WHERE farmer_id = %s",
        (session['user_id'],)
    )
    trust = cursor.fetchone()

    return render_template('my_rentals.html', rentals=rentals, trust=trust)


# ── MANAGE REQUESTS (owner view) ─────────────────────────────────
@rental_bp.route('/manage-rentals')
@login_required
def manage_rentals():
    """Equipment owner sees all rental requests on their equipment."""
    if session.get('user_role') != 'equip_owner':
        return redirect(url_for('equipment.equipment_list'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT r.*, e.name AS equip_name, u.name AS farmer_name, u.phone AS farmer_phone "
        "FROM rentals r "
        "JOIN equipment e ON r.equipment_id  = e.id "
        "JOIN users     u ON r.farmer_id     = u.id "
        "WHERE e.owner_id = %s "
        "ORDER BY r.created_at DESC",
        (session['user_id'],)
    )
    requests = cursor.fetchall()
    return render_template('manage_rentals.html', requests=requests)


# ── APPROVE / REJECT 
──────────────────────────────────────────────
@rental_bp.route('/update-rental/<int:rental_id>/<action>', methods=['POST'])
@login_required
def update_rental(rental_id, action):
    """
    Owner approves or rejects a rental request.
    On approve: equipment availability → 'rented'
    On reject:  nothing changes on equipment
    """
    if session.get('user_role') != 'equip_owner':
        return redirect(url_for('equipment.equipment_list'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Verify this rental belongs to this owner's equipment
    cursor.execute(
        "SELECT r.*, e.owner_id, r.equipment_id FROM rentals r "
        "JOIN equipment e ON r.equipment_id = e.id "
        "WHERE r.id = %s AND e.owner_id = %s",
        (rental_id, session['user_id'])
    )
    rental = cursor.fetchone()
    if not rental:
        flash('Rental not found.', 'error')
        return redirect(url_for('rental.manage_rentals'))

    if action == 'approve':
        cursor.execute(
            "UPDATE rentals SET status = 'approved' WHERE id = %s", (rental_id,))
        # Mark equipment as rented so nobody else can book it
        cursor.execute(
            "UPDATE equipment SET availability = 'rented' WHERE id = %s",
            (rental['equipment_id'],)
        )
        db.commit()
        flash('Rental approved!', 'success')

    elif action == 'reject':
        cursor.execute(
            "UPDATE rentals SET status = 'rejected' WHERE id = %s", (rental_id,))
        db.commit()
        flash('Rental rejected.', 'info')

    return redirect(url_for('rental.manage_rentals'))


# ── MARK AS RETURNED 
──────────────────────────────────────────────
@rental_bp.route('/mark-returned/<int:rental_id>', methods=['POST'])
@login_required
def mark_returned(rental_id):
    """
    Owner marks equipment as returned.
    This frees the equipment for the next farmer AND updates trust score.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT r.*, e.owner_id, r.farmer_id, r.equipment_id "
        "FROM rentals r JOIN equipment e ON r.equipment_id = e.id "
        "WHERE r.id = %s AND e.owner_id = %s",
        (rental_id, session['user_id'])
    )
    rental = cursor.fetchone()
    if not rental:
        flash('Not found.', 'error')
        return redirect(url_for('rental.manage_rentals'))

    # Mark rental as returned
    cursor.execute(
        "UPDATE rentals SET status = 'returned' WHERE id = %s", (rental_id,))

    # Free up the equipment
    cursor.execute(
        "UPDATE equipment SET availability = 'available' WHERE id = %s",
        (rental['equipment_id'],)
    )

    # ── Update Trust Score 
────────────────────────────────────────
    # Completed rental → completed_rentals + 1
    # Score formula: (completed / total_rentals) × 5
    update_trust_score(cursor, rental['farmer_id'], completed=True)

    db.commit()
    flash('Marked as returned. Trust score updated!', 'success')
    return redirect(url_for('rental.manage_rentals'))


# ── TRUST SCORE LOGIC 
─────────────────────────────────────────────
def update_trust_score(cursor, farmer_id, completed=True):
    """
    Recalculates a farmer's trust score after a rental ends.
    
    Algorithm:
      - completed_rentals increases by 1 on success
      - cancelled_rentals increases by 1 on failure
      - score = (completed / total) × 5.0  (max score is 5.0)
    
    This is Member 4's core algorithm — explain this in the slides.
    """
    if completed:
        cursor.execute(
            "UPDATE trust_history "
            "SET completed_rentals = completed_rentals + 1 "
            "WHERE farmer_id = %s",
            (farmer_id,)
        )
    else:
        cursor.execute(
            "UPDATE trust_history "
            "SET cancelled_rentals = cancelled_rentals + 1 "
            "WHERE farmer_id = %s",
            (farmer_id,)
        )

    # Re-fetch totals to recalculate score
    cursor.execute(
        "SELECT completed_rentals, cancelled_rentals "
        "FROM trust_history WHERE farmer_id = %s",
        (farmer_id,)
    )
    row = cursor.fetchone()
    if row:
        total = row['completed_rentals'] + row['cancelled_rentals']
        if total > 0:
            new_score = round((row['completed_rentals'] / total) * 5.0, 2)
        else:
            new_score = 0.00
        cursor.execute(
            "UPDATE trust_history SET score = %s WHERE farmer_id = %s",
            (new_score, farmer_id)
        )

