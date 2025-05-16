from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, AdminUser, ContactMessage, NewsletterSubscription, SiteConfig
import logging

# Blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Rutas principales
@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('Por favor complete todos los campos', 'error')
            return redirect(url_for('main.home'))

        try:
            new_message = ContactMessage(name=name, email=email, message=message)
            db.session.add(new_message)
            db.session.commit()
            flash('Mensaje enviado con éxito', 'success')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error al guardar mensaje: {str(e)}")
            flash('Ocurrió un error al enviar el mensaje', 'error')

        return redirect(url_for('main.home'))

@main_bp.route('/subscribe', methods=['POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form.get('email')

        if not email:
            return jsonify({'success': False, 'message': 'Email es requerido'})

        try:
            existing = NewsletterSubscription.query.filter_by(email=email).first()
            if existing:
                if not existing.active:
                    # Reactivar suscripción
                    existing.active = True
                    db.session.commit()
                    return jsonify({'success': True, 'message': 'Suscripción reactivada'})
                return jsonify({'success': False, 'message': 'Este email ya está suscrito'})

            subscription = NewsletterSubscription(email=email)
            db.session.add(subscription)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Suscripción exitosa'})
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error al suscribir: {str(e)}")
            return jsonify({'success': False, 'message': 'Error al procesar la suscripción'})

# Rutas de autenticación
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = AdminUser.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Credenciales inválidas', 'error')

    return render_template('admin_login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Rutas de administración
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    subscriptions = NewsletterSubscription.query.order_by(NewsletterSubscription.created_at.desc()).all()

    # Estadísticas
    stats = {
        'total_messages': ContactMessage.query.count(),
        'unread_messages': ContactMessage.query.filter_by(read=False).count(),
        'total_subscriptions': NewsletterSubscription.query.filter_by(active=True).count()
    }

    return render_template('admin_dashboard.html',
                          messages=messages,
                          subscriptions=subscriptions,
                          stats=stats)

@admin_bp.route('/messages')
@login_required
def messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)

@admin_bp.route('/messages/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.read = True
    db.session.commit()
    return jsonify({'success': True})

# Nueva ruta para cambiar el estado de leído/no leído de un mensaje
@admin_bp.route('/messages/toggle/<int:message_id>', methods=['POST'])
@login_required
def toggle_message_status(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    message.read = not message.read
    db.session.commit()
    flash('Estado del mensaje actualizado', 'success')
    return redirect(url_for('admin.messages'))

# Nueva ruta para eliminar un mensaje
@admin_bp.route('/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Mensaje eliminado', 'success')
    return redirect(url_for('admin.messages'))

@admin_bp.route('/subscriptions')
@login_required
def subscriptions():
    subscriptions = NewsletterSubscription.query.order_by(NewsletterSubscription.created_at.desc()).all()
    return render_template('admin_subscriptions.html', subscriptions=subscriptions)

@admin_bp.route('/subscriptions/<int:subscription_id>/toggle', methods=['POST'])
@login_required
def toggle_subscription(subscription_id):
    subscription = NewsletterSubscription.query.get_or_404(subscription_id)
    subscription.active = not subscription.active
    db.session.commit()
    return jsonify({'success': True, 'active': subscription.active})

@admin_bp.route('/settings')
@login_required
def settings():
    configs = SiteConfig.query.all()
    return render_template('admin_settings.html', configs=configs)

@admin_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    for key, value in request.form.items():
        if key.startswith('config_'):
            config_key = key[7:]  # Quitar el prefijo 'config_'
            config = SiteConfig.query.filter_by(key=config_key).first()

            if config:
                config.value = value
            else:
                config = SiteConfig(key=config_key, value=value)
                db.session.add(config)

    db.session.commit()
    flash('Configuración actualizada', 'success')
    return redirect(url_for('admin.settings'))
