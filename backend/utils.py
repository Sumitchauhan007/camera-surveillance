"""
Utility functions for AI Surveillance System
"""
import cv2
import numpy as np
from datetime import datetime
import os
import json

def create_video_thumbnail(video_path, output_path=None):
    """Create thumbnail from video file"""
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return None
    
    # Resize to thumbnail size
    thumbnail = cv2.resize(frame, (320, 240))
    
    if output_path:
        cv2.imwrite(output_path, thumbnail)
    
    return thumbnail

def format_duration(seconds):
    """Format duration in seconds to human-readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def get_video_info(video_path):
    """Get video file information"""
    if not os.path.exists(video_path):
        return None
    
    cap = cv2.VideoCapture(video_path)
    
    info = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)),
        'size': os.path.getsize(video_path)
    }
    
    cap.release()
    return info

def cleanup_old_recordings(days=7):
    """Delete recordings older than specified days"""
    import config
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for filename in os.listdir(config.RECORDINGS_DIR):
        filepath = os.path.join(config.RECORDINGS_DIR, filename)
        
        if os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_time < cutoff_date:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"Deleted old recording: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")
    
    return deleted_count

def export_detections_to_json(db, output_file, days=30):
    """Export detections to JSON file"""
    from datetime import timedelta
    
    detections = db.get_recent_detections(limit=1000)
    
    export_data = []
    for det in detections:
        export_data.append({
            'id': det[0],
            'timestamp': det[1],
            'person_id': det[2],
            'person_name': det[3],
            'confidence': det[4],
            'face_image_path': det[5],
            'video_path': det[6],
            'camera_id': det[7]
        })
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    return len(export_data)

def send_notification(title, message):
    """Send system notification (Windows toast notification)"""
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=5, threaded=True)
    except ImportError:
        print(f"Notification: {title} - {message}")
    except Exception as e:
        print(f"Error sending notification: {e}")

def check_camera_available(camera_id):
    """Check if camera is available"""
    cap = cv2.VideoCapture(camera_id)
    is_available = cap.isOpened()
    cap.release()
    return is_available

def list_available_cameras(max_cameras=5):
    """List available cameras"""
    available = []
    
    for i in range(max_cameras):
        if check_camera_available(i):
            available.append(i)
    
    return available
