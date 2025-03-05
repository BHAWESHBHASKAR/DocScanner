from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from database.models import db, User, CreditRequest

credit_bp = Blueprint('credit', __name__, url_prefix='/credit')

@credit_bp.route('/request', methods=['GET', 'POST'])
@login_required
def request_credits():
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = request.get_json()
            amount = data.get('amount')
            reason = data.get('reason')
        else:
            amount = request.form.get('amount')
            reason = request.form.get('reason')
        
        # Validate input
        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            if request.content_type == 'application/json':
                return jsonify({'error': 'Invalid amount'}), 400
            flash('Invalid amount', 'error')
            return render_template('request_credits.html')
        
        # Create credit request
        credit_request = CreditRequest(
            user_id=current_user.id,
            amount=amount,
            reason=reason,
            status='pending'
        )
        db.session.add(credit_request)
        db.session.commit()
        
        if request.content_type == 'application/json':
            return jsonify({'message': 'Credit request submitted successfully'}), 201
        
        flash('Credit request submitted successfully', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('request_credits.html')

@credit_bp.route('/approve/<int:request_id>', methods=['POST'])
@login_required
def approve_request(request_id):
    # Check if user is admin
    if current_user.role != 'admin':
        if request.content_type == 'application/json':
            return jsonify({'error': 'Unauthorized'}), 403
        flash('Unauthorized', 'error')
        return redirect(url_for('index'))
    
    # Get credit request
    credit_request = CreditRequest.query.get_or_404(request_id)
    
    # Check if request is pending
    if credit_request.status != 'pending':
        if request.content_type == 'application/json':
            return jsonify({'error': 'Request already processed'}), 400
        flash('Request already processed', 'error')
        return redirect(url_for('admin.credit_requests'))
    
    # Update request status
    credit_request.status = 'approved'
    credit_request.admin_id = current_user.id
    
    # Add credits to user
    user = User.query.get(credit_request.user_id)
    user.credits += credit_request.amount
    
    db.session.commit()
    
    if request.content_type == 'application/json':
        return jsonify({'message': 'Credit request approved successfully'}), 200
    
    flash('Credit request approved successfully', 'success')
    return redirect(url_for('admin.credit_requests'))

@credit_bp.route('/deny/<int:request_id>', methods=['POST'])
@login_required
def deny_request(request_id):
    # Check if user is admin
    if current_user.role != 'admin':
        if request.content_type == 'application/json':
            return jsonify({'error': 'Unauthorized'}), 403
        flash('Unauthorized', 'error')
        return redirect(url_for('index'))
    
    # Get credit request
    credit_request = CreditRequest.query.get_or_404(request_id)
    
    # Check if request is pending
    if credit_request.status != 'pending':
        if request.content_type == 'application/json':
            return jsonify({'error': 'Request already processed'}), 400
        flash('Request already processed', 'error')
        return redirect(url_for('admin.credit_requests'))
    
    # Update request status
    credit_request.status = 'denied'
    credit_request.admin_id = current_user.id
    
    db.session.commit()
    
    if request.content_type == 'application/json':
        return jsonify({'message': 'Credit request denied successfully'}), 200
    
    flash('Credit request denied successfully', 'success')
    return redirect(url_for('admin.credit_requests'))

@credit_bp.route('/adjust/<int:user_id>', methods=['POST'])
@login_required
def adjust_credits(user_id):
    # Check if user is admin
    if current_user.role != 'admin':
        if request.content_type == 'application/json':
            return jsonify({'error': 'Unauthorized'}), 403
        flash('Unauthorized', 'error')
        return redirect(url_for('index'))
    
    # Get user
    user = User.query.get_or_404(user_id)
    
    # Get amount
    if request.content_type == 'application/json':
        data = request.get_json()
        amount = data.get('amount')
    else:
        amount = request.form.get('amount')
    
    # Validate input
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        if request.content_type == 'application/json':
            return jsonify({'error': 'Invalid amount'}), 400
        flash('Invalid amount', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    # Update user credits
    user.credits = amount
    db.session.commit()
    
    if request.content_type == 'application/json':
        return jsonify({'message': 'Credits adjusted successfully'}), 200
    
    flash('Credits adjusted successfully', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))
