from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        else:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
        
        # Validate input
        if not username or not email or not password:
            if request.content_type == 'application/json':
                return jsonify({'error': 'Missing required fields'}), 400
            flash('Missing required fields', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            if request.content_type == 'application/json':
                return jsonify({'error': 'Username already exists'}), 400
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            if request.content_type == 'application/json':
                return jsonify({'error': 'Email already exists'}), 400
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        if request.content_type == 'application/json':
            return jsonify({'message': 'User registered successfully'}), 201
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
        
        # Validate input
        if not username or not password:
            if request.content_type == 'application/json':
                return jsonify({'error': 'Missing required fields'}), 400
            flash('Missing required fields', 'error')
            return render_template('login.html')
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            if request.content_type == 'application/json':
                return jsonify({'error': 'Invalid username or password'}), 401
            flash('Invalid username or password', 'error')
            return render_template('login.html')
        
        # Log in user
        login_user(user)
        
        if request.content_type == 'application/json':
            return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
        
        flash('Login successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    
    if request.content_type == 'application/json':
        return jsonify({'message': 'Logout successful'}), 200
    
    flash('Logout successful!', 'success')
    return redirect(url_for('index'))
