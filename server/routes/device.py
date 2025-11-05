"""
Device management routes
"""
from flask import Blueprint, request, jsonify
from server.models.database import db

device_bp = Blueprint('device', __name__, url_prefix='/api')


@device_bp.route('/register', methods=['POST'])
def register_device():
    """Register new player device"""
    data = request.get_json()
    name = data.get('name')
    uuid = data.get('uuid')
    ip_address = request.remote_addr

    if not name or not uuid:
        return jsonify({'error': 'Device name and UUID required'}), 400

    device_id, token = db.register_device(name, uuid, ip_address)

    return jsonify({
        'success': True,
        'device': {
            'id': device_id,
            'name': name,
            'uuid': uuid,
            'token': token
        }
    }), 201


@device_bp.route('/devices', methods=['GET'])
def list_devices():
    """List all devices"""
    devices = db.get_all_devices()
    return jsonify({'devices': devices})


@device_bp.route('/device/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """Get device by ID"""
    device = db.get_device(device_id=device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    return jsonify({'device': device})


@device_bp.route('/device/<int:device_id>/assign', methods=['POST'])
def assign_playlist(device_id):
    """Assign playlist to device"""
    data = request.get_json()
    playlist_id = data.get('playlist_id')

    device = db.get_device(device_id=device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404

    if playlist_id:
        playlist = db.get_playlist(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404

    db.assign_playlist_to_device(device_id, playlist_id)
    return jsonify({'success': True})


@device_bp.route('/device/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Delete device"""
    device = db.get_device(device_id=device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM devices WHERE id = ?', (device_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

