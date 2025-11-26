"""
Quick start script to test camera and face detection
"""
import cv2
from insightface.app import FaceAnalysis
import numpy as np

def test_camera():
    """Test if camera is accessible"""
    print("Testing camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Cannot access camera")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print("❌ Error: Cannot read from camera")
        cap.release()
        return False
    
    print(f"✓ Camera working: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
    return True

def test_insightface():
    """Test InsightFace installation"""
    print("\nTesting InsightFace...")
    try:
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        print("✓ InsightFace initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing InsightFace: {e}")
        return False

def test_face_detection():
    """Test face detection with camera"""
    print("\nTesting face detection...")
    print("Press 'q' to quit, 'c' to capture and test detection")
    
    try:
        cap = cv2.VideoCapture(0)
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect faces
            faces = app.get(frame)
            
            # Draw boxes
            for face in faces:
                bbox = face.bbox.astype(int)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                
                # Draw landmarks
                if hasattr(face, 'kps') and face.kps is not None:
                    for kp in face.kps:
                        cv2.circle(frame, (int(kp[0]), int(kp[1])), 2, (255, 255, 0), -1)
            
            # Display count
            cv2.putText(frame, f"Faces: {len(faces)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Face Detection Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                if len(faces) > 0:
                    print(f"✓ Detected {len(faces)} face(s)")
                else:
                    print("❌ No faces detected")
        
        cap.release()
        cv2.destroyAllWindows()
        print("✓ Face detection test complete")
        
    except Exception as e:
        print(f"❌ Error during face detection test: {e}")
        return False
    
    return True

def main():
    print("=" * 50)
    print("AI Surveillance System - Quick Test")
    print("=" * 50)
    
    # Run tests
    camera_ok = test_camera()
    insightface_ok = test_insightface()
    
    if camera_ok and insightface_ok:
        print("\n✓ All basic tests passed!")
        print("\nStarting live face detection test...")
        test_face_detection()
    else:
        print("\n❌ Some tests failed. Please fix the issues before running the main application.")
        return
    
    print("\n" + "=" * 50)
    print("Setup verification complete!")
    print("You can now run:")
    print("  - python main.py  (command-line mode)")
    print("  - python gui.py   (GUI dashboard)")
    print("=" * 50)

if __name__ == "__main__":
    main()
