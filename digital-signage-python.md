🐍 DIGITAL SIGNAGE SYSTEM — PYTHON DEVELOPMENT PLAN
🎯 PROJECT GOAL

Develop a local digital signage platform using Python that:

Runs without internet (local LAN or offline)

Lets admin upload media, create playlists, and set schedules

Plays content (images/videos/text/webpages) on any screen (Raspberry Pi, Android TV, or PC)

Supports offline playback with automatic syncing and caching

🧩 SYSTEM OVERVIEW
Component	Description	Technology
Backend Server	REST API for content management & device control	Python (Flask or FastAPI)
Database	Stores users, playlists, schedules, and devices	SQLite (local)
Storage	Local folder for uploaded media	/uploads directory
Admin Dashboard	Web-based UI for managing playlists	HTML/CSS/JS or React frontend
Player Application	Runs on Raspberry Pi / PC / Android TV	Python + PyQt5 / VLC / Chromium kiosk
Sync Layer	Keeps playlists synced between server and players	HTTP (REST) + JSON cache
⚙️ PHASE 1 — PROJECT SETUP & DESIGN (2 days)
Tasks

Select Framework:
Use Flask for simplicity and speed, or FastAPI if you need async.

Define Data Models:

users: id, username, password

media: id, filename, filetype, path

playlists: id, name, json_items, created_at

schedule: id, playlist_id, start_time, end_time

devices: id, name, uuid, assigned_playlist, last_sync

Create Folder Structure:

digital_signage/
├── server/
│   ├── app.py
│   ├── routes/
│   ├── models/
│   ├── templates/
│   ├── static/
│   └── uploads/
├── player/
│   ├── player.py
│   └── cache/
├── config.py
├── requirements.txt
└── docs/
    └── DEVELOPMENT_PLAN_PYTHON.md


Initialize Git & Virtual Environment:

python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors requests python-vlc pillow

🧠 PHASE 2 — BACKEND DEVELOPMENT (5 days)
Objectives

Implement REST APIs for uploads, playlists, and device sync.

Store uploaded files locally and metadata in SQLite.

Key Endpoints
Method	Route	Description
POST	/api/login	User authentication
POST	/api/upload	Upload image/video file
GET	/api/media	List all media
POST	/api/playlist	Create or update playlist
GET	/api/playlist/:deviceId	Get playlist for a device
GET	/api/schedule/:deviceId	Get active schedule
POST	/api/register	Register new player device
Implementation Tasks

Set up Flask app with Blueprints for modular routes.

Integrate SQLite3 with a helper module for CRUD operations.

Implement file uploads using Flask-Uploads or werkzeug’s file handler.

Serve media files via /uploads/<filename> route.

Create a simple HTML admin dashboard (Bootstrap-based).

💻 PHASE 3 — ADMIN DASHBOARD (5 days)
Features

Login screen (basic authentication)

Upload media (image/video)

Create and edit playlists (add, remove media items)

Schedule playlists (select time ranges)

Device management (view online/offline status)

Implementation

Use Flask templates (Jinja2) or a lightweight React frontend.

Integrate Axios or fetch() to call REST APIs.

Include a “Preview” page that loads /player.html and shows how content rotates.

📺 PHASE 4 — PLAYER APPLICATION (5 days)
Option A — Python GUI Player (Raspberry Pi / PC)

Use PyQt5 or Tkinter with VLC for video playback and Pillow for images.

Key Features:

Fetch playlist JSON via /api/playlist/:deviceId

Cache media locally (/player/cache)

Play image → delay → play next item → loop

Play videos using VLC or OMXPlayer

Fullscreen display (no window borders)

Example Loop (Pseudo-code):

import requests, time, vlc, os
SERVER = "http://192.168.1.100:5000"
CACHE = "cache/"

while True:
    playlist = requests.get(f"{SERVER}/api/playlist/pi01").json()
    for item in playlist['items']:
        path = CACHE + item['url'].split('/')[-1]
        if not os.path.exists(path):
            open(path, 'wb').write(requests.get(SERVER + item['url']).content)
        if item['type'] == 'image':
            # Display using Pillow or OpenCV
            pass
        elif item['type'] == 'video':
            vlc.MediaPlayer(path).play()
            time.sleep(item['duration'])

Option B — Browser Player (Android TV / Raspberry Pi)

Serve a /player.html that uses JavaScript to fetch playlist and rotate media.

Launch Chromium in kiosk mode:

chromium-browser --kiosk http://<server-ip>:5000/player

🔄 PHASE 5 — SYNC & OFFLINE LOGIC (3 days)
Tasks

Player fetches playlist every X seconds.

Compare version → download new assets if changed.

Maintain playlist.json and cache/ folder locally.

If no connection → load cached playlist.

Log playback events locally for analytics.

🔐 PHASE 6 — DEVICE MANAGEMENT & SECURITY (2 days)
Features

Device registration via /api/register

Server tracks each device’s UUID, IP, and last_seen

Assign playlist per device

Simple token-based authentication for API access

Basic HTTPS support (self-signed certificate optional)

🧪 PHASE 7 — TESTING & DEPLOYMENT (3 days)
On Raspberry Pi:

Install dependencies:

sudo apt update
sudo apt install python3-pip vlc ffmpeg chromium-browser
pip3 install flask requests python-vlc pillow


Run the server:

python3 server/app.py


Run the player:

python3 player/player.py


Autostart on boot:
Create a systemd service for each process:

signage-server.service

signage-player.service

Testing Checklist

Upload and display various media formats (JPG, PNG, MP4)

Verify playlist timing accuracy

Test offline playback (server down → local cache)

Test device re-registration and playlist switching

Reboot and confirm auto-start works

🚀 PHASE 8 — FUTURE ENHANCEMENTS (Optional)

WebSocket or MQTT live updates (real-time sync)

Multi-user roles (Admin, Editor)

Analytics dashboard (play count, uptime, active devices)

Multi-screen layouts (zones for video, text, ticker)

Remote screenshots or heartbeat pings

Cloud sync or remote management (optional)

🧱 PROJECT STRUCTURE (Final Layout)
digital_signage/
├── server/
│   ├── app.py
│   ├── routes/
│   ├── models/
│   ├── static/
│   ├── templates/
│   └── uploads/
├── player/
│   ├── player.py
│   ├── cache/
│   └── logs/
├── config.py
├── requirements.txt
└── docs/
    └── DEVELOPMENT_PLAN_PYTHON.md

⏱ PROJECT TIMELINE
Phase	Description	Duration
1	Setup & Architecture	2 days
2	Backend APIs	5 days
3	Admin Dashboard	5 days
4	Player Application	5 days
5	Sync & Offline Logic	3 days
6	Device Management & Security	2 days
7	Testing & Deployment	3 days
Total	Full System Delivery	~25 days (3–4 weeks)
✅ SUMMARY

This plan builds a Python-based digital signage system from scratch, focused on:

Local/offline reliability

Simplicity and modular design

Full control over player behavior and scheduling

Once complete, this system can run entirely on Raspberry Pi, PC, or Android TV — no internet required.