from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import Employee
from werkzeug.security import check_password_hash

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        employee = Employee.query.filter_by(email=email).first()

        if employee and check_password_hash(employee.password_hash, password):
            login_user(employee)

            flash(f'Добро пожаловать, {employee.full_name}!', 'success')
            return redirect(url_for('views.admin_faq')) 
        else:
            flash('Неверный email или пароль.', 'error')

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('views.index'))