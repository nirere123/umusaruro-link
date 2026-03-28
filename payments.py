# ================================================================
# FILE        : payments.py
# PURPOSE     : Manage payment records (farmer payments + owner receipts)
# ================================================================

from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from database.db import get_db
from equipment.equipment import login_required
from datetime import date
from notifications import create_notification

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


# ================================================================
# FILE        : payments.py
# PURPOSE     : Manage payment records (farmer payments + owner receipts)
# ================================================================

from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from database.db import get_db
from equipment.equipment import login_required
from datetime import date
from notifications import create_notification

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


@payments_bp.route('/pay/<int:rental_id>', methods=['GET', 'POST'])
@login_required
def pay_rental(rental_id):
    """Handle MTN Mobile Money payment for rental"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get rental details
    cursor.execute("""
        SELECT r.*, e.name AS equipment_name, e.owner_id, u.name AS owner_name
        FROM rentals r
        JOIN equipment e ON r.equipment_id = e.id
        JOIN users u ON e.owner_id = u.id
        WHERE r.id = %s AND r.farmer_id = %s
    """, (rental_id, session['user_id']))

    rental = cursor.fetchone()
    if not rental:
        flash('Rental not found or not assigned to you.', 'error')
        return redirect(url_for('rental.my_rentals'))

    # Check if already paid
    cursor.execute("SELECT * FROM payments WHERE rental_id = %s", (rental_id,))
    existing_payment = cursor.fetchone()
    if existing_payment:
        flash('This rental has already been paid.', 'error')
        return redirect(url_for('payments.payment_history'))

    # Get farmer's phone number
    cursor.execute("SELECT phone FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    farmer_phone = user['phone'] if user else ''

    if request.method == 'POST':
        phone_number = request.form.get('phone_number', '').strip()

        # Validation
        if not phone_number:
            flash('Phone number is required.', 'error')
            return render_template('payments/pay.html', rental=rental, farmer_phone=farmer_phone)

        # MTN Mobile Money validation (Rwanda)
        if not (phone_number.startswith('078') or phone_number.startswith('079')):
            flash('Please enter a valid MTN Mobile Money number (starting with 078 or 079).', 'error')
            return render_template('payments/pay.html', rental=rental, farmer_phone=farmer_phone)

        if len(phone_number) != 10 or not phone_number.isdigit():
            flash('Phone number must be exactly 10 digits.', 'error')
            return render_template('payments/pay.html', rental=rental, farmer_phone=farmer_phone)

        # Process payment (simulated)
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO payments (rental_id, farmer_id, amount, status, payment_date, payment_method, phone_number)
            VALUES (%s, %s, %s, 'paid', %s, 'MTN Mobile Money', %s)
        """, (rental_id, session['user_id'], rental['total_cost'], date.today(), phone_number))
        db.commit()

        # Create notification for equipment owner
        amount_formatted = f"RWF {rental['total_cost']:,.0f}"
        create_notification(
            rental['owner_id'],
            f"Payment received: {amount_formatted} for equipment rental ({rental['equipment_name']})",
            url_for('payments.owner_payments')
        )

        flash(f"Payment of {amount_formatted} sent via MTN MoMo successfully!", 'success')
        return redirect(url_for('payments.payment_history'))

    return render_template('payments/pay.html', rental=rental, farmer_phone=farmer_phone)


@payments_bp.route('/history')
@login_required
def payment_history():
    """Show farmer's payment history"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, r.equipment_id, e.name AS equipment_name, e.location
        FROM payments p
        JOIN rentals r ON p.rental_id = r.id
        JOIN equipment e ON r.equipment_id = e.id
        WHERE p.farmer_id = %s
        ORDER BY p.created_at DESC
    """, (session['user_id'],))

    payments = cursor.fetchall()
    return render_template('payments/history.html', payments=payments)


@payments_bp.route('/owner')
@login_required
def owner_payments():
    """Show equipment owner's received payments"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, r.id AS rental_id, u.name AS farmer_name, e.name AS equipment_name,
               p.phone_number, p.payment_method
        FROM payments p
        JOIN rentals r ON p.rental_id = r.id
        JOIN equipment e ON r.equipment_id = e.id
        JOIN users u ON p.farmer_id = u.id
        WHERE e.owner_id = %s
        ORDER BY p.created_at DESC
    """, (session['user_id'],))

    payments = cursor.fetchall()
    return render_template('payments/owner_payments.html', payments=payments)
