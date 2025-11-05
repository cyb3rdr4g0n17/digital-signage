"""
Authentication routes
"""
from flask import Blueprint, request, jsonify, session
from server.models.database import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = db.authenticate_user(username, password)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username']
            }
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True})


@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session.get('username')
            }
        })
    return jsonify({'authenticated': False}), 401

