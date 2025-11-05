"""
Schedule management routes
"""
from flask import Blueprint, request, jsonify
from server.models.database import db

schedule_bp = Blueprint('schedule', __name__, url_prefix='/api')


@schedule_bp.route('/schedule', methods=['POST'])
def create_schedule():
    """Create schedule"""
    data = request.get_json()
    playlist_id = data.get('playlist_id')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    device_id = data.get('device_id')
    days_of_week = data.get('days_of_week')

    if not playlist_id or not start_time or not end_time:
        return jsonify({'error': 'Playlist ID, start time, and end time required'}), 400

    schedule_id = db.create_schedule(playlist_id, start_time, end_time, device_id, days_of_week)
    return jsonify({
        'success': True,
        'schedule': {
            'id': schedule_id,
            'playlist_id': playlist_id,
            'start_time': start_time,
            'end_time': end_time,
            'device_id': device_id
        }
    }), 201


@schedule_bp.route('/schedule/<int:device_id>', methods=['GET'])
def get_active_schedule(device_id):
    """Get active schedule for device"""
    schedule = db.get_active_schedule(device_id)
    if schedule:
        playlist = db.get_playlist(schedule['playlist_id'])
        schedule['playlist'] = playlist
    return jsonify({'schedule': schedule})

