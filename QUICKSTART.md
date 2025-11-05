# Quick Start Guide

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. **Clone or download this project**

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

1. **Start the server**:
   ```bash
   python run_server.py
   ```
   Or:
   ```bash
   python server/app.py
   ```

2. **Open your browser**:
   - Admin Dashboard: http://localhost:5000/admin
   - Default login: `admin` / `admin`

## Using the Player

### Option 1: Browser Player (Easiest)

1. Open in any browser:
   ```
   http://localhost:5000/player?device=pi01
   ```
   The player will auto-register with the server.

2. For kiosk mode (Raspberry Pi):
   ```bash
   chromium-browser --kiosk http://localhost:5000/player?device=pi01
   ```

### Option 2: Python GUI Player

1. **Install additional dependencies** (if not already installed):
   ```bash
   pip install PyQt5 python-vlc Pillow
   ```

2. **Run the player**:
   ```bash
   python player/player.py --server http://localhost:5000 --device-id pi01
   ```

## First Steps

1. **Login to Admin Dashboard**
   - URL: http://localhost:5000/admin
   - Username: `admin`
   - Password: `admin`

2. **Upload Media**
   - Go to "Media" tab
   - Click "Choose File" and select an image or video
   - Click "Upload"

3. **Create a Playlist**
   - Go to "Playlists" tab
   - Click "Create Playlist"
   - Enter a name
   - Select media from dropdown and add to playlist
   - Set duration for each item
   - Click "Save Playlist"

4. **Assign Playlist to Device**
   - Go to "Devices" tab
   - Find your device (or it will appear when player connects)
   - Select a playlist from the dropdown
   - The player will automatically update

5. **View Player**
   - Open http://localhost:5000/player?device=pi01
   - Your playlist should start playing automatically

## Troubleshooting

### Server won't start
- Check if port 5000 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Player shows "Waiting for playlist..."
- Make sure you've created a playlist in the admin dashboard
- Assign the playlist to your device in the Devices tab
- Check browser console for errors

### Media won't upload
- Check file size (max 100MB by default)
- Verify file type is supported (images, videos, HTML, text)
- Check server logs for errors

## Next Steps

- Change the default admin password
- Configure the server (edit `config.py`)
- Set up systemd services for auto-start (see README.md)
- Add more media and create multiple playlists

## Support

For more information, see the full README.md file.

