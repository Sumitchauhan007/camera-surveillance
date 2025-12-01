"""
Configuration file for AI Surveillance Camera System
"""
import os

# Camera Settings
CAMERA_ID = 0  # 0 for default webcam, or use RTSP URL for IP camera
CAMERA_WIDTH = 640  # Reduced for better performance
CAMERA_HEIGHT = 480  # Reduced for better performance
CAMERA_FPS = 30

# Face Detection Settings
DETECTION_CONFIDENCE = 0.5  # Minimum confidence for face detection
FACE_SIZE_THRESHOLD = 30  # Minimum face size in pixels
DETECTION_INTERVAL = 5  # Detect faces every N frames (higher = better performance, lower = more responsive)

# Face Recognition Settings
RECOGNITION_THRESHOLD = 0.4  # Similarity threshold for face recognition (lower = more lenient)
ENABLE_RECOGNITION = True

# Recording Settings
ENABLE_RECORDING = True
RECORD_ON_DETECTION = True  # Only record when faces are detected
MAX_RECORDING_DURATION = 300  # Maximum recording duration in seconds (5 minutes)
VIDEO_CODEC = 'mp4v'  # Video codec: 'mp4v', 'XVID', 'H264'
VIDEO_FPS = 20

# Storage Settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RECORDINGS_DIR = os.path.join(DATA_DIR, 'recordings')
FACES_DIR = os.path.join(DATA_DIR, 'faces')
KNOWN_FACES_DIR = os.path.join(DATA_DIR, 'known_faces')
DATABASE_PATH = os.path.join(DATA_DIR, 'surveillance.db')

# Alert Settings
ENABLE_ALERTS = True
UNKNOWN_FACE_ALERT = True
ALERT_COOLDOWN = 60  # Seconds between alerts for the same person

# Display Settings
SHOW_PREVIEW = True
SHOW_FPS = True
PREVIEW_WIDTH = 1280
PREVIEW_HEIGHT = 720

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
