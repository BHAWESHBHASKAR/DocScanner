"""
Database Models for Document Scanner Application

This module defines the SQLAlchemy models that represent the database schema for the
Document Scanner application. The models include:

- User: Manages user accounts and authentication
- Document: Stores uploaded documents and their metadata
- CreditRequest: Handles credit request workflow
- ScanLog: Tracks document scanning activity
- DocumentMatch: Records similarity matches between documents

Each model includes relationships, utility methods, and serialization support.

Author: Bhawesh Bhaskar
Date: March 2025
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    """
    User model for authentication and credit management.
    
    Each user starts with 20 free credits daily and can request more from admins.
    Users can be either regular users or administrators.
    """
    __tablename__ = 'users'
    
    # Basic user information
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # User role and status
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    
    # Credit management
    credits = db.Column(db.Integer, default=20)
    total_credits_granted = db.Column(db.Integer, default=20)
    last_credit_reset = db.Column(db.DateTime, default=datetime.now)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, default=datetime.now)
    
    # Flask-Login integration
    is_authenticated = True
    is_anonymous = False
    
    # Relationships
    documents = db.relationship('Document', backref='owner', lazy=True)
    credit_requests = db.relationship('CreditRequest', 
                                    foreign_keys='CreditRequest.user_id',
                                    backref='requester', 
                                    lazy=True)
    scan_logs = db.relationship('ScanLog', backref='user', lazy=True)
    
    def get_id(self):
        """Required by Flask-Login."""
        return str(self.id)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary for API responses."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'credits': self.credits,
            'total_credits_granted': self.total_credits_granted,
            'credits_used': self.total_credits_granted - self.credits,
            'last_credit_reset': self.last_credit_reset.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }


class Document(db.Model):
    """
    Document model for storing uploaded text documents.
    
    Includes metadata for efficient searching and similarity matching.
    Supports various file types and maintains content vectors for AI matching.
    """
    __tablename__ = 'documents'
    
    # Basic document information
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Document metadata
    content_hash = db.Column(db.String(64))  # SHA-256 hash for duplicate detection
    content_vector = db.Column(db.Text)      # TF-IDF vector for similarity
    file_type = db.Column(db.String(10), default='txt')
    file_size = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer)
    language = db.Column(db.String(10))
    
    # Ownership and timestamps
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships for document matching
    matches_as_source = db.relationship('DocumentMatch', 
                                      foreign_keys='DocumentMatch.source_document_id',
                                      backref='source_document',
                                      lazy='dynamic')
    matches_as_target = db.relationship('DocumentMatch', 
                                      foreign_keys='DocumentMatch.matched_document_id',
                                      backref='matched_document',
                                      lazy='dynamic')
    
    def get_similar_documents(self, min_score=0.7, limit=10):
        """
        Find similar documents based on stored matches.
        
        Args:
            min_score (float): Minimum similarity score (0-1)
            limit (int): Maximum number of results
            
        Returns:
            list: Tuples of (document, similarity_score)
        """
        from sqlalchemy import or_
        
        matches = DocumentMatch.query.filter(
            or_(
                DocumentMatch.source_document_id == self.id,
                DocumentMatch.matched_document_id == self.id
            ),
            DocumentMatch.similarity_score >= min_score
        ).order_by(DocumentMatch.similarity_score.desc()).limit(limit).all()
        
        similar_docs = []
        for match in matches:
            if match.source_document_id == self.id:
                similar_docs.append((match.matched_document, match.similarity_score))
            else:
                similar_docs.append((match.source_document, match.similarity_score))
        
        return similar_docs
    
    def to_dict(self, include_content=False):
        """
        Convert document to dictionary for API responses.
        
        Args:
            include_content (bool): Whether to include full document content
        """
        data = {
            'id': self.id,
            'title': self.title,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'word_count': self.word_count,
            'language': self.language,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_content:
            data['content'] = self.content
        else:
            # Show preview for long documents
            data['content'] = self.content[:200] + '...' if len(self.content) > 200 else self.content
        
        return data


class CreditRequest(db.Model):
    """
    Credit request model for managing user credit allocations.
    
    Users can request additional credits when they run out of their daily limit.
    Admins can approve or deny these requests.
    """
    __tablename__ = 'credit_requests'
    
    # Request details
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending/approved/denied
    
    # Admin approval
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship to admin user
    admin = db.relationship('User', foreign_keys=[admin_id], backref='approved_requests')
    
    def to_dict(self):
        """Convert request to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'reason': self.reason,
            'status': self.status,
            'admin_id': self.admin_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ScanLog(db.Model):
    """
    Scan log model for tracking document scanning activity.
    
    Records each scan operation, including settings and results.
    Supports different scan types and stores match results.
    """
    __tablename__ = 'scan_logs'
    
    # Scan information
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    scan_type = db.Column(db.String(20), default='standard')  # standard/deep/quick
    
    # Scan results
    scan_metadata = db.Column(db.Text)  # JSON with scan settings
    matched_documents = db.Column(db.Text)  # JSON list of matches
    similarity_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    document = db.relationship('Document', backref='scans')
    matches = db.relationship('DocumentMatch', backref='scan', lazy='dynamic')
    
    def to_dict(self):
        """Convert scan log to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'document_id': self.document_id,
            'document_title': self.document.title,
            'scan_type': self.scan_type,
            'scan_metadata': json.loads(self.scan_metadata) if self.scan_metadata else None,
            'matched_documents': json.loads(self.matched_documents) if self.matched_documents else [],
            'similarity_score': self.similarity_score,
            'matches_count': self.matches.count(),
            'created_at': self.created_at.isoformat()
        }


class DocumentMatch(db.Model):
    """
    Document match model for storing similarity results.
    
    Records both AI-based and traditional similarity scores between documents.
    Includes detailed match information and prevents duplicate matches.
    """
    __tablename__ = 'document_matches'
    
    # Match identification
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan_logs.id'), nullable=False)
    source_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    matched_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    
    # Similarity scores
    similarity_score = db.Column(db.Float, nullable=False)  # Overall score
    ai_similarity_score = db.Column(db.Float)  # AI model score
    traditional_similarity_score = db.Column(db.Float)  # TF-IDF score
    
    # Match details
    match_type = db.Column(db.String(20), default='low')  # exact/high/medium/low
    match_details = db.Column(db.Text)  # JSON with match details
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Prevent duplicate matches
    __table_args__ = (
        db.UniqueConstraint('source_document_id', 'matched_document_id',
                           name='unique_document_match'),
    )
    
    @classmethod
    def create_or_update(cls, source_id, matched_id, similarity_score, ai_score=None, traditional_score=None, details=None):
        """
        Create or update a document match.
        
        Args:
            source_id (int): ID of the source document
            matched_id (int): ID of the matched document
            similarity_score (float): Overall similarity score
            ai_score (float, optional): AI-based similarity score
            traditional_score (float, optional): Traditional similarity score
            details (dict, optional): Additional match details
            
        Returns:
            DocumentMatch: Created or updated match object
        """
        try:
            # Try to find existing match
            match = cls.query.filter_by(
                source_document_id=source_id,
                matched_document_id=matched_id
            ).first()
            
            if match:
                # Update existing match
                match.similarity_score = similarity_score
                match.ai_similarity_score = ai_score
                match.traditional_similarity_score = traditional_score
                match.match_details = json.dumps(details) if details else None
                match.updated_at = datetime.now()
            else:
                # Create new match
                match = cls(
                    source_document_id=source_id,
                    matched_document_id=matched_id,
                    similarity_score=similarity_score,
                    ai_similarity_score=ai_score,
                    traditional_similarity_score=traditional_score,
                    match_details=json.dumps(details) if details else None,
                    match_type='exact' if similarity_score >= 0.95 else 'high' if similarity_score >= 0.7 else 'medium' if similarity_score >= 0.5 else 'low'
                )
            
            return match
            
        except Exception as e:
            current_app.logger.error(f"Error creating/updating document match: {str(e)}")
            raise
    
    def to_dict(self):
        """Convert match to dictionary for API responses."""
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'source_document_id': self.source_document_id,
            'matched_document_id': self.matched_document_id,
            'similarity_score': self.similarity_score,
            'ai_similarity_score': self.ai_similarity_score,
            'traditional_similarity_score': self.traditional_similarity_score,
            'match_type': self.match_type,
            'match_details': json.loads(self.match_details) if self.match_details else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
