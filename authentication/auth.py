from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt
from database.db import get_db

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        role     = request.form['role']
        location = request.form['location'].strip()
        phone    = request.form.get('phone', '').strip()

        if not name or not email or not password or not phone:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('This email is already registered.', 'error')
            return render_template('register.html')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO users (name, email, password, role, location, phone) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, hashed.decode('utf-8'), role, location, phone)
        )
        db.commit()
        new_user_id = cursor.lastrowid

        if role == 'farmer':
            cursor.execute(
                "INSERT INTO trust_history (farmer_id, completed_rentals, score) VALUES (%s, 0, 0.00)",
                (new_user_id,)
            )
            db.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            flash('Email or password are not correct.', 'error')
            return render_template('login.html')

        session['user_id']   = user['id']
        session['user_name'] = user['name']
        session['user_role'] = user['role']

        flash(f"Welcome back, {user['name']}!", 'success')

        if user['role'] == 'equip_owner':
            return redirect(url_for('equipment.my_equipment'))
        else:
            return redirect(url_for('equipment.equipment_list'))

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
