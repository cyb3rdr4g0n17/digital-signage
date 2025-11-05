"""
Configuration file for Digital Signage System
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DATABASE_PATH = os.path.join(BASE_DIR, 'digital_signage.db')

# File uploads
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'server', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'webm', 'html', 'txt'}

# Server settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', 5000))
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Player settings
PLAYER_CACHE_DIR = os.path.join(BASE_DIR, 'player', 'cache')
PLAYER_LOG_DIR = os.path.join(BASE_DIR, 'player', 'logs')
PLAYER_SYNC_INTERVAL = 30  # seconds
PLAYER_DEFAULT_DURATION = 5  # seconds for images

# Media settings
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLAYER_CACHE_DIR, exist_ok=True)
os.makedirs(PLAYER_LOG_DIR, exist_ok=True)

