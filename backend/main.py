"""
Main AI Surveillance Camera Application
"""
import cv2
import numpy as np
from datetime import datetime, timedelta
import time
import threading
import os
from face_detector import FaceDetector
from database import SurveillanceDB
import config

class SurveillanceCamera:
    def __init__(self):
        """Initialize surveillance camera system"""
        print("=" * 50)
        print("AI Surveillance Camera System")
        print("=" * 50)
        
        # Initialize components
        self.face_detector = FaceDetector()
        self.db = SurveillanceDB()
        
        # Camera setup
        self.cap = None
        self.is_running = False
        self.frame_count = 0
        
        # Recording setup
        self.video_writer = None
        self.recording_start_time = None
        self.current_video_path = None
        self.is_recording = False
        
        # Detection tracking
        self.last_detection_time = {}
        self.detected_persons = set()
        self.photo_taken_for = {}  # Track which persons have had photos taken
        self.person_still_present = {}  # Track if person is still in frame
        
        # FPS calculation
        self.fps = 0
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        
        print("Initialization complete!")
    
    def initialize_camera(self):
        """Initialize camera capture"""
        print(f"Initializing camera (ID: {config.CAMERA_ID})...")
        
        if isinstance(config.CAMERA_ID, int):
            self.cap = cv2.VideoCapture(config.CAMERA_ID)
        else:
            # RTSP or video file
            self.cap = cv2.VideoCapture(config.CAMERA_ID)
        
        if not self.cap.isOpened():
            raise Exception("Failed to open camera!")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        
        print(f"Camera initialized: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
              f"{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    
    def start_recording(self):
        """Start video recording"""
        if self.is_recording:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp4"
        self.current_video_path = os.path.join(config.RECORDINGS_DIR, filename)
        
        fourcc = cv2.VideoWriter_fourcc(*config.VIDEO_CODEC)
        frame_size = (config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
        
        self.video_writer = cv2.VideoWriter(
            self.current_video_path,
            fourcc,
            config.VIDEO_FPS,
            frame_size
        )
        
        self.recording_start_time = datetime.now()
        self.is_recording = True
        
        self.db.log_system_event("INFO", "Recording started", self.current_video_path)
        print(f"Recording started: {filename}")
    
    def stop_recording(self):
        """Stop video recording"""
        if not self.is_recording:
            return
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        duration = (datetime.now() - self.recording_start_time).total_seconds()
        self.db.log_system_event("INFO", f"Recording stopped (Duration: {duration:.1f}s)", 
                                self.current_video_path)
        
        print(f"Recording stopped: {self.current_video_path} (Duration: {duration:.1f}s)")
        
        self.is_recording = False
        self.recording_start_time = None
        self.current_video_path = None
    
    def process_frame(self, frame):
        """Process a single frame for face detection"""
        faces = []
        
        # Detect faces
        if self.frame_count % config.DETECTION_INTERVAL == 0:
            faces = self.face_detector.detect_faces(frame)
        
        return faces
    
    def handle_detection(self, frame, faces):
        """Handle detected faces"""
        current_time = datetime.now()
        faces_detected = len(faces) > 0
        
        # Track which persons are currently in frame
        current_frame_persons = set()
        
        # Start recording if faces detected and recording is enabled
        if faces_detected and config.ENABLE_RECORDING and config.RECORD_ON_DETECTION:
            if not self.is_recording:
                self.start_recording()
        
        # Process each detected face
        for face in faces:
            # Check face size
            bbox = face.bbox.astype(int)
            face_width = bbox[2] - bbox[0]
            face_height = bbox[3] - bbox[1]
            
            if face_width < config.FACE_SIZE_THRESHOLD or face_height < config.FACE_SIZE_THRESHOLD:
                continue
            
            # Get face embedding and recognize
            embedding = self.face_detector.get_face_embedding(face)
            person_name = None
            similarity = 0
            person_id = "unknown"
            
            if config.ENABLE_RECOGNITION:
                person_name, similarity = self.face_detector.recognize_face(embedding)
                if person_name:
                    person_id = person_name
            
            # Add to current frame persons
            current_frame_persons.add(person_id)
            
            # Draw face box on frame
            frame = self.face_detector.draw_face_box(frame, face, person_name, similarity)
            
            # Check if photo already taken for this person in current detection session
            take_photo = False
            if person_id not in self.photo_taken_for:
                # First time seeing this person - take photo
                take_photo = True
                self.photo_taken_for[person_id] = current_time
            elif person_id not in self.person_still_present:
                # Person returned after leaving - take new photo
                take_photo = True
                self.photo_taken_for[person_id] = current_time
            
            # Mark person as present in this frame
            self.person_still_present[person_id] = current_time
            
            if take_photo:
                # Save face image
                face_image_path = self.face_detector.save_face_image(frame, face, person_id)
                
                # Log to database
                self.db.log_detection(
                    person_id=person_id,
                    person_name=person_name,
                    confidence=similarity,
                    face_image_path=face_image_path,
                    video_path=self.current_video_path,
                    camera_id=str(config.CAMERA_ID)
                )
                
                # Create alert for unknown faces
                if not person_name and config.ENABLE_ALERTS and config.UNKNOWN_FACE_ALERT:
                    self.db.create_alert(
                        alert_type="UNKNOWN_PERSON",
                        person_id=person_id,
                        description=f"Unknown person detected at {current_time.strftime('%H:%M:%S')}"
                    )
                
                print(f"[{current_time.strftime('%H:%M:%S')}] Photo captured: {person_name or 'Unknown'} "
                      f"(Confidence: {similarity:.2f})")
        
        # Clean up persons who are no longer in frame (not seen for 5 seconds)
        persons_to_remove = []
        for person_id, last_seen in list(self.person_still_present.items()):
            if person_id not in current_frame_persons:
                time_diff = (current_time - last_seen).total_seconds()
                if time_diff > 5:  # Person hasn't been seen for 5 seconds
                    persons_to_remove.append(person_id)
        
        for person_id in persons_to_remove:
            del self.person_still_present[person_id]
            if person_id in self.photo_taken_for:
                del self.photo_taken_for[person_id]
        
        # Stop recording if no faces and max duration reached
        if self.is_recording:
            recording_duration = (current_time - self.recording_start_time).total_seconds()
            
            if not faces_detected:
                # Stop recording after 5 seconds of no detection
                if recording_duration > 5:
                    self.stop_recording()
            elif recording_duration > config.MAX_RECORDING_DURATION:
                # Stop if max duration reached
                self.stop_recording()
        
        return frame
    
    def calculate_fps(self):
        """Calculate current FPS"""
        self.fps_frame_count += 1
        
        if self.fps_frame_count >= 30:
            current_time = time.time()
            elapsed = current_time - self.fps_start_time
            self.fps = self.fps_frame_count / elapsed
            
            self.fps_frame_count = 0
            self.fps_start_time = current_time
    
    def draw_info_overlay(self, frame):
        """Draw information overlay on frame"""
        overlay = frame.copy()
        
        # Draw semi-transparent black box at top
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 80), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        
        # System info
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # FPS
        if config.SHOW_FPS:
            fps_text = f"FPS: {self.fps:.1f}"
            cv2.putText(frame, fps_text, (10, 55), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Recording indicator
        if self.is_recording:
            rec_text = "REC"
            text_size = cv2.getTextSize(rec_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            x_pos = frame.shape[1] - text_size[0] - 20
            cv2.circle(frame, (x_pos - 15, 30), 8, (0, 0, 255), -1)
            cv2.putText(frame, rec_text, (x_pos, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        return frame
    
    def run(self):
        """Main surveillance loop"""
        try:
            self.initialize_camera()
            self.is_running = True
            
            self.db.log_system_event("INFO", "Surveillance system started")
            
            print("\nSurveillance active! Press 'q' to quit, 'r' to toggle recording")
            print("-" * 50)
            
            # Start continuous recording if enabled and not detection-based
            if config.ENABLE_RECORDING and not config.RECORD_ON_DETECTION:
                self.start_recording()
            
            while self.is_running:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("Failed to read frame from camera")
                    break
                
                self.frame_count += 1
                
                # Process frame for face detection
                faces = self.process_frame(frame)
                
                # Handle detections
                if faces:
                    frame = self.handle_detection(frame, faces)
                
                # Record frame if recording
                if self.is_recording and self.video_writer:
                    self.video_writer.write(frame)
                
                # Calculate FPS
                self.calculate_fps()
                
                # Draw info overlay
                if config.SHOW_PREVIEW:
                    frame = self.draw_info_overlay(frame)
                    
                    # Display frame
                    display_frame = cv2.resize(frame, (config.PREVIEW_WIDTH, config.PREVIEW_HEIGHT))
                    cv2.imshow('AI Surveillance Camera', display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\nShutting down...")
                    break
                elif key == ord('r'):
                    if self.is_recording:
                        self.stop_recording()
                    else:
                        self.start_recording()
                elif key == ord('s'):
                    # Save current frame
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = os.path.join(config.DATA_DIR, f"screenshot_{timestamp}.jpg")
                    cv2.imwrite(screenshot_path, frame)
                    print(f"Screenshot saved: {screenshot_path}")
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        except Exception as e:
            print(f"\nError: {e}")
            self.db.log_system_event("ERROR", str(e))
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        
        self.is_running = False
        
        if self.is_recording:
            self.stop_recording()
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        self.db.log_system_event("INFO", "Surveillance system stopped")
        self.db.close()
        
        print("Cleanup complete!")

def main():
    """Main entry point"""
    try:
        surveillance = SurveillanceCamera()
        surveillance.run()
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
