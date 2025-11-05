"""
Media management routes
"""
import os
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
from server.models.database import db

media_bp = Blueprint('media', __name__, url_prefix='/api')


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filename):
    """Determine file type from extension"""
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['png', 'jpg', 'jpeg', 'gif']:
        return 'image'
    elif ext in ['mp4', 'avi', 'mov', 'webm']:
        return 'video'
    elif ext == 'html':
        return 'webpage'
    elif ext == 'txt':
        return 'text'
    return 'unknown'


@media_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload media file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    if file.content_length and file.content_length > MAX_UPLOAD_SIZE:
        return jsonify({'error': 'File too large'}), 400

    filename = secure_filename(file.filename)
    # Add timestamp to avoid collisions
    import time
    timestamp = int(time.time())
    name, ext = os.path.splitext(filename)
    filename = f"{name}_{timestamp}{ext}"

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    filetype = get_file_type(filename)
    size = os.path.getsize(filepath)

    # Add to database
    media_id = db.add_media(filename, filetype, f"/uploads/{filename}", size=size)

    return jsonify({
        'success': True,
        'media': {
            'id': media_id,
            'filename': filename,
            'filetype': filetype,
            'path': f"/uploads/{filename}",
            'size': size
        }
    })


@media_bp.route('/media', methods=['GET'])
def list_media():
    """List all media"""
    media_list = db.get_media()
    return jsonify({'media': media_list})


@media_bp.route('/media/<int:media_id>', methods=['DELETE'])
def delete_media(media_id):
    """Delete media"""
    media = db.get_media(media_id)
    if not media:
        return jsonify({'error': 'Media not found'}), 404

    # Delete file
    filepath = os.path.join(UPLOAD_FOLDER, media['filename'])
    if os.path.exists(filepath):
        os.remove(filepath)

    # Delete from database
    db.delete_media(media_id)
    return jsonify({'success': True})


@media_bp.route('/uploads/<filename>', methods=['GET'])
def serve_media(filename):
    """Serve uploaded media files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

