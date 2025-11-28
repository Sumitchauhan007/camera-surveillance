"""
Flask REST API Server for AI Surveillance System
Provides endpoints for React frontendfghjk
"""
from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import cv2
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import os
import base64
from io import BytesIO
from PIL import Image
import json

from face_detector import FaceDetector
from database import SurveillanceDB
import config

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global state
camera_state = {
    'is_running': False,
    'is_recording': False,
    'cap': None,
    'current_frame': None,
    'faces_detected': [],
    'video_writer': None,
    'recording_path': None
}

face_detector = FaceDetector()
db = SurveillanceDB()

# Thread lock
lock = threading.Lock()

# ============= CAMERA CONTROL ENDPOINTS =============

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    """Start camera feed"""
    global camera_state
    
    with lock:
        if camera_state['is_running']:
            return jsonify({'success': False, 'message': 'Camera already running'})
        
        try:
            camera_state['cap'] = cv2.VideoCapture(config.CAMERA_ID)
            
            if not camera_state['cap'].isOpened():
                return jsonify({'success': False, 'message': 'Failed to open camera'})
            
            camera_state['cap'].set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            camera_state['cap'].set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            camera_state['is_running'] = True
            
            # Start processing thread
            threading.Thread(target=process_camera_feed, daemon=True).start()
            
            db.log_system_event("INFO", "Camera started via API")
            
            return jsonify({'success': True, 'message': 'Camera started'})
        
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    """Stop camera feed"""
    global camera_state
    
    with lock:
        if not camera_state['is_running']:
            return jsonify({'success': False, 'message': 'Camera not running'})
        
        camera_state['is_running'] = False
        
        if camera_state['is_recording']:
            stop_recording_internal()
        
        if camera_state['cap']:
            camera_state['cap'].release()
            camera_state['cap'] = None
        
        camera_state['current_frame'] = None
        camera_state['faces_detected'] = []
        
        db.log_system_event("INFO", "Camera stopped via API")
        
        return jsonify({'success': True, 'message': 'Camera stopped'})

@app.route('/api/camera/status', methods=['GET'])
def camera_status():
    """Get camera status"""
    return jsonify({
        'is_running': camera_state['is_running'],
        'is_recording': camera_state['is_recording'],
        'faces_detected': len(camera_state['faces_detected'])
    })

@app.route('/api/camera/frame', methods=['GET'])
def get_frame():
    """Get current camera frame as JPEG"""
    if camera_state['current_frame'] is None:
        return jsonify({'success': False, 'message': 'No frame available'}), 404
    
    try:
        # Encode frame to JPEG
        _, buffer = cv2.imencode('.jpg', camera_state['current_frame'])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'frame': f'data:image/jpeg;base64,{img_base64}',
            'timestamp': datetime.now().isoformat(),
            'faces': camera_state['faces_detected']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/camera/stream')
def video_stream():
    """Stream video feed"""
    def generate():
        while camera_state['is_running']:
            if camera_state['current_frame'] is not None:
                _, buffer = cv2.imencode('.jpg', camera_state['current_frame'])
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/recording/start', methods=['POST'])
def start_recording():
    """Start video recording"""
    global camera_state
    
    with lock:
        if not camera_state['is_running']:
            return jsonify({'success': False, 'message': 'Camera not running'})
        
        if camera_state['is_recording']:
            return jsonify({'success': False, 'message': 'Already recording'})
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mp4"
            camera_state['recording_path'] = os.path.join(config.RECORDINGS_DIR, filename)
            
            fourcc = cv2.VideoWriter_fourcc(*config.VIDEO_CODEC)
            camera_state['video_writer'] = cv2.VideoWriter(
                camera_state['recording_path'],
                fourcc,
                config.VIDEO_FPS,
                (config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
            )
            
            camera_state['is_recording'] = True
            db.log_system_event("INFO", f"Recording started: {filename}")
            
            return jsonify({'success': True, 'message': 'Recording started', 'filename': filename})
        
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/recording/stop', methods=['POST'])
def stop_recording():
    """Stop video recording"""
    with lock:
        result = stop_recording_internal()
        return jsonify(result)

def stop_recording_internal():
    """Internal function to stop recording"""
    if not camera_state['is_recording']:
        return {'success': False, 'message': 'Not recording'}
    
    if camera_state['video_writer']:
        camera_state['video_writer'].release()
        camera_state['video_writer'] = None
    
    filename = os.path.basename(camera_state['recording_path']) if camera_state['recording_path'] else None
    camera_state['is_recording'] = False
    camera_state['recording_path'] = None
    
    db.log_system_event("INFO", f"Recording stopped: {filename}")
    
    return {'success': True, 'message': 'Recording stopped', 'filename': filename}

@app.route('/api/camera/snapshot', methods=['POST'])
def take_snapshot():
    """Take a snapshot from current frame"""
    if camera_state['current_frame'] is None:
        return jsonify({'success': False, 'message': 'No frame available'})
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp}.jpg"
        filepath = os.path.join(config.DATA_DIR, filename)
        
        cv2.imwrite(filepath, camera_state['current_frame'])
        
        return jsonify({'success': True, 'message': 'Snapshot saved', 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============= STUDENT MANAGEMENT ENDPOINTS =============

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    students = db.get_known_persons()
    
    result = []
    for student in students:
        result.append({
            'id': student[0],
            'name': student[1],
            'date_added': student[2],
            'image_path': student[3],
            'notes': student[4]
        })
    
    return jsonify({'success': True, 'students': result})

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get specific student"""
    # Implementation needed based on database structure
    return jsonify({'success': True, 'student': {}})

@app.route('/api/students', methods=['POST'])
def add_student():
    """Add new student"""
    try:
        data = request.get_json()
        name = data.get('name')
        notes = data.get('notes', '')
        image_data = data.get('image')  # Base64 encoded image
        
        if not name or not image_data:
            return jsonify({'success': False, 'message': 'Name and image required'})
        
        print(f"📝 Adding student: {name}")
        
        # Decode base64 image
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name.replace(' ', '_')}_{timestamp}.jpg"
        image_path = os.path.join(config.KNOWN_FACES_DIR, filename)
        image.save(image_path)
        print(f"💾 Saved image to: {image_path}")
        
        # Convert to OpenCV format for face detection
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Add to face detector
        print(f"🔍 Adding face to detector...")
        success = face_detector.add_known_face(name, image_path)
        
        if not success:
            os.remove(image_path)
            return jsonify({'success': False, 'message': 'No face detected in image or multiple faces found'})
        
        print(f"✅ Face added to detector")
        
        # Add to database
        print(f"💾 Adding {name} to database...")
        db_success = db.add_known_person(name, image_path, notes)
        
        if not db_success:
            # Student already in database, but might not be in face detector
            # This is OK - just update the face detector
            print(f"⚠️ Student {name} already in database, but added to face detector")
            db.log_system_event("INFO", f"Student face updated: {name}")
            return jsonify({'success': True, 'message': f'Student {name} face data updated successfully'})
        
        db.log_system_event("INFO", f"Student added: {name}")
        print(f"✅ Student {name} added successfully to database")
        
        # Verify it was added
        all_students = db.get_known_persons()
        print(f"📊 Total students in database after add: {len(all_students)}")
        
        return jsonify({'success': True, 'message': f'Student {name} added successfully'})
    
    except Exception as e:
        print(f"❌ Error adding student: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete student"""
    try:
        # Get student info first
        students = db.get_known_persons()
        student = next((s for s in students if s[0] == student_id), None)
        
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'})
        
        name = student[1]
        
        # Remove from face detector
        if name in face_detector.known_faces:
            del face_detector.known_faces[name]
            face_detector.save_known_faces()
        
        # Remove from database (you'll need to add this method to database.py)
        # For now, just log it
        db.log_system_event("INFO", f"Student deleted: {name}")
        
        return jsonify({'success': True, 'message': f'Student {name} deleted'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============= DETECTION & ALERTS ENDPOINTS =============

@app.route('/api/detections/recent', methods=['GET'])
def get_recent_detections():
    """Get recent detections"""
    limit = request.args.get('limit', 50, type=int)
    detections = db.get_recent_detections(limit=limit)
    
    result = []
    for det in detections:
        result.append({
            'id': det[0],
            'timestamp': det[1],
            'person_id': det[2],
            'person_name': det[3],
            'confidence': det[4],
            'face_image_path': det[5],
            'video_path': det[6],
            'camera_id': det[7],
            'is_intruder': det[3] is None  # Intruder if name is None
        })
    
    return jsonify({'success': True, 'detections': result})

@app.route('/api/detections/student/<string:name>', methods=['GET'])
def get_student_detections(name):
    """Get all detections for a specific student"""
    detections = db.get_detections_by_person(name)
    
    result = []
    for det in detections:
        result.append({
            'id': det[0],
            'timestamp': det[1],
            'person_id': det[2],
            'person_name': det[3],
            'confidence': det[4],
            'face_image_path': det[5],
            'video_path': det[6],
            'camera_id': det[7]
        })
    
    return jsonify({'success': True, 'detections': result})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get unacknowledged alerts"""
    alerts = db.get_unacknowledged_alerts()
    
    result = []
    for alert in alerts:
        result.append({
            'id': alert[0],
            'timestamp': alert[1],
            'alert_type': alert[2],
            'person_id': alert[3],
            'person_name': alert[4],
            'description': alert[5],
            'acknowledged': alert[6]
        })
    
    return jsonify({'success': True, 'alerts': result})

@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    success = db.acknowledge_alert(alert_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Alert acknowledged'})
    else:
        return jsonify({'success': False, 'message': 'Failed to acknowledge alert'})

# ============= STATISTICS & REPORTS ENDPOINTS =============

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    stats = db.get_statistics()
    
    # Add additional stats
    alerts = db.get_unacknowledged_alerts()
    intruder_count = len([a for a in alerts if a[2] == 'UNKNOWN_PERSON'])
    
    stats['pending_intruder_alerts'] = intruder_count
    stats['camera_status'] = camera_state['is_running']
    stats['recording_status'] = camera_state['is_recording']
    
    return jsonify({'success': True, 'statistics': stats})

@app.route('/api/reports/daily', methods=['GET'])
def get_daily_report():
    """Get daily activity report"""
    date = request.args.get('date', datetime.now().date().isoformat())
    
    # Get detections for the day
    detections = db.get_recent_detections(limit=1000)
    
    # Filter by date
    daily_detections = [d for d in detections if d[1].startswith(date)]
    
    # Categorize
    students = {}
    intruders = []
    
    for det in daily_detections:
        if det[3]:  # Known student
            if det[3] not in students:
                students[det[3]] = {'count': 0, 'first_seen': det[1], 'last_seen': det[1]}
            students[det[3]]['count'] += 1
            students[det[3]]['last_seen'] = det[1]
        else:  # Intruder
            intruders.append({
                'timestamp': det[1],
                'person_id': det[2],
                'face_image_path': det[5]
            })
    
    return jsonify({
        'success': True,
        'date': date,
        'total_detections': len(daily_detections),
        'students': students,
        'intruders': intruders
    })

@app.route('/api/reports/intruders', methods=['GET'])
def get_intruder_report():
    """Get all intruder detections"""
    detections = db.get_recent_detections(limit=500)
    
    intruders = []
    for det in detections:
        if det[3] is None:  # Unknown person
            intruders.append({
                'id': det[0],
                'timestamp': det[1],
                'person_id': det[2],
                'face_image_path': det[5],
                'video_path': det[6]
            })
    
    return jsonify({'success': True, 'intruders': intruders})

@app.route('/api/images/<path:filename>')
def serve_image(filename):
    """Serve images from data directories"""
    # Try different directories
    paths = [
        os.path.join(config.FACES_DIR, filename),
        os.path.join(config.KNOWN_FACES_DIR, filename),
        os.path.join(config.DATA_DIR, filename)
    ]
    
    for path in paths:
        if os.path.exists(path):
            return send_file(path, mimetype='image/jpeg')
    
    return jsonify({'success': False, 'message': 'Image not found'}), 404

# ============= CAMERA PROCESSING =============

def process_camera_feed():
    """Process camera feed in background thread"""
    frame_count = 0
    
    while camera_state['is_running']:
        if camera_state['cap'] is None:
            break
        
        ret, frame = camera_state['cap'].read()
        
        if not ret:
            break
        
        frame_count += 1
        
        # Detect faces periodically
        if frame_count % config.DETECTION_INTERVAL == 0:
            faces = face_detector.detect_faces(frame)
            
            camera_state['faces_detected'] = []
            
            for face in faces:
                bbox = face.bbox.astype(int)
                
                # Get embedding and recognize
                embedding = face_detector.get_face_embedding(face)
                person_name, similarity = face_detector.recognize_face(embedding)
                
                person_id = person_name if person_name else "intruder"
                
                # Draw on frame
                frame = face_detector.draw_face_box(frame, face, person_name, similarity)
                
                # Store detection info
                camera_state['faces_detected'].append({
                    'bbox': bbox.tolist(),
                    'name': person_name,
                    'confidence': float(similarity),
                    'is_intruder': person_name is None
                })
                
                # Log detection
                face_image_path = face_detector.save_face_image(frame, face, person_id)
                
                db.log_detection(
                    person_id=person_id,
                    person_name=person_name,
                    confidence=similarity,
                    face_image_path=face_image_path,
                    video_path=camera_state['recording_path'],
                    camera_id=str(config.CAMERA_ID)
                )
                
                # Create alert for intruders
                if not person_name and config.ENABLE_ALERTS:
                    db.create_alert(
                        alert_type="INTRUDER",
                        person_id=person_id,
                        description=f"Intruder detected at {datetime.now().strftime('%H:%M:%S')}"
                    )
        
        # Draw info overlay
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if camera_state['is_recording']:
            cv2.circle(frame, (frame.shape[1] - 30, 30), 8, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (frame.shape[1] - 70, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Update current frame
        with lock:
            camera_state['current_frame'] = frame.copy()
            
            # Write to video if recording
            if camera_state['is_recording'] and camera_state['video_writer']:
                camera_state['video_writer'].write(frame)
        
        time.sleep(0.001)  # Small delay

# ============= SERVER INFO =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'camera_running': camera_state['is_running']
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get system configuration"""
    return jsonify({
        'camera_id': config.CAMERA_ID,
        'camera_width': config.CAMERA_WIDTH,
        'camera_height': config.CAMERA_HEIGHT,
        'detection_confidence': config.DETECTION_CONFIDENCE,
        'recognition_threshold': config.RECOGNITION_THRESHOLD,
        'enable_recording': config.ENABLE_RECORDING,
        'enable_alerts': config.ENABLE_ALERTS
    })

if __name__ == '__main__':
    print("=" * 50)
    print("AI Surveillance API Server")
    print("=" * 50)
    print(f"Starting server on http://localhost:5000")
    print("API Documentation:")
    print("  Camera: /api/camera/*")
    print("  Students: /api/students")
    print("  Detections: /api/detections/*")
    print("  Alerts: /api/alerts")
    print("  Statistics: /api/statistics")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
