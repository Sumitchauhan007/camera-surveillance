# AI Surveillance System

Complete AI-powered surveillance system with face detection, recognition, and intruder alerts.

## 📁 Project Structure

```
ai surv-2/
├── backend/              # Flask API & Python backend
│   ├── api_server.py    # Main API server
│   ├── face_detector.py # InsightFace integration
│   ├── database.py      # SQLite database
│   ├── config.py        # Configuration
│   ├── utils.py         # Utility functions
│   ├── main.py          # CLI application
│   ├── gui.py           # Tkinter GUI
│   └── data/            # Data storage
│       ├── recordings/  # Video recordings
│       ├── faces/       # Detected faces
│       └── known_faces/ # Student photos
│
├── frontend/            # React admin panel
│   ├── public/
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── pages/       # Main pages (Dashboard, Students, Reports, Alerts, Settings)
│   │   ├── services/    # API client
│   │   └── App.js       # Main app
│   └── package.json
│
├── requirements.txt     # Python dependencies
├── setup.bat           # Setup script
├── start.bat           # Start script
└── SETUP_GUIDE.md      # Detailed documentation
```

## 🚀 Quick Start

### 1. Setup (First time only)
```bash
setup.bat
```
This will install all Python and React dependencies.

### 2. Start the Application
```bash
start.bat
```
This opens two terminals:
- Backend API on http://localhost:5000
- Frontend on http://localhost:3000

### 3. Manual Start (Alternative)
**Terminal 1:**
```bash
cd backend
python api_server.py
```

**Terminal 2:**
```bash
cd frontend
npm start
```

## ✨ Features

### Backend (Python/Flask)
- ✅ Real-time face detection using InsightFace RetinaFace
- ✅ Face recognition with student database
- ✅ Automatic intruder detection and alerts
- ✅ Video recording with smart triggers
- ✅ RESTful API for frontend communication
- ✅ SQLite database with comprehensive logging

### Frontend (React)
- 🎥 **Live Camera Feed** - Real-time monitoring with face detection overlay
- 👤 **Student Management** - Add/remove students with webcam or photo upload
- 🚨 **Intruder Alerts** - Automatic detection and real-time notifications
- 📊 **Reports & Analytics** - Daily reports with photo evidence
- 🎬 **Camera Controls** - Start/stop/record/snapshot
- ⚙️ **Settings** - Configure all system parameters

## 📖 Documentation

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete documentation including:
- Detailed installation instructions
- API endpoints reference
- Troubleshooting guide
- Configuration options
- Security considerations

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- Flask (REST API)
- InsightFace (Face detection/recognition)
- OpenCV (Computer vision)
- SQLite (Database)

**Frontend:**
- React 18
- React Router
- Axios (API client)
- React Toastify (Notifications)
- Lucide React (Icons)

## 📝 Requirements

- Python 3.8+
- Node.js 16+
- Webcam or IP camera
- 2GB RAM minimum
- ~500MB disk space (for AI models)

## 🎯 First Use

1. Start the application with `start.bat`
2. Open http://localhost:3000
3. Click "Start Camera" on the dashboard
4. Go to "Students" page to add your first student
5. System will detect and alert for unknown faces

## 🔐 Security Note

This is for internal use only. Do not expose to the internet without proper authentication and encryption.

## 📄 License

Educational and personal use. Comply with local privacy and surveillance laws.

### GUI Mode (Dashboard)

Launch the GUI dashboard:
```bash
python gui.py
```

The GUI provides:
- Live video feed with face detection
- Real-time statistics
- Recent detection history
- Known faces management
- Recording controls

## Configuration

Edit `config.py` to customize settings:

### Camera Settings
```python
CAMERA_ID = 0  # 0 for webcam, or "rtsp://..." for IP camera
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30
```

### Detection Settings
```python
DETECTION_CONFIDENCE = 0.5  # Face detection threshold
FACE_SIZE_THRESHOLD = 30    # Minimum face size in pixels
RECOGNITION_THRESHOLD = 0.6 # Face recognition threshold
```

### Recording Settings
```python
ENABLE_RECORDING = True
RECORD_ON_DETECTION = True  # Only record when faces detected
MAX_RECORDING_DURATION = 300  # Max 5 minutes per recording
```

## Adding Known Faces

### Method 1: Via GUI
1. Launch `gui.py`
2. Click "Add Known Face"
3. Select an image file
4. Enter the person's name

### Method 2: Via Known Faces Directory
1. Place face images in `data/known_faces/` directory
2. Name each file with the person's name (e.g., `john_doe.jpg`)
3. Restart the application

### Method 3: Programmatically
```python
from face_detector import FaceDetector

detector = FaceDetector()
detector.add_known_face("John Doe", "path/to/image.jpg")
```

## Project Structure

```
ai surv-2/
├── main.py              # Main surveillance application
├── gui.py               # GUI dashboard
├── face_detector.py     # Face detection and recognition
├── database.py          # Database operations
├── config.py            # Configuration settings
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── data/                # Data directory (auto-created)
    ├── recordings/      # Video recordings
    ├── faces/           # Detected face images
    ├── known_faces/     # Known face reference images
    └── surveillance.db  # SQLite database
```

## Database Schema

### detection_events
Stores all face detection events with timestamps, person information, and video references.

### known_persons
Registry of known individuals with reference images.

### alerts
System alerts for unknown persons or suspicious activity.

### system_logs
Application logs and events.

## Performance Tips

1. **CPU Performance**: Default configuration uses CPU. For better performance:
   - Reduce `CAMERA_WIDTH` and `CAMERA_HEIGHT`
   - Increase `DETECTION_INTERVAL` to detect every N frames

2. **GPU Acceleration**: For NVIDIA GPUs:
   ```bash
   pip uninstall onnxruntime
   pip install onnxruntime-gpu
   ```

3. **Storage Management**: Use the cleanup utility:
   ```python
   from utils import cleanup_old_recordings
   cleanup_old_recordings(days=7)  # Delete recordings older than 7 days
   ```

## Features in Detail

### Face Detection
- RetinaFace algorithm via InsightFace
- Detects multiple faces simultaneously
- Facial landmark detection (eyes, nose, mouth)
- Bounding box visualization

### Face Recognition
- 512-dimensional face embeddings
- Cosine similarity matching
- Configurable recognition threshold
- Automatic unknown person detection

### Recording System
- Automatic recording on detection
- Manual recording control
- MP4 format with configurable codec
- Maximum duration limits
- Linked to detection events in database

### Alert System
- Unknown person alerts
- Cooldown period to prevent spam
- Database-stored alerts
- GUI notifications

## Troubleshooting

### Camera not detected
```python
from utils import list_available_cameras
print(list_available_cameras())  # Lists available camera IDs
```

### InsightFace model download issues
The first run downloads models (~500MB). Ensure stable internet connection.

### Low detection accuracy
- Ensure good lighting
- Use higher resolution camera
- Adjust `DETECTION_CONFIDENCE` threshold
- Add more reference images for known faces

### High CPU usage
- Increase `DETECTION_INTERVAL`
- Reduce camera resolution
- Consider GPU acceleration

## API Usage

### Programmatic Access

```python
from face_detector import FaceDetector
from database import SurveillanceDB

# Initialize
detector = FaceDetector()
db = SurveillanceDB()

# Detect faces in image
import cv2
image = cv2.imread("photo.jpg")
faces = detector.detect_faces(image)

# Process detections
for face in faces:
    embedding = detector.get_face_embedding(face)
    name, similarity = detector.recognize_face(embedding)
    print(f"Detected: {name or 'Unknown'} ({similarity:.2f})")

# Query database
recent = db.get_recent_detections(limit=10)
stats = db.get_statistics()
```

## Security Considerations

- Face recognition is not 100% accurate
- Use appropriate `RECOGNITION_THRESHOLD` for your use case
- Secure the `data/` directory with proper permissions
- Consider encryption for stored face embeddings
- Comply with local privacy and surveillance laws

## License

This project is for educational and personal use. Ensure compliance with local laws regarding surveillance and facial recognition.

## Credits

- **InsightFace**: Face detection and recognition models
- **OpenCV**: Computer vision library
- **SQLite**: Database engine

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review configuration settings
3. Ensure all dependencies are installed correctly

## Future Enhancements

- [ ] Multi-camera support
- [ ] Cloud storage integration
- [ ] Mobile app for remote monitoring
- [ ] Advanced analytics and reporting
- [ ] Email/SMS notifications
- [ ] Motion detection integration
- [ ] Night vision support
- [ ] Person tracking across frames
