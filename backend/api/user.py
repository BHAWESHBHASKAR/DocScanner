from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from database.models import db, User, Document, ScanLog, CreditRequest

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    if request.content_type == 'application/json':
        return jsonify({
            'user': current_user.to_dict(),
            'documents': [doc.to_dict() for doc in current_user.documents],
            'scan_logs': [log.to_dict() for log in current_user.scan_logs],
            'credit_requests': [req.to_dict() for req in current_user.credit_requests]
        }), 200
    
    return render_template('profile.html', 
                          user=current_user,
                          documents=current_user.documents,
                          scan_logs=current_user.scan_logs,
                          credit_requests=current_user.credit_requests)

@user_bp.route('/activity', methods=['GET'])
@login_required
def activity():
    # Get user's recent activity
    recent_scans = ScanLog.query.filter_by(user_id=current_user.id).order_by(ScanLog.created_at.desc()).limit(10).all()
    recent_documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.created_at.desc()).limit(10).all()
    recent_requests = CreditRequest.query.filter_by(user_id=current_user.id).order_by(CreditRequest.created_at.desc()).limit(10).all()
    
    if request.content_type == 'application/json':
        return jsonify({
            'recent_scans': [scan.to_dict() for scan in recent_scans],
            'recent_documents': [doc.to_dict() for doc in recent_documents],
            'recent_requests': [req.to_dict() for req in recent_requests]
        }), 200
    
    return render_template('activity.html',
                          recent_scans=recent_scans,
                          recent_documents=recent_documents,
                          recent_requests=recent_requests)

@user_bp.route('/export-history', methods=['GET'])
@login_required
def export_history():
    # Get user's scan history
    scan_logs = ScanLog.query.filter_by(user_id=current_user.id).order_by(ScanLog.created_at.desc()).all()
    
    # Format scan history as text
    history_text = f"Scan History for {current_user.username}\n"
    history_text += "=" * 50 + "\n\n"
    
    for log in scan_logs:
        document = Document.query.get(log.document_id)
        history_text += f"Date: {log.created_at}\n"
        history_text += f"Document: {document.title}\n"
        history_text += f"Similarity Score: {log.similarity_score}\n"
        history_text += f"Matched Documents: {log.matched_documents}\n"
        history_text += "-" * 50 + "\n\n"
    
    # Return as downloadable text file
    return history_text, 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': 'attachment; filename=scan_history.txt'
    }
