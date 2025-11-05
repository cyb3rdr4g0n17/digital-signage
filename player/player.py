"""
Digital Signage Player Application
Runs on Raspberry Pi, PC, or Android TV
"""
import os
import sys
import time
import requests
import json
import logging
from pathlib import Path

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False
    print("Warning: python-vlc not available. Video playback will be limited.")

try:
    from PIL import Image
    from PIL import ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow not available. Image display will be limited.")

try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("Warning: tkinter not available. Using fallback display.")

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PLAYER_CACHE_DIR, PLAYER_LOG_DIR, PLAYER_SYNC_INTERVAL, PLAYER_DEFAULT_DURATION

# Setup logging
os.makedirs(PLAYER_LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(PLAYER_LOG_DIR, 'player.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DigitalSignagePlayer:
    def __init__(self, server_url, device_id, device_name=None):
        self.server_url = server_url.rstrip('/')
        self.device_id = device_id
        self.device_name = device_name or f"Player-{device_id}"
        self.cache_dir = PLAYER_CACHE_DIR
        self.playlist_cache = os.path.join(self.cache_dir, 'playlist.json')
        self.current_playlist = None
        self.current_index = 0
        self.playlist_version = 0
        self.vlc_instance = None
        self.vlc_player = None

        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)

        # Initialize VLC if available
        if VLC_AVAILABLE:
            self.vlc_instance = vlc.Instance(['--no-xlib', '--quiet'])
            self.vlc_player = self.vlc_instance.media_player_new()

        # Initialize GUI if available
        self.root = None
        self.canvas = None
        if TKINTER_AVAILABLE:
            self.setup_gui()

        # Register device
        self.register_device()

        # Load cached playlist
        self.load_cached_playlist()

    def setup_gui(self):
        """Setup Tkinter GUI for fullscreen display"""
        self.root = tk.Tk()
        self.root.title("Digital Signage Player")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())

        self.canvas = tk.Canvas(
            self.root,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.root:
            self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def register_device(self):
        """Register device with server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/register",
                json={
                    'name': self.device_name,
                    'uuid': self.device_id
                },
                timeout=5
            )
            if response.status_code == 201:
                logging.info(f"Device registered: {self.device_id}")
            else:
                logging.warning(f"Device registration returned: {response.status_code}")
        except Exception as e:
            logging.warning(f"Could not register device: {e}")

    def fetch_playlist(self):
        """Fetch playlist from server"""
        try:
            response = requests.get(
                f"{self.server_url}/api/playlist/device/{self.device_id}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                playlist = data.get('playlist')
                if playlist and playlist.get('version') != self.playlist_version:
                    self.current_playlist = playlist
                    self.playlist_version = playlist.get('version', 0)
                    self.current_index = 0
                    self.save_cached_playlist()
                    logging.info(f"Playlist updated: {playlist.get('name')}")
                    return True
        except Exception as e:
            logging.warning(f"Could not fetch playlist: {e}")
        return False

    def load_cached_playlist(self):
        """Load playlist from cache"""
        try:
            if os.path.exists(self.playlist_cache):
                with open(self.playlist_cache, 'r') as f:
                    data = json.load(f)
                    self.current_playlist = data.get('playlist')
                    self.playlist_version = data.get('version', 0)
                    logging.info("Loaded cached playlist")
        except Exception as e:
            logging.error(f"Error loading cached playlist: {e}")

    def save_cached_playlist(self):
        """Save playlist to cache"""
        try:
            with open(self.playlist_cache, 'w') as f:
                json.dump({
                    'playlist': self.current_playlist,
                    'version': self.playlist_version
                }, f)
        except Exception as e:
            logging.error(f"Error saving cached playlist: {e}")

    def cache_file(self, url, filename):
        """Download and cache a file"""
        cache_path = os.path.join(self.cache_dir, filename)
        if os.path.exists(cache_path):
            return cache_path

        try:
            full_url = url if url.startswith('http') else f"{self.server_url}{url}"
            response = requests.get(full_url, timeout=30, stream=True)
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logging.info(f"Cached file: {filename}")
                return cache_path
        except Exception as e:
            logging.error(f"Error caching file {url}: {e}")

        return None

    def display_image(self, filepath, duration):
        """Display image using PIL/Tkinter"""
        if not PIL_AVAILABLE or not TKINTER_AVAILABLE:
            logging.error("Image display requires PIL and tkinter")
            return

        try:
            img = Image.open(filepath)
            # Resize to fit screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            img.thumbnail((screen_width, screen_height), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(
                screen_width // 2,
                screen_height // 2,
                image=photo,
                anchor=tk.CENTER
            )
            self.canvas.image = photo  # Keep reference
            self.root.update()
            time.sleep(duration)
        except Exception as e:
            logging.error(f"Error displaying image: {e}")

    def display_video(self, filepath, duration):
        """Display video using VLC"""
        if not VLC_AVAILABLE:
            logging.error("Video playback requires python-vlc")
            return

        try:
            media = self.vlc_instance.media_new(filepath)
            self.vlc_player.set_media(media)
            
            if TKINTER_AVAILABLE:
                # Embed VLC player in tkinter window
                self.vlc_player.set_hwnd(self.canvas.winfo_id())
            
            self.vlc_player.play()
            time.sleep(duration)
            self.vlc_player.stop()
        except Exception as e:
            logging.error(f"Error playing video: {e}")

    def display_text(self, filepath, duration):
        """Display text content"""
        if not TKINTER_AVAILABLE:
            return

        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = "No content"
            
            self.canvas.delete("all")
            self.canvas.create_text(
                self.root.winfo_screenwidth() // 2,
                self.root.winfo_screenheight() // 2,
                text=text,
                fill='white',
                font=('Arial', 48),
                anchor=tk.CENTER,
                width=self.root.winfo_screenwidth() - 100
            )
            self.root.update()
            time.sleep(duration)
        except Exception as e:
            logging.error(f"Error displaying text: {e}")

    def play_next(self):
        """Play next item in playlist"""
        if not self.current_playlist or not self.current_playlist.get('items'):
            # No playlist, show default
            if TKINTER_AVAILABLE:
                self.canvas.delete("all")
                self.canvas.create_text(
                    self.root.winfo_screenwidth() // 2,
                    self.root.winfo_screenheight() // 2,
                    text="Waiting for playlist...",
                    fill='white',
                    font=('Arial', 36),
                    anchor=tk.CENTER
                )
                self.root.update()
            time.sleep(5)
            return

        items = self.current_playlist['items']
        if not items:
            time.sleep(5)
            return

        item = items[self.current_index]
        item_type = item.get('type', 'unknown')
        item_url = item.get('url', '')
        duration = item.get('duration', PLAYER_DEFAULT_DURATION)

        # Cache file
        filename = os.path.basename(item_url)
        filepath = self.cache_file(item_url, filename)

        if not filepath:
            logging.warning(f"Could not cache file: {item_url}")
            time.sleep(duration)
        else:
            if item_type == 'image':
                self.display_image(filepath, duration)
            elif item_type == 'video':
                self.display_video(filepath, duration)
            elif item_type == 'text':
                self.display_text(filepath, duration)
            else:
                logging.warning(f"Unknown item type: {item_type}")
                time.sleep(duration)

        # Move to next item
        self.current_index = (self.current_index + 1) % len(items)

    def run(self):
        """Main playback loop"""
        logging.info(f"Starting player: {self.device_name} ({self.device_id})")
        logging.info(f"Server: {self.server_url}")

        last_sync = 0

        try:
            while True:
                # Sync playlist periodically
                current_time = time.time()
                if current_time - last_sync > PLAYER_SYNC_INTERVAL:
                    self.fetch_playlist()
                    last_sync = current_time

                # Play next item
                self.play_next()

                # Update GUI if available
                if TKINTER_AVAILABLE:
                    self.root.update()

        except KeyboardInterrupt:
            logging.info("Player stopped by user")
        except Exception as e:
            logging.error(f"Player error: {e}", exc_info=True)
        finally:
            if self.vlc_player:
                self.vlc_player.stop()
            if self.root:
                self.root.quit()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Digital Signage Player')
    parser.add_argument('--server', default='http://localhost:5000',
                       help='Server URL (default: http://localhost:5000)')
    parser.add_argument('--device-id', required=True,
                       help='Device ID/UUID')
    parser.add_argument('--device-name',
                       help='Device name (default: Player-{device-id})')

    args = parser.parse_args()

    player = DigitalSignagePlayer(
        server_url=args.server,
        device_id=args.device_id,
        device_name=args.device_name
    )

    player.run()


if __name__ == '__main__':
    main()

