"""
Playlist management routes
"""
from flask import Blueprint, request, jsonify
from server.models.database import db

playlist_bp = Blueprint('playlist', __name__, url_prefix='/api')


@playlist_bp.route('/playlist', methods=['POST'])
def create_playlist():
    """Create or update playlist"""
    data = request.get_json()
    name = data.get('name')
    items = data.get('items', [])

    if not name:
        return jsonify({'error': 'Playlist name required'}), 400

    playlist_id = data.get('id')
    if playlist_id:
        # Update existing playlist
        db.update_playlist(playlist_id, name=name, items=items)
        return jsonify({
            'success': True,
            'playlist': {
                'id': playlist_id,
                'name': name,
                'items': items
            }
        })
    else:
        # Create new playlist
        playlist_id = db.create_playlist(name, items)
        return jsonify({
            'success': True,
            'playlist': {
                'id': playlist_id,
                'name': name,
                'items': items
            }
        }), 201


@playlist_bp.route('/playlist', methods=['GET'])
def list_playlists():
    """List all playlists"""
    playlists = db.get_all_playlists()
    return jsonify({'playlists': playlists})


@playlist_bp.route('/playlist/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """Get playlist by ID"""
    playlist = db.get_playlist(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404
    return jsonify({'playlist': playlist})


@playlist_bp.route('/playlist/device/<int:device_id>', methods=['GET'])
def get_playlist_for_device(device_id):
    """Get playlist assigned to a device by ID"""
    device = db.get_device(device_id=device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404

    playlist_id = device.get('assigned_playlist_id')
    if not playlist_id:
        return jsonify({
            'playlist': {
                'id': None,
                'name': 'No Playlist',
                'items': [],
                'version': 0
            }
        })

    playlist = db.get_playlist(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    # Update device sync time
    db.update_device_sync(device_id)

    return jsonify({'playlist': playlist})


@playlist_bp.route('/playlist/device/uuid/<uuid>', methods=['GET'])
def get_playlist_for_device_uuid(uuid):
    """Get playlist assigned to a device by UUID"""
    device = db.get_device(uuid=uuid)
    if not device:
        # Device not registered yet, return empty playlist
        return jsonify({
            'playlist': {
                'id': None,
                'name': 'No Playlist',
                'items': [],
                'version': 0
            }
        })

    playlist_id = device.get('assigned_playlist_id')
    if not playlist_id:
        return jsonify({
            'playlist': {
                'id': None,
                'name': 'No Playlist',
                'items': [],
                'version': 0
            }
        })

    playlist = db.get_playlist(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    # Update device sync time
    db.update_device_sync(device['id'])

    return jsonify({'playlist': playlist})


@playlist_bp.route('/playlist/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    """Delete playlist"""
    playlist = db.get_playlist(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    # Note: In production, check if playlist is assigned to any device
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM playlists WHERE id = ?', (playlist_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

