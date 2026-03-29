# FILE: profile.py
# MEMBER: Profile Team
# PURPOSE: User profile management - view, edit profile, change password

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_db
import bcrypt

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

# ── Helper function to get user profile data ──────────────────────
def get_user_profile(user_id):
    """Get complete user profile including farmer data if applicable"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get basic user info
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return None

    # If user is a farmer, get additional farmer info
    if user['role'] == 'farmer':
        cursor.execute("SELECT * FROM farmers WHERE user_id = %s", (user_id,))
        farmer_data = cursor.fetchone()
        if farmer_data:
            user.update(farmer_data)

    return user

# ── Route: View Profile ────────────────────────────────────────────
@profile_bp.route('/')
def view():
    """Show current logged in user their own profile"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('auth.login'))

    user = get_user_profile(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))

    return render_template('profile/view.html', user=user)

# ── Route: Edit Profile ────────────────────────────────────────────
@profile_bp.route('/edit', methods=['GET', 'POST'])
def edit():
    """Form to update user profile information"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('auth.login'))

    user = get_user_profile(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        phone = request.form.get('phone', '').strip()

        # Validation
        if not name or not location:
            flash('Name and location are required', 'error')
            return render_template('profile/edit.html', user=user)

        if len(phone) > 0 and len(phone) < 10:
            flash('Phone number must be at least 10 digits', 'error')
            return render_template('profile/edit.html', user=user)

        # Update users table
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE users
            SET name = %s, location = %s, phone = %s
            WHERE id = %s
        """, (name, location, phone, session['user_id']))

        # If user is farmer, update farmers table too
        if user['role'] == 'farmer':
            farm_location = request.form.get('farm_location', '').strip()
            crop_type = request.form.get('crop_type', '').strip()
            bio = request.form.get('bio', '').strip()

            cursor.execute("""
                UPDATE farmers
                SET farm_location = %s, crop_type = %s, bio = %s
                WHERE user_id = %s
            """, (farm_location, crop_type, bio, session['user_id']))

        db.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile.view'))

    return render_template('profile/edit.html', user=user)

# ── Route: Change Password ─────────────────────────────────────────
@profile_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Form to change user password"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not current_password or not new_password or not confirm_password:
            flash('All password fields are required', 'error')
            return render_template('profile/change_password.html')

        if len(new_password) < 6:
            flash('New password must be at least 6 characters', 'error')
            return render_template('profile/change_password.html')

        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('profile/change_password.html')

        # Verify current password
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
            flash('Current password is incorrect', 'error')
            return render_template('profile/change_password.html')

        # Hash new password and update
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor = db.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password.decode('utf-8'), session['user_id']))
        db.commit()

        flash('Password changed successfully', 'success')
        return redirect(url_for('profile.view'))

    return render_template('profile/change_password.html')
