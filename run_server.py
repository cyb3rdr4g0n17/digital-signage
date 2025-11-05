#!/usr/bin/env python3
"""
Simple script to run the Digital Signage server
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.app import app
from config import SERVER_HOST, SERVER_PORT, DEBUG

if __name__ == '__main__':
    print("=" * 60)
    print("Digital Signage Server")
    print("=" * 60)
    print(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")
    print(f"Admin Dashboard: http://{SERVER_HOST}:{SERVER_PORT}/admin")
    print(f"Player: http://{SERVER_HOST}:{SERVER_PORT}/player")
    print(f"Debug Mode: {DEBUG}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)

