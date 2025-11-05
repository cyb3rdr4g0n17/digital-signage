"""
Ticker management routes
"""
from flask import Blueprint, request, jsonify
from server.models.database import db

ticker_bp = Blueprint('ticker', __name__, url_prefix='/api')


@ticker_bp.route('/ticker', methods=['POST'])
def create_ticker():
    """Create new ticker"""
    data = request.get_json()
    name = data.get('name')
    text = data.get('text')
    
    if not name or not text:
        return jsonify({'error': 'Name and text required'}), 400

    ticker_id = db.create_ticker(
        name=name,
        text=text,
        speed=data.get('speed', 50),
        font_size=data.get('font_size', 24),
        font_color=data.get('font_color', '#FFFFFF'),
        background_color=data.get('background_color', '#000000'),
        position=data.get('position', 'bottom'),
        device_id=data.get('device_id')
    )

    return jsonify({
        'success': True,
        'ticker': {
            'id': ticker_id,
            'name': name,
            'text': text
        }
    }), 201


@ticker_bp.route('/ticker', methods=['GET'])
def list_tickers():
    """List all tickers"""
    tickers = db.get_all_tickers()
    return jsonify({'tickers': tickers})


@ticker_bp.route('/ticker/<int:ticker_id>', methods=['GET'])
def get_ticker(ticker_id):
    """Get ticker by ID"""
    ticker = db.get_ticker(ticker_id)
    if not ticker:
        return jsonify({'error': 'Ticker not found'}), 404
    return jsonify({'ticker': ticker})


@ticker_bp.route('/ticker/<int:ticker_id>', methods=['PUT'])
def update_ticker(ticker_id):
    """Update ticker"""
    data = request.get_json()
    ticker = db.get_ticker(ticker_id)
    
    if not ticker:
        return jsonify({'error': 'Ticker not found'}), 404

    # Build update dict
    updates = {}
    for key in ['name', 'text', 'speed', 'font_size', 'font_color', 
                'background_color', 'position', 'is_active', 'device_id']:
        if key in data:
            updates[key] = data[key]

    db.update_ticker(ticker_id, **updates)
    return jsonify({'success': True, 'ticker': db.get_ticker(ticker_id)})


@ticker_bp.route('/ticker/<int:ticker_id>', methods=['DELETE'])
def delete_ticker(ticker_id):
    """Delete ticker"""
    ticker = db.get_ticker(ticker_id)
    if not ticker:
        return jsonify({'error': 'Ticker not found'}), 404

    db.delete_ticker(ticker_id)
    return jsonify({'success': True})


@ticker_bp.route('/ticker/device/<int:device_id>', methods=['GET'])
def get_device_ticker(device_id):
    """Get active ticker for device"""
    ticker = db.get_active_ticker_for_device(device_id)
    return jsonify({'ticker': ticker})

