# Digital Signage System - Python

A local digital signage platform built with Python that runs without internet, allowing you to upload media, create playlists, and play content on any screen (Raspberry Pi, Android TV, or PC).

## Features

- 🖥️ **Local/Offline Operation** - Runs entirely on local network
- 📤 **Media Management** - Upload images, videos, webpages, and text
- 📋 **Playlist Creation** - Create and manage playlists with timing controls
- 📱 **Multi-Device Support** - Manage multiple player devices
- 🔄 **Auto-Sync** - Automatic playlist synchronization and caching
- 🌐 **Web Admin Dashboard** - Easy-to-use web interface
- 📺 **Multiple Players** - Browser-based and Python GUI players

## Project Structure

```
digital-signage/
├── server/
│   ├── app.py              # Flask application
│   ├── routes/             # API route blueprints
│   │   ├── auth.py
│   │   ├── media.py
│   │   ├── playlist.py
│   │   ├── device.py
│   │   └── schedule.py
│   ├── models/
│   │   └── database.py     # Database models and operations
│   ├── templates/
│   │   ├── admin.html      # Admin dashboard
│   │   └── player.html     # Browser-based player
│   ├── static/             # Static files (CSS, JS)
│   └── uploads/            # Uploaded media files
├── player/
│   ├── player.py           # Python GUI player
│   ├── cache/              # Cached media files
│   └── logs/               # Player logs
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
└── README.md
```

## Installation

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 2. System Dependencies (for Raspberry Pi)

```bash
sudo apt update
sudo apt install python3-pip vlc ffmpeg chromium-browser
```

## Usage

### Starting the Server

```bash
python server/app.py
```

The server will start on `http://localhost:5000` by default.

- **Admin Dashboard**: http://localhost:5000/admin
- **Player**: http://localhost:5000/player

### Default Login

- **Username**: `admin`
- **Password**: `admin`

⚠️ **Change the default password in production!**

### Using the Python Player

```bash
python player/player.py --server http://192.168.1.100:5000 --device-id pi01
```

Options:
- `--server`: Server URL (default: http://localhost:5000)
- `--device-id`: Unique device identifier (required)
- `--device-name`: Device name (optional)

### Using the Browser Player

1. Open Chromium in kiosk mode:
   ```bash
   chromium-browser --kiosk http://<server-ip>:5000/player?device=pi01
   ```

2. Or open in any browser and the player will auto-register with a temporary device ID.

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/check-auth` - Check authentication status

### Media
- `POST /api/upload` - Upload media file
- `GET /api/media` - List all media
- `DELETE /api/media/<id>` - Delete media
- `GET /api/uploads/<filename>` - Serve media file

### Playlists
- `POST /api/playlist` - Create or update playlist
- `GET /api/playlist` - List all playlists
- `GET /api/playlist/<id>` - Get playlist by ID
- `GET /api/playlist/device/<device_id>` - Get playlist for device
- `DELETE /api/playlist/<id>` - Delete playlist

### Devices
- `POST /api/register` - Register new device
- `GET /api/devices` - List all devices
- `GET /api/device/<id>` - Get device by ID
- `POST /api/device/<id>/assign` - Assign playlist to device
- `DELETE /api/device/<id>` - Delete device

### Schedules
- `POST /api/schedule` - Create schedule
- `GET /api/schedule/<device_id>` - Get active schedule for device

## Configuration

Edit `config.py` to customize:

- Server host and port
- Upload folder location
- Cache directory
- Sync interval
- Default media duration
- Maximum upload size

## Database

The system uses SQLite database (`digital_signage.db`) that is automatically created on first run. Tables include:

- `users` - Admin users
- `media` - Uploaded media files
- `playlists` - Playlists with JSON items
- `schedule` - Playlist schedules
- `devices` - Registered player devices

## Player Features

### Offline Support
- Players cache playlists and media locally
- Automatic fallback to cached content when server is unavailable
- Periodic sync when connection is restored

### Media Types
- **Images**: PNG, JPG, JPEG, GIF
- **Videos**: MP4, AVI, MOV, WEBM
- **Webpages**: HTML files
- **Text**: TXT files

### Playback Control
- Configurable duration per item
- Automatic looping
- Fullscreen display
- Error handling and retry logic

## Deployment

### Systemd Service (Raspberry Pi)

Create `/etc/systemd/system/signage-server.service`:

```ini
[Unit]
Description=Digital Signage Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/digital-signage
ExecStart=/home/pi/digital-signage/venv/bin/python server/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/signage-player.service`:

```ini
[Unit]
Description=Digital Signage Player
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/digital-signage
ExecStart=/home/pi/digital-signage/venv/bin/python player/player.py --server http://localhost:5000 --device-id pi01
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl enable signage-server.service
sudo systemctl enable signage-player.service
sudo systemctl start signage-server
sudo systemctl start signage-player
```

## Troubleshooting

### Player won't connect to server
- Check server is running and accessible
- Verify device ID is correct
- Check firewall settings

### Media not displaying
- Verify file formats are supported
- Check file permissions
- Review player logs in `player/logs/player.log`

### Playlist not updating
- Check device is assigned a playlist in admin dashboard
- Verify device last sync time
- Check network connectivity

## License

This project is open source and available for modification and distribution.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

