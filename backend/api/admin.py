"""
Admin Blueprint for Document Scanner Application

This module provides administrative functionality including:
- Dashboard with real-time analytics
- User management
- Credit request handling
- System analytics and reporting
- Data export capabilities

The blueprint is protected by role-based access control and requires admin privileges.

Author: Bhawesh Bhaskar
Date: March 2025
"""

from flask import (
    Blueprint, request, jsonify, render_template, redirect,
    url_for, flash, current_app as app, send_file
)
from flask_login import login_required, current_user
from database.models import db, User, Document, ScanLog, CreditRequest, DocumentMatch
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import pandas as pd
import json
import io
import csv

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Template context processors
@admin_bp.context_processor
def inject_now():
    """Add current timestamp to template context."""
    return {'now': datetime.now()}

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    
    Returns 403 for API requests and redirects to index for web requests.
    """
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            if request.content_type == 'application/json':
                return jsonify({'error': 'Admin access required'}), 403
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard showing system-wide analytics.
    
    Displays:
    - User, document, and scan statistics
    - Month-over-month changes
    - Top users by scan count and credit usage
    - Recent scan activity with match details
    - 7-day scan activity trends
    
    Returns:
        JSON response for API requests
        HTML template for web requests
    """
    # Time range for statistics
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    prev_month_start = start_date - timedelta(days=30)
    
    # Basic statistics
    stats = {
        'user_count': User.query.filter_by(role='user').count(),
        'document_count': db.session.query(func.count(Document.id)).scalar(),
        'scan_count': ScanLog.query.count(),
        'pending_requests': CreditRequest.query.filter_by(status='pending').count(),
        'match_count': DocumentMatch.query.count()
    }
    
    # Calculate month-over-month changes
    changes = {}
    for metric in ['user', 'document', 'scan', 'request']:
        prev_count = _get_count_for_period(metric, prev_month_start, start_date)
        curr_count = _get_count_for_period(metric, start_date, end_date)
        changes[f'{metric}_change'] = (
            ((curr_count - prev_count) / max(prev_count, 1)) * 100 if prev_count else 0
        )
    
    # Get top users by scan activity
    top_users = {
        'by_scans': _get_top_users_by_scans(),
        'by_credits': _get_top_users_by_credits()
    }
    
    # Get recent scan activity
    recent_scans = _get_recent_scans()
    scan_activity = _get_scan_activity_last_7_days()
    
    if request.content_type == 'application/json':
        return jsonify({
            'stats': {
                **stats,
                'changes': {k: round(v, 1) for k, v in changes.items()}
            },
            'top_users': top_users,
            'recent_scans': [
                {
                    'scan': scan.to_dict(),
                    'document': doc.to_dict(),
                    'match': match.to_dict() if match else None
                } for scan, doc, match in recent_scans
            ],
            'scan_activity': scan_activity
        }), 200
    
    return render_template(
        'admin/dashboard.html',
        **stats,
        **{k: round(v, 1) for k, v in changes.items()},
        top_users_by_scans=top_users['by_scans'],
        top_users_by_credits=top_users['by_credits'],
        recent_scans=recent_scans,
        scan_activity=json.dumps(scan_activity),
        system_status="online"
    )

def _get_count_for_period(metric, start_date, end_date):
    """Helper function to get count of items for a given time period."""
    model_map = {
        'user': User,
        'document': Document,
        'scan': ScanLog,
        'request': CreditRequest
    }
    return model_map[metric].query.filter(
        and_(
            model_map[metric].created_at >= start_date,
            model_map[metric].created_at <= end_date
        )
    ).count()

def _get_top_users_by_scans(limit=5):
    """Get users with the most scans."""
    return db.session.query(
        User.id, User.username, 
        func.count(ScanLog.id).label('scan_count')
    ).join(ScanLog).group_by(User.id).order_by(
        desc('scan_count')
    ).limit(limit).all()

def _get_top_users_by_credits(limit=5):
    """Get users with highest credit usage."""
    top_users = db.session.query(
        User.id, User.username,
        (User.total_credits_granted - User.credits).label('credits_used')
    ).filter(User.role == 'user').order_by(
        desc('credits_used')
    ).limit(limit).all()
    
    return top_users if top_users else [(0, 'No users yet', 0)]

def _get_recent_scans(limit=10):
    """Get recent scans with their document and match details."""
    return db.session.query(
        ScanLog, Document, DocumentMatch
    ).join(
        Document, ScanLog.document_id == Document.id
    ).outerjoin(
        DocumentMatch, ScanLog.id == DocumentMatch.scan_id
    ).order_by(ScanLog.created_at.desc()).limit(limit).all()

def _get_scan_activity_last_7_days():
    """Get daily scan activity metrics for the last 7 days."""
    today = datetime.now().date()
    activity = []
    
    for i in range(7):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        stats = db.session.query(
            func.count(ScanLog.id).label('total_scans'),
            func.count(DocumentMatch.id).label('matches_found'),
            func.avg(DocumentMatch.ai_similarity_score).label('avg_similarity')
        ).outerjoin(
            DocumentMatch, ScanLog.id == DocumentMatch.scan_id
        ).filter(
            ScanLog.created_at.between(day_start, day_end)
        ).first()
        
        activity.append({
            'date': day.strftime('%Y-%m-%d'),
            'total_scans': stats.total_scans,
            'matches_found': stats.matches_found or 0,
            'avg_similarity': float(stats.avg_similarity or 0)
        })
    
    return activity

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def users():
    """List all users with their details."""
    users = User.query.all()
    
    if request.content_type == 'application/json':
        return jsonify({'users': [user.to_dict() for user in users]}), 200
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def user_detail(user_id):
    """
    Show detailed information about a specific user.
    
    Includes:
    - Basic user information
    - Document statistics
    - Scan history
    - Credit usage
    """
    user = User.query.get_or_404(user_id)
    documents = Document.query.filter_by(user_id=user_id).all()
    
    # Get scan statistics
    scan_stats = db.session.query(
        func.count(ScanLog.id).label('total_scans'),
        func.count(DocumentMatch.id).label('total_matches'),
        func.avg(DocumentMatch.similarity_score).label('avg_similarity')
    ).join(
        Document, Document.user_id == user_id
    ).outerjoin(
        DocumentMatch, ScanLog.id == DocumentMatch.scan_id
    ).first()
    
    if request.content_type == 'application/json':
        return jsonify({
            'user': user.to_dict(),
            'documents': [doc.to_dict() for doc in documents],
            'stats': {
                'total_scans': scan_stats.total_scans,
                'total_matches': scan_stats.total_matches or 0,
                'avg_similarity': float(scan_stats.avg_similarity or 0)
            }
        }), 200
    
    return render_template(
        'admin/user_detail.html',
        user=user,
        documents=documents,
        scan_stats=scan_stats
    )

@admin_bp.route('/credit-requests', methods=['GET'])
@login_required
@admin_required
def credit_requests():
    """
    List all credit requests with user information.
    
    Returns:
        JSON response for API requests
        HTML template for web requests
    """
    # Use a join to get user information along with credit requests
    requests = db.session.query(CreditRequest, User)\
        .join(User, CreditRequest.user_id == User.id)\
        .order_by(CreditRequest.created_at.desc())\
        .all()
    
    if request.content_type == 'application/json':
        return jsonify({
            'requests': [{
                **req.to_dict(),
                'username': user.username,
                'status': req.status,
                'approved_by': req.approved_by,
                'approved_at': req.approved_at.isoformat() if req.approved_at else None
            } for req, user in requests]
        }), 200
    
    # Create a list of enhanced request objects with user information
    enhanced_requests = []
    for req, user in requests:
        req.username = user.username  # Add username attribute to request object
        enhanced_requests.append(req)
    
    return render_template('admin/credit_requests.html', requests=enhanced_requests)

@admin_bp.route('/credit-requests/<int:request_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_credit_request(request_id):
    """
    Approve a credit request and update user's credit balance.
    
    Args:
        request_id (int): ID of the credit request to approve
        
    Returns:
        JSON response with success/error message
    """
    try:
        credit_request = CreditRequest.query.get_or_404(request_id)
        
        # Check if request is already processed
        if credit_request.status != 'pending':
            return jsonify({
                'error': f'Request is already {credit_request.status}'
            }), 400
            
        # Get associated user
        user = User.query.get(credit_request.user_id)
        if not user:
            return jsonify({'error': 'Associated user not found'}), 404
            
        # Update credit request
        credit_request.status = 'approved'
        credit_request.approved_by = current_user.id
        credit_request.approved_at = datetime.utcnow()
        
        # Update user's credit balance
        user.credits += credit_request.amount
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'message': 'Credit request approved successfully',
            'request': {
                **credit_request.to_dict(),
                'username': user.username
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/credit-requests/<int:request_id>/reject', methods=['POST']) 
@login_required
@admin_required
def reject_credit_request(request_id):
    """
    Reject a credit request.
    
    Args:
        request_id (int): ID of the credit request to reject
        
    Returns:
        JSON response with success/error message
    """
    try:
        credit_request = CreditRequest.query.get_or_404(request_id)
        
        # Check if request is already processed
        if credit_request.status != 'pending':
            return jsonify({
                'error': f'Request is already {credit_request.status}'
            }), 400
            
        # Update credit request
        credit_request.status = 'rejected'
        credit_request.approved_by = current_user.id
        credit_request.approved_at = datetime.utcnow()
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'message': 'Credit request rejected successfully',
            'request': credit_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics', methods=['GET'])
@login_required
@admin_required
def analytics():
    """
    Show system analytics and reporting.
    
    Includes:
    - Scan count by day (last 30 days)
    - User registration by day (last 30 days)
    - Credit usage by day (last 30 days)
    - System performance metrics (mocked)
    - Database size
    
    Returns:
        JSON response for API requests
        HTML template for web requests
    """
    # Get scan count by day (last 30 days)
    today = datetime.now().date()
    scan_by_day = []
    for i in range(30):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        count = ScanLog.query.filter(ScanLog.created_at.between(day_start, day_end)).count()
        scan_by_day.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Get user registration by day (last 30 days)
    user_by_day = []
    for i in range(30):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        count = User.query.filter(User.created_at.between(day_start, day_end)).count()
        user_by_day.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Get credit usage by day (last 30 days)
    credit_by_day = []
    for i in range(30):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        count = ScanLog.query.filter(ScanLog.created_at.between(day_start, day_end)).count()
        credit_by_day.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count  # Each scan uses 1 credit
        })
    
    if request.content_type == 'application/json':
        return jsonify({
            'scan_by_day': scan_by_day,
            'user_by_day': user_by_day,
            'credit_by_day': credit_by_day
        }), 200
    
    # Calculate or mock system performance metrics
    avg_scan_time = 0.75  # Mock value in seconds
    avg_api_time = 0.32   # Mock value in seconds
    
    # Calculate database size
    import os
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    
    # Convert to human-readable format
    if db_size_bytes < 1024:
        db_size = f"{db_size_bytes} bytes"
    elif db_size_bytes < 1024 * 1024:
        db_size = f"{db_size_bytes / 1024:.2f} KB"
    else:
        db_size = f"{db_size_bytes / (1024 * 1024):.2f} MB"
    
    return render_template('admin/analytics.html',
                          scan_by_day=json.dumps(scan_by_day),
                          user_by_day=json.dumps(user_by_day),
                          credit_by_day=json.dumps(credit_by_day),
                          avg_scan_time=avg_scan_time,
                          avg_api_time=avg_api_time,
                          db_size=db_size)

@admin_bp.route('/system-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    """
    Handle system settings updates.
    
    Returns:
        JSON response for API requests
        HTML template for web requests
    """
    if request.method == 'POST':
        # Handle system settings update
        flash('System settings updated successfully', 'success')
        return redirect(url_for('admin.system_settings'))
    
    # For now, just render a placeholder template
    return render_template('admin/system_settings.html')

@admin_bp.route('/export/<data_type>', methods=['GET'])
@login_required
@admin_required
def export_data(data_type):
    """
    Export data in CSV format.
    
    Supports:
    - Scans
    - Users
    - Documents
    - Matches
    
    Returns:
        CSV file
    """
    if data_type not in ['scans', 'users', 'documents', 'matches']:
        return jsonify({'error': 'Invalid data type'}), 400
        
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    if data_type == 'scans':
        data = db.session.query(
            ScanLog.id, ScanLog.user_id, User.username, 
            Document.title, ScanLog.created_at,
            DocumentMatch.ai_similarity_score, DocumentMatch.traditional_similarity_score
        ).join(User).join(Document).outerjoin(DocumentMatch).filter(
            ScanLog.created_at.between(start_date, end_date)
        ).all()
        
        df = pd.DataFrame(data, columns=[
            'Scan ID', 'User ID', 'Username', 'Document Title', 
            'Scan Date', 'AI Similarity', 'Traditional Similarity'
        ])
        
    elif data_type == 'users':
        data = db.session.query(
            User.id, User.username, User.email, User.role,
            User.credits, User.created_at, User.last_login
        ).filter(User.role == 'user').all()
        
        df = pd.DataFrame(data, columns=[
            'User ID', 'Username', 'Email', 'Role', 
            'Credits', 'Created At', 'Last Login'
        ])
        
    elif data_type == 'documents':
        data = db.session.query(
            Document.id, Document.title, Document.file_type,
            Document.file_size, Document.word_count, Document.language,
            User.username, Document.created_at
        ).join(User).filter(
            Document.created_at.between(start_date, end_date)
        ).all()
        
        df = pd.DataFrame(data, columns=[
            'Document ID', 'Title', 'File Type', 'File Size',
            'Word Count', 'Language', 'Owner', 'Created At'
        ])
        
    else:  # matches
        data = db.session.query(
            DocumentMatch.id, DocumentMatch.scan_id,
            Document.title.label('source_doc'),
            Document.title.label('matched_doc'),
            DocumentMatch.ai_similarity_score,
            DocumentMatch.traditional_similarity_score,
            DocumentMatch.match_type,
            DocumentMatch.created_at
        ).join(
            Document, DocumentMatch.document_id == Document.id
        ).filter(
            DocumentMatch.created_at.between(start_date, end_date)
        ).all()
        
        df = pd.DataFrame(data, columns=[
            'Match ID', 'Scan ID', 'Source Document',
            'Matched Document', 'AI Similarity', 'Traditional Similarity',
            'Match Type', 'Match Date'
        ])
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{data_type}_export_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@admin_bp.route('/help', methods=['GET'])
@login_required
@admin_required
def help():
    """
    Show help and documentation.
    
    Returns:
        HTML template
    """
    # For now, just render a placeholder template
    return render_template('admin/help.html')
