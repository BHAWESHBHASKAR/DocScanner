import os
import json
import requests
from flask import Blueprint, request, jsonify, render_template, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from database.models import db, Document, ScanLog, DocumentMatch, User
import re
import math
from collections import Counter

document_bp = Blueprint('document', __name__, url_prefix='/document')

from ..utils.document_parser import DocumentParser

# Helper function to check if file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in DocumentParser.get_allowed_extensions()

# Helper function to get text similarity using OpenRouter API
def get_openrouter_similarity(text1, text2):
    try:
        headers = {
            "Authorization": f"Bearer {current_app.config['OPENROUTER_API_KEY']}",
            "HTTP-Referer": "http://localhost:5001",
            "Content-Type": "application/json"
        }
        
        # Create a clear prompt for similarity comparison
        prompt = f"""Compare the semantic similarity between these two texts and return a similarity score between 0 and 1.
- Score 1.0 means the texts are semantically identical or extremely similar
- Score 0.0 means the texts are completely different
- Score 0.7-0.9 means high similarity (same topic, similar content)
- Score 0.4-0.6 means moderate similarity (related topics)
- Score 0.1-0.3 means low similarity (few common elements)

Return ONLY the similarity score as a number between 0 and 1, no other text.

Text 1:
{text1[:1500]}

Text 2:
{text2[:1500]}

Similarity score:"""
        
        payload = {
            "model": current_app.config['OPENROUTER_MODEL'],
            "messages": [
                {"role": "system", "content": "You are an expert at semantic text comparison. Always return only a number between 0 and 1."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 10  # We only need a number
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            similarity_text = result['choices'][0]['message']['content'].strip()
            try:
                similarity = float(similarity_text)
                return min(max(similarity, 0), 1)  # Ensure it's between 0 and 1
            except ValueError:
                current_app.logger.error(f"OpenRouter returned non-numeric response: {similarity_text}")
                return None
        return None
    except Exception as e:
        current_app.logger.error(f"OpenRouter API error: {str(e)}")
        return None

# Helper function to get text similarity using Mistral API
def get_mistral_similarity(text1, text2):
    try:
        # First check if texts are identical or nearly identical
        if text1 == text2:
            return 1.0
            
        # Check if one text is completely contained in the other
        if text1 in text2 or text2 in text1:
            longer = max(len(text1), len(text2))
            shorter = min(len(text1), len(text2))
            if shorter / longer > 0.9:  # If the shorter text is >90% of the longer text
                return 0.95
        
        headers = {
            "Authorization": f"Bearer {current_app.config['MISTRAL_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        # Create a clear prompt for similarity comparison
        prompt = f"""Compare the semantic similarity between these two texts and return a similarity score between 0 and 1.
- Score 1.0 means the texts are semantically identical or extremely similar
- Score 0.0 means the texts are completely different
- Score 0.7-0.9 means high similarity (same topic, similar content)
- Score 0.4-0.6 means moderate similarity (related topics)
- Score 0.1-0.3 means low similarity (few common elements)

Return ONLY the similarity score as a number between 0 and 1, no other text.

Text 1:
{text1[:1500]}

Text 2:
{text2[:1500]}

Similarity score:"""
        
        payload = {
            "model": "mistral-small",  # Using a more powerful model for better similarity detection
            "messages": [
                {"role": "system", "content": "You are an expert at semantic text comparison. Always return only a number between 0 and 1."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 10  # We only need a number
        }
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            similarity_text = result['choices'][0]['message']['content'].strip()
            try:
                similarity = float(similarity_text)
                return min(max(similarity, 0), 1)  # Ensure it's between 0 and 1
            except ValueError:
                current_app.logger.error(f"Mistral returned non-numeric response: {similarity_text}")
                return None
        return None
    except Exception as e:
        current_app.logger.error(f"Mistral API error: {str(e)}")
        return None

# Helper function to get text similarity using traditional methods
def get_traditional_similarity(text1, text2):
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Create TF-IDF vectorizer with improved parameters
        vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents='unicode',
            analyzer='word',
            stop_words='english',
            token_pattern=r'\w{2,}',  # Words of at least 2 characters
            max_features=5000,  # Limit features to most common words
            ngram_range=(1, 2)  # Use both unigrams and bigrams
        )
        
        try:
            # Fit and transform the texts
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Normalize to [0, 1] range
            similarity = float(similarity)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            current_app.logger.error(f"TF-IDF calculation error: {str(e)}")
            
            # Fallback to simple word overlap if TF-IDF fails
            words1 = set(re.findall(r'\w+', text1.lower()))
            words2 = set(re.findall(r'\w+', text2.lower()))
            
            if not words1 and not words2:  # Both empty
                return 1.0
                
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0
            
    except Exception as e:
        current_app.logger.error(f"Traditional similarity error: {str(e)}")
        return 0.0

@document_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # Check if user has enough credits
        if current_user.credits <= 0:
            if request.content_type == 'application/json':
                return jsonify({'error': 'Not enough credits'}), 403
            flash('You do not have enough credits to scan a document', 'error')
            return redirect(url_for('credit.request_credits'))
        
        # Get file from request
        if request.content_type == 'application/json':
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
            file = request.files['file']
        else:
            if 'file' not in request.files:
                flash('No file part', 'error')
                return render_template('upload.html')
            file = request.files['file']
        
        # Check if file is empty
        if file.filename == '':
            if request.content_type == 'application/json':
                return jsonify({'error': 'No selected file'}), 400
            flash('No selected file', 'error')
            return render_template('upload.html')
        
        # Check if file is allowed
        if not allowed_file(file.filename):
            if request.content_type == 'application/json':
                return jsonify({'error': 'File type not allowed'}), 400
            supported_types = ', '.join(['.' + ext for ext in DocumentParser.get_allowed_extensions()])
            flash(f'File type not allowed. Supported file types: {supported_types}', 'error')
            return render_template('upload.html')
        
        try:
            # Get filename
            filename = secure_filename(file.filename)
            
            # Parse file content directly from the uploaded file
            file.seek(0)  # Reset file pointer to beginning
            content = DocumentParser.parse_file(file)
            
            # Calculate content hash for duplicate detection
            import hashlib
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            current_app.logger.info(f"Calculated content hash: {content_hash}")
            
            # Create document with content hash
            document = Document(
                title=filename,
                content=content,
                content_hash=content_hash,
                user_id=current_user.id
            )
            db.session.add(document)
            db.session.commit()
            current_app.logger.info(f"Document created with ID {document.id} and content hash {content_hash}")
            
            # Find similar documents
            all_documents = Document.query.filter(Document.id != document.id).all()
            current_app.logger.info(f"Found {len(all_documents)} other documents to compare with")
            
            matches = []
            scan_id = None  # Will be set when creating ScanLog
            
            for doc in all_documents:
                try:
                    # Check for exact duplicates using content hash
                    if doc.content_hash and doc.content_hash == content_hash:
                        similarity = 1.0
                        ai_score = 1.0
                        trad_score = 1.0
                        match_details = {'match_method': 'hash', 'exact_duplicate': True}
                        current_app.logger.info(f"Exact duplicate found! Document {document.id} matches {doc.id} by hash")
                    else:
                        # Use Mistral as primary similarity method
                        ai_score = get_mistral_similarity(content, doc.content)
                        
                        # Fall back to OpenRouter if Mistral fails
                        if ai_score is None:
                            ai_score = get_openrouter_similarity(content, doc.content)
                        
                        # Calculate traditional similarity score
                        trad_score = get_traditional_similarity(content, doc.content)
                        
                        # Use AI score if available, otherwise use traditional score
                        similarity = ai_score if ai_score is not None else trad_score
                        
                        # Create match details
                        match_details = {
                            'match_method': 'ai' if ai_score is not None else 'traditional',
                            'exact_duplicate': False,
                            'ai_method': 'mistral' if ai_score == similarity else 'openrouter' if ai_score is not None else None
                        }
                    
                    # Only consider documents with similarity above threshold (0.5 or 50%)
                    if similarity >= 0.5:
                        matches.append({
                            'document': doc,
                            'similarity': similarity,
                            'ai_score': ai_score,
                            'trad_score': trad_score,
                            'details': match_details
                        })
                        
                        # Create scan log if not already created
                        if scan_id is None:
                            scan_log = ScanLog(
                                user_id=current_user.id,
                                document_id=document.id,
                                matched_documents='[]',  # Will update after processing all matches
                                similarity_score=0  # Will update after processing all matches
                            )
                            db.session.add(scan_log)
                            db.session.commit()
                            scan_id = scan_log.id
                        
                        try:
                            # Create or update match record
                            match = DocumentMatch.create_or_update(
                                source_id=document.id,
                                matched_id=doc.id,
                                similarity_score=similarity,
                                ai_score=ai_score,
                                traditional_score=trad_score,
                                details=match_details
                            )
                            match.scan_id = scan_id  # Set the scan_id
                            db.session.add(match)
                            db.session.commit()
                            current_app.logger.info(f"Created/updated match between documents {document.id} and {doc.id} with score {similarity}")
                        except Exception as e:
                            current_app.logger.error(f"Error creating/updating match: {str(e)}")
                            db.session.rollback()
                            # Continue processing other matches
                            continue
                
                except Exception as e:
                    current_app.logger.error(f"Error processing match for document {doc.id}: {str(e)}")
                    # Continue processing other documents
                    continue
            
            # Sort matches by similarity (descending)
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Take top 5 matches for display
            top_matches = matches[:5]
            
            # Update scan log with match information
            if scan_id:
                try:
                    scan_log = ScanLog.query.get(scan_id)
                    matched_docs_json = json.dumps([{
                        'id': match['document'].id,
                        'title': match['document'].title,
                        'similarity': match['similarity']
                    } for match in top_matches])
                    
                    scan_log.matched_documents = matched_docs_json
                    scan_log.similarity_score = top_matches[0]['similarity'] if top_matches else 0
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Error updating scan log: {str(e)}")
            
            # Deduct credit
            current_user.credits -= 1
            db.session.commit()
            
            # Return success
            if request.content_type == 'application/json':
                return jsonify({
                    'message': 'Document uploaded successfully', 
                    'document_id': document.id,
                    'matches_count': len(matches)
                }), 200
            
            flash(f'Document uploaded successfully! Found {len(matches)} similar documents.', 'success')
            return redirect(url_for('document.view', doc_id=document.id))
            
        except Exception as e:
            current_app.logger.error(f"Error processing document: {str(e)}")
            if request.content_type == 'application/json':
                return jsonify({'error': 'Error processing document'}), 500
            flash('Error processing document. Please try again.', 'error')
            return render_template('upload.html')
    
    return render_template('upload.html')

@document_bp.route('/view/<int:doc_id>', methods=['GET'])
@login_required
def view(doc_id):
    document = Document.query.get_or_404(doc_id)
    
    # Check if user is owner or admin
    if document.user_id != current_user.id and current_user.role != 'admin':
        if request.content_type == 'application/json':
            return jsonify({'error': 'Unauthorized'}), 403
        flash('You do not have permission to view this document', 'error')
        return redirect(url_for('index'))
    
    # Get matches (both as source and as matched document)
    from sqlalchemy import or_
    matches = DocumentMatch.query.filter(
        or_(
            DocumentMatch.source_document_id == doc_id,
            DocumentMatch.matched_document_id == doc_id
        )
    ).order_by(DocumentMatch.similarity_score.desc()).all()
    
    # Process matches to ensure the correct document is shown
    processed_matches = []
    for match in matches:
        if match.source_document_id == doc_id:
            match.matched_document = Document.query.get(match.matched_document_id)
            processed_matches.append(match)
        else:
            # Create a temporary match object with swapped document references
            temp_match = DocumentMatch(
                source_document_id=match.matched_document_id,
                matched_document_id=match.source_document_id,
                similarity_score=match.similarity_score,
                ai_similarity_score=match.ai_similarity_score,
                traditional_similarity_score=match.traditional_similarity_score,
                match_type=match.match_type,
                match_details=match.match_details,
                created_at=match.created_at,
                updated_at=match.updated_at
            )
            temp_match.matched_document = Document.query.get(match.source_document_id)
            processed_matches.append(temp_match)
    
    # Sort by similarity score
    processed_matches.sort(key=lambda x: x.similarity_score, reverse=True)
    matches = processed_matches
    
    if request.content_type == 'application/json':
        return jsonify({
            'document': document.to_dict(),
            'matches': [{
                'document': Document.query.get(match.matched_document_id).to_dict(),
                'similarity': match.similarity_score
            } for match in matches]
        }), 200
    
    return render_template('view_document.html', document=document, matches=matches)

@document_bp.route('/matches/<int:doc_id>', methods=['GET'])
@login_required
def matches(doc_id):
    document = Document.query.get_or_404(doc_id)
    
    # Check if user is owner or admin
    if document.user_id != current_user.id and current_user.role != 'admin':
        if request.content_type == 'application/json':
            return jsonify({'error': 'Unauthorized'}), 403
        flash('You do not have permission to view matches for this document', 'error')
        return redirect(url_for('index'))
    
    # Get matches (both as source and as matched document)
    from sqlalchemy import or_
    matches = DocumentMatch.query.filter(
        or_(
            DocumentMatch.source_document_id == doc_id,
            DocumentMatch.matched_document_id == doc_id
        )
    ).order_by(DocumentMatch.similarity_score.desc()).all()
    
    # Process matches to ensure the correct document is shown
    processed_matches = []
    for match in matches:
        if match.source_document_id == doc_id:
            match.matched_document = Document.query.get(match.matched_document_id)
            processed_matches.append(match)
        else:
            # Create a temporary match object with swapped document references
            temp_match = DocumentMatch(
                source_document_id=match.matched_document_id,
                matched_document_id=match.source_document_id,
                similarity_score=match.similarity_score,
                ai_similarity_score=match.ai_similarity_score,
                traditional_similarity_score=match.traditional_similarity_score,
                match_type=match.match_type,
                match_details=match.match_details,
                created_at=match.created_at,
                updated_at=match.updated_at
            )
            temp_match.matched_document = Document.query.get(match.source_document_id)
            processed_matches.append(temp_match)
    
    # Sort by similarity score
    processed_matches.sort(key=lambda x: x.similarity_score, reverse=True)
    matches = processed_matches
    
    if request.content_type == 'application/json':
        return jsonify({
            'matches': [{
                'document': Document.query.get(match.matched_document_id).to_dict(),
                'similarity': match.similarity_score
            } for match in matches]
        }), 200
    
    return render_template('matches.html', document=document, matches=matches)
