from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_db
from equipment.equipment import login_required

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')


@messages_bp.route('/')
@login_required
def inbox():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT m.*, u.name AS sender_name "
        "FROM messages m JOIN users u ON m.sender_id = u.id "
        "WHERE m.receiver_id = %s "
        "ORDER BY m.created_at DESC",
        (session['user_id'],)
    )
    messages = cursor.fetchall()

    # Mark messages as read after fetch
    cursor = db.cursor()
    cursor.execute(
        "UPDATE messages SET is_read = TRUE WHERE receiver_id = %s AND is_read = FALSE",
        (session['user_id'],)
    )
    db.commit()

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name FROM users WHERE id != %s ORDER BY name",
        (session['user_id'],)
    )
    contacts = cursor.fetchall()

    return render_template('messages/inbox.html', messages=messages, contacts=contacts)


@messages_bp.route('/start/<int:other_user_id>', methods=['POST'])
@login_required
def start_conversation(other_user_id):
    return redirect(url_for('messages.conversation', other_user_id=other_user_id))


@messages_bp.route('/conversation/<int:other_user_id>')
@login_required
def conversation(other_user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT name, phone FROM users WHERE id = %s", (other_user_id,))
    other_user = cursor.fetchone()
    if other_user:
        other_user_name = other_user['name']
        other_user_phone = other_user.get('phone') or 'Unknown phone'
    else:
        other_user_name = 'Unknown User'
        other_user_phone = 'Unknown phone'

    cursor.execute(
        "SELECT m.*, u.name AS sender_name "
        "FROM messages m JOIN users u ON m.sender_id = u.id "
        "WHERE (m.sender_id = %s AND m.receiver_id = %s) "
        "OR (m.sender_id = %s AND m.receiver_id = %s) "
        "ORDER BY m.created_at ASC",
        (session['user_id'], other_user_id, other_user_id, session['user_id'])
    )
    conversation_messages = cursor.fetchall()

    # Mark messages from other user as read
    cursor.execute(
        "UPDATE messages SET is_read = TRUE WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE",
        (other_user_id, session['user_id'])
    )
    db.commit()

    return render_template('messages/conversation.html', conversation=conversation_messages, other_user_id=other_user_id, other_user_name=other_user_name, other_user_phone=other_user_phone)


@messages_bp.route('/send/<int:receiver_id>', methods=['POST'])
@login_required
def send_message(receiver_id):
    content = request.form.get('content', '').strip()
    if not content:
        flash('Message cannot be empty.', 'error')
        return redirect(url_for('messages.conversation', other_user_id=receiver_id))

    if receiver_id == session['user_id']:
        flash('Cannot send message to yourself.', 'error')
        return redirect(url_for('messages.conversation', other_user_id=receiver_id))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get sender name
    cursor.execute("SELECT name FROM users WHERE id = %s", (session['user_id'],))
    sender = cursor.fetchone()
    sender_name = sender['name'] if sender else 'Someone'
    
    cursor.execute(
        "INSERT INTO messages (sender_id, receiver_id, content) VALUES (%s, %s, %s)",
        (session['user_id'], receiver_id, content)
    )
    db.commit()

    # Send notification to receiver
    cursor.execute(
        "INSERT INTO notifications (user_id, message, link) VALUES (%s, %s, %s)",
        (receiver_id, f"You have a new message from {sender_name}.", "/messages")
    )
    db.commit()

    flash('Message sent.', 'success')
    return redirect(url_for('messages.conversation', other_user_id=receiver_id))