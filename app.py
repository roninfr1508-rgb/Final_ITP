from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from config import Config
from controllers.auth import AuthController, login_required
from controllers.admin import AdminController
from controllers.user import UserController

app = Flask(__name__)
app.config.from_object(Config)


# ==================== МАРШРУТЫ АВТОРИЗАЦИИ (AUTH) ====================

@app.route('/')
def index():
    """Если пользователь зашел на главную — перенаправляем на дашборд или логин."""
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login_route'))


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if AuthController.login(username, password):
            if session.get('role') == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))

        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Дополнительная проверка длины на бэкенде (Task 2)
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long.')
            return render_template('register.html')
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.')
            return render_template('register.html')

        success, message = AuthController.register(username, password)
        if success:
            flash('Registration successful! Please log in.')
            return redirect(url_for('login_route'))
        else:
            flash(message)  # Выведет "Username already exists", если имя занято

    return render_template('register.html')


@app.route('/logout')
def logout_route():
    AuthController.logout()
    return redirect(url_for('login_route'))


# ==================== ПАНЕЛЬ АДМИНИСТРАТОРА (ADMIN) ====================

@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    # Собираем статистику (кол-во пользователей, записей и последние 5 юзеров)
    data = AdminController.get_dashboard_data()
    return render_template('admin_dashboard.html', **data)


@app.route('/admin/users', methods=['GET'])
@login_required(role='admin')
def admin_users():
    users = AdminController.list_users()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/create', methods=['POST'])
@login_required(role='admin')
def admin_create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')  # 'admin' или 'user'

    if username and password and role:
        if AdminController.create_user(username, password, role):
            flash(f"User '{username}' created successfully!")
        else:
            flash('Failed to create user (username might be taken).')
    else:
        flash('All fields are required.')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required(role='admin')
def admin_delete_user(user_id):
    # Передаем ID текущего админа, чтобы он не удалил сам себя
    if AdminController.delete_user(session.get('user_id'), user_id):
        flash('User and all their related students deleted.')
    else:
        flash('Action denied! You cannot delete your own admin account.')
    return redirect(url_for('admin_users'))


@app.route('/admin/students')
@login_required(role='admin')
def admin_students():
    """Просмотр ВСЕХ студентов всех пользователей с пагинацией по 10 штук."""
    page = request.args.get('page', 1, type=int)
    records, total_pages = AdminController.list_all_records_paginated(page, per_page=10)
    return render_template('admin_students.html', records=records, page=page, total_pages=total_pages)


# --- API ЭНДПОИНТ ДЛЯ ЖИВОГО ПОИСКА (Task 5 - JS Fetch) ---
@app.route('/api/admin/users/search')
@login_required(role='admin')
def api_search_users():
    """
    Принимает GET-запрос типа /api/admin/users/search?q=alex
    Используется фронтендерами для динамической фильтрации таблицы пользователей.
    """
    query = request.args.get('q', '').lower()
    users = AdminController.list_users()
    filtered = [u.to_dict() for u in users if query in u.username.lower()]
    return jsonify(filtered)


# ==================== ЛИЧНЫЙ КАБИНЕТ ПОЛЬЗОВАТЕЛЯ (USER) ====================

@app.route('/user/dashboard')
@login_required()
def user_dashboard():
    # Обычный пользователь видит ТОЛЬКО своих студентов
    records = UserController.get_my_records(session.get('user_id'))
    return render_template('user_dashboard.html', records=records)


@app.route('/user/students/add', methods=['POST'])
@login_required()
def user_add_student():
    # Получаем поля студента (как в 3-м ассаименте)
    name = request.form.get('name')
    age = request.form.get('age')
    group = request.form.get('group')
    gpa = request.form.get('gpa')

    if name and age and group and gpa:
        try:
            UserController.add_record(
                user_id=session.get('user_id'),
                name=name,
                age=age,
                group=group,
                gpa=gpa
            )
            flash('Student added successfully!')
        except ValueError:
            flash('Invalid format for Age or GPA.')
    else:
        flash('All student fields are required.')

    return redirect(url_for('user_dashboard'))


@app.route('/user/profile', methods=['GET', 'POST'])
@login_required()
def user_profile():
    user_id = session.get('user_id')
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if new_password and len(new_password) >= 6:
            UserController.update_password(user_id, new_password)
            flash('Password updated successfully!')
        else:
            flash('Password must be at least 6 characters long.')

    profile_data = UserController.get_profile_info(user_id)
    return render_template('user_profile.html', profile=profile_data)


# ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================

if __name__ == '__main__':
    # Приложение запустится локально на http://127.0.0.1:5000
    app.run(debug=Config.DEBUG)