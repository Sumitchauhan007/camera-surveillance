"""
Face Detection and Recognition Module using InsightFace
"""
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
import os
import pickle
from datetime import datetime
import config

class FaceDetector:
    def __init__(self):
        """Initialize InsightFace with RetinaFace detector"""
        print("Initializing InsightFace...")
        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        
        self.known_faces = {}  # Dictionary to store known face embeddings
        self.load_known_faces()
        print(f"Face detector initialized. Loaded {len(self.known_faces)} known faces.")
    
    def detect_faces(self, frame):
        """
        Detect faces in the frame using RetinaFace
        Returns list of face objects with bounding boxes and embeddings
        """
        faces = self.app.get(frame)
        return faces
    
    def get_face_embedding(self, face):
        """Extract face embedding from detected face"""
        return face.embedding
    
    def recognize_face(self, face_embedding):
        """
        Compare face embedding with known faces
        Returns (name, similarity) or (None, 0) if unknown
        """
        if not self.known_faces:
            return None, 0
        
        max_similarity = 0
        recognized_name = None
        
        for name, known_embedding in self.known_faces.items():
            # Calculate cosine similarity
            similarity = self.compute_similarity(face_embedding, known_embedding)
            
            if similarity > max_similarity and similarity > config.RECOGNITION_THRESHOLD:
                max_similarity = similarity
                recognized_name = name
        
        return recognized_name, max_similarity
    
    def compute_similarity(self, embedding1, embedding2):
        """Compute cosine similarity between two embeddings"""
        embedding1 = np.array(embedding1).flatten()
        embedding2 = np.array(embedding2).flatten()
        
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        return similarity
    
    def save_face_image(self, frame, face, person_id):
        """Save detected face image"""
        bbox = face.bbox.astype(int)
        x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
        
        # Add padding
        padding = 20
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(frame.shape[1], x2 + padding)
        y2 = min(frame.shape[0], y2 + padding)
        
        face_img = frame[y1:y2, x1:x2]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{person_id}_{timestamp}.jpg"
        filepath = os.path.join(config.FACES_DIR, filename)
        
        cv2.imwrite(filepath, face_img)
        return filepath
    
    def add_known_face(self, name, image_path):
        """Add a new known face from an image"""
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not read image {image_path}")
            return False
        
        faces = self.detect_faces(img)
        
        if len(faces) == 0:
            print(f"No face detected in {image_path}")
            return False
        
        if len(faces) > 1:
            print(f"Multiple faces detected in {image_path}. Using the first one.")
        
        # Use the first detected face
        embedding = self.get_face_embedding(faces[0])
        self.known_faces[name] = embedding
        
        # Save to disk
        self.save_known_faces()
        print(f"Added known face: {name}")
        return True
    
    def load_known_faces(self):
        """Load known faces from disk"""
        known_faces_file = os.path.join(config.DATA_DIR, 'known_faces.pkl')
        
        if os.path.exists(known_faces_file):
            try:
                with open(known_faces_file, 'rb') as f:
                    self.known_faces = pickle.load(f)
            except Exception as e:
                print(f"Error loading known faces: {e}")
                self.known_faces = {}
        
        # Also scan known_faces directory for new images
        if os.path.exists(config.KNOWN_FACES_DIR):
            for filename in os.listdir(config.KNOWN_FACES_DIR):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    name = os.path.splitext(filename)[0]
                    if name not in self.known_faces:
                        filepath = os.path.join(config.KNOWN_FACES_DIR, filename)
                        self.add_known_face(name, filepath)
    
    def save_known_faces(self):
        """Save known faces to disk"""
        known_faces_file = os.path.join(config.DATA_DIR, 'known_faces.pkl')
        try:
            with open(known_faces_file, 'wb') as f:
                pickle.dump(self.known_faces, f)
        except Exception as e:
            print(f"Error saving known faces: {e}")
    
    def draw_face_box(self, frame, face, name=None, similarity=0):
        """Draw bounding box and label on frame"""
        bbox = face.bbox.astype(int)
        x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
        
        # Choose color based on recognition
        if name:
            color = (0, 255, 0)  # Green for known
            label = f"{name} ({similarity:.2f})"
        else:
            color = (0, 0, 255)  # Red for unknown
            label = "Unknown"
        
        # Draw rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), color, -1)
        
        # Draw label text
        cv2.putText(frame, label, (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw landmarks if available
        if hasattr(face, 'kps') and face.kps is not None:
            for kp in face.kps:
                cv2.circle(frame, (int(kp[0]), int(kp[1])), 2, (255, 255, 0), -1)
        
        return frame
