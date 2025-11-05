"""
Digital Signage Server - Main Application
"""
from flask import Flask, render_template, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from config import SECRET_KEY, SERVER_HOST, SERVER_PORT, DEBUG, UPLOAD_FOLDER

# Import routes
from server.routes.auth import auth_bp
from server.routes.media import media_bp
from server.routes.playlist import playlist_bp
from server.routes.device import device_bp
from server.routes.schedule import schedule_bp
from server.routes.ticker import ticker_bp

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = SECRET_KEY
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(media_bp)
app.register_blueprint(playlist_bp)
app.register_blueprint(device_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(ticker_bp)


@app.route('/')
def index():
    """Redirect to admin dashboard"""
    return redirect(url_for('admin'))


@app.route('/admin')
def admin():
    """Admin dashboard"""
    return render_template('admin.html')


@app.route('/player')
def player():
    """Browser-based player"""
    return render_template('player.html')


@app.route('/uploads/<filename>')
def serve_uploads(filename):
    """Serve uploaded media files directly (without /api prefix)"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/playlist/<device_identifier>')
def get_device_playlist(device_identifier):
    """Get playlist for device (handles both ID and UUID)"""
    from flask import jsonify
    from server.models.database import db
    
    # Try to parse as integer first
    try:
        device_id = int(device_identifier)
        device = db.get_device(device_id=device_id)
    except ValueError:
        # Not an integer, treat as UUID
        device = db.get_device(uuid=device_identifier)
    
    if not device:
        # Device not found, return empty playlist
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

    db.update_device_sync(device['id'])
    return jsonify({'playlist': playlist})


if __name__ == '__main__':
    print(f"Starting Digital Signage Server on {SERVER_HOST}:{SERVER_PORT}")
    print(f"Admin Dashboard: http://{SERVER_HOST}:{SERVER_PORT}/admin")
    print(f"Player: http://{SERVER_HOST}:{SERVER_PORT}/player")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)

