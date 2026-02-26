from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_bcrypt import Bcrypt
from supabase_client import supabase
from functools import wraps

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        gender = request.form.get('gender', 'feminine')

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        # Check if user already exists
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        if existing_user.data:
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')

        # Hash password and store in Supabase
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            supabase.table('users').insert({
                'name': name,
                'email': email,
                'password_hash': password_hash,
                'gender': gender
            }).execute()
            
            # Automatically log in and redirect to survey
            user_res = supabase.table('users').select('*').eq('email', email).execute()
            if user_res.data:
                session['user_id'] = user_res.data[0]['id']
                session['user_name'] = name
                return redirect(url_for('survey.survey_page'))
            
            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return render_template('auth/register.html')

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/login.html')

        # Get user from Supabase
        user_response = supabase.table('users').select('*').eq('email', email).execute()
        user = user_response.data[0] if user_response.data else None

        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            from services.streak_engine import streak_engine
            streak_engine.record_activity(user['id'])
            
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
