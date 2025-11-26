# AI Surveillance System - Complete Setup Guide

## 🎯 Features

### Backend (Python/Flask)
- ✅ Real-time face detection using InsightFace RetinaFace
- ✅ Face recognition with student database
- ✅ Automatic intruder detection and alerts
- ✅ Video recording with smart triggers
- ✅ RESTful API for frontend communication
- ✅ SQLite database for all records

### Frontend (React)
- ✅ Modern admin dashboard with live camera feed
- ✅ Real-time face detection overlay
- ✅ Student management with webcam/upload registration
- ✅ Intruder alerts with photo capture
- ✅ Comprehensive reports and analytics
- ✅ Camera controls (start/stop/record/snapshot)
- ✅ Real-time notifications

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16+ and npm
- Webcam or IP camera
- Windows/Linux/Mac OS

## 🚀 Installation

### Step 1: Backend Setup

```bash
# Install Python dependencies
pip install flask flask-cors opencv-python numpy insightface onnxruntime Pillow

# Verify InsightFace installation
python -c "from insightface.app import FaceAnalysis; print('✓ InsightFace ready')"
```

### Step 2: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# The following packages will be installed:
# - react, react-dom, react-router-dom
# - axios (API calls)
# - react-toastify (notifications)
# - lucide-react (icons)
# - recharts (charts)
```

## 🎮 Running the Application

### Method 1: Separate Terminals (Development)

**Terminal 1 - Backend API:**
```bash
python api_server.py
```
The API will start on `http://localhost:5000`

**Terminal 2 - React Frontend:**
```bash
cd frontend
npm start
```
The frontend will open at `http://localhost:3000`

### Method 2: Production Build

```bash
# Build React frontend
cd frontend
npm run build

# Serve both from Flask (you'd need to configure Flask to serve the build folder)
```

## 📱 Using the Application

### 1. Dashboard
- **Start Camera**: Click "Start Camera" to begin live monitoring
- **Recording**: Toggle recording on/off
- **Snapshot**: Capture current frame
- **Live Feed**: See real-time face detection with bounding boxes
- **Statistics**: View total detections, students, alerts

### 2. Student Management
**Adding Students:**
- Click "Add Student" button
- Enter student name and optional notes
- Choose to upload photo OR use webcam
- System will detect face and create profile

**Managing Students:**
- Search students by name
- View detection history
- Delete students if needed

### 3. Reports & Analytics
**Daily Report:**
- Select date to view activity
- See all student detections
- View intruder incidents
- Export reports (coming soon)

**Intruder History:**
- Browse all unknown person detections
- View captured photos
- Track incident timestamps

### 4. Alerts
- View all system alerts
- Filter by acknowledged/unacknowledged
- Acknowledge alerts to clear
- Real-time intruder notifications

### 5. Settings
- Configure camera parameters
- Adjust detection thresholds
- Set alert preferences
- Recording settings

## 🔧 Configuration

### Backend Configuration (`config.py`)

```python
# Camera Settings
CAMERA_ID = 0  # 0 for webcam, or "rtsp://..." for IP camera
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Detection Settings
DETECTION_CONFIDENCE = 0.5  # Face detection threshold
RECOGNITION_THRESHOLD = 0.6  # Face recognition threshold

# Recording Settings
ENABLE_RECORDING = True
RECORD_ON_DETECTION = True  # Only record when faces detected

# Alerts
ENABLE_ALERTS = True
UNKNOWN_FACE_ALERT = True
```

### Frontend Configuration

Edit `frontend/src/services/api.js` if your backend runs on a different port:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

## 📁 Project Structure

```
ai surv-2/
├── backend/
│   ├── api_server.py        # Flask REST API
│   ├── face_detector.py     # InsightFace integration
│   ├── database.py          # SQLite database
│   ├── config.py            # Configuration
│   ├── utils.py             # Utility functions
│   └── data/                # Data storage
│       ├── recordings/      # Video files
│       ├── faces/           # Detected faces
│       ├── known_faces/     # Student photos
│       └── surveillance.db  # Database
│
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/      # Reusable components
    │   │   └── Layout.js    # Main layout with sidebar
    │   ├── pages/           # Main pages
    │   │   ├── Dashboard.js
    │   │   ├── Students.js
    │   │   ├── Reports.js
    │   │   ├── Alerts.js
    │   │   └── Settings.js
    │   ├── services/
    │   │   └── api.js       # API client
    │   ├── App.js
    │   └── index.js
    └── package.json
```

## 🔌 API Endpoints

### Camera Control
- `POST /api/camera/start` - Start camera
- `POST /api/camera/stop` - Stop camera
- `GET /api/camera/status` - Get camera status
- `GET /api/camera/frame` - Get current frame
- `POST /api/camera/snapshot` - Take snapshot

### Recording
- `POST /api/recording/start` - Start recording
- `POST /api/recording/stop` - Stop recording

### Students
- `GET /api/students` - Get all students
- `POST /api/students` - Add new student
- `DELETE /api/students/:id` - Delete student

### Detections & Reports
- `GET /api/detections/recent` - Recent detections
- `GET /api/detections/student/:name` - Student history
- `GET /api/reports/daily?date=YYYY-MM-DD` - Daily report
- `GET /api/reports/intruders` - All intruders

### Alerts
- `GET /api/alerts` - Get all alerts
- `POST /api/alerts/:id/acknowledge` - Acknowledge alert

### System
- `GET /api/statistics` - System statistics
- `GET /api/health` - Health check
- `GET /api/config` - System configuration

## 🎨 Features in Detail

### Face Detection
- Uses InsightFace's RetinaFace model
- Detects multiple faces simultaneously
- Real-time bounding box visualization
- Facial landmark detection

### Face Recognition
- 512-dimensional face embeddings
- Cosine similarity matching
- Configurable recognition threshold
- Automatic unknown detection

### Student Registration
- Upload photo or use webcam
- Automatic face extraction
- Duplicate detection
- Profile management

### Intruder Detection
- Automatic unknown person alerts
- Photo capture of intruders
- Historical tracking
- Real-time notifications

### Recording System
- Smart recording (only when detecting)
- Manual recording control
- MP4 format with H.264 codec
- Linked to detection events

### Reporting
- Daily activity summaries
- Student attendance tracking
- Intruder incident reports
- Export capabilities (planned)

## 🛠️ Troubleshooting

### Camera Not Starting
```bash
# Check available cameras
python -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"
```

### InsightFace Model Download
On first run, InsightFace downloads models (~500MB). Ensure stable internet.

### CORS Errors
Make sure Flask server is running and CORS is enabled in `api_server.py`

### Port Already in Use
```bash
# Change Flask port in api_server.py
app.run(host='0.0.0.0', port=5001)  # Use different port

# Update frontend API URL in src/services/api.js
```

### Face Not Detected
- Ensure good lighting
- Face should be clearly visible
- Try different angles
- Adjust detection confidence in settings

## 🔐 Security Considerations

- Run on internal network only (not exposed to internet)
- Implement authentication for production use
- Encrypt face embeddings in database
- Comply with local privacy laws
- Regular security updates

## 📊 Performance Optimization

### CPU Performance
- Increase `DETECTION_INTERVAL` (process every Nth frame)
- Reduce camera resolution
- Lower FPS setting

### GPU Acceleration
```bash
pip uninstall onnxruntime
pip install onnxruntime-gpu
```

## 🆘 Support & Documentation

- Check camera permissions
- Verify Python and Node.js versions
- Review browser console for frontend errors
- Check Flask terminal for backend errors

## 📝 Future Enhancements

- [ ] Multi-camera support
- [ ] Cloud storage integration
- [ ] Mobile app
- [ ] Email/SMS notifications
- [ ] Advanced analytics
- [ ] Motion detection
- [ ] Person tracking
- [ ] API authentication

## 📄 License

For educational and personal use. Ensure compliance with local surveillance and privacy laws.

## 🙏 Credits

- **InsightFace** - Face detection and recognition
- **React** - Frontend framework
- **Flask** - Backend API
- **OpenCV** - Computer vision

---

**Ready to use!** Start the backend server and frontend, then access the dashboard at `http://localhost:3000`
