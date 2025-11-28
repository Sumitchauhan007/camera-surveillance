"""
Sync face detector pickle file with database
This fixes the issue where faces are in pickle but not in database
"""
import sys
import os
sys.path.append('.')

from face_detector import FaceDetector
from database import SurveillanceDB

print("\n" + "="*60)
print("SYNCING FACE DETECTOR WITH DATABASE")
print("="*60)

# Load face detector
print("\nLoading face detector...")
fd = FaceDetector()
print(f"✅ Face detector has {len(fd.known_faces)} known faces")

# Load database
print("\nLoading database...")
db = SurveillanceDB()
students = db.get_known_persons()
print(f"✅ Database has {len(students)} students")

# Get names from database
db_names = {student[1] for student in students}  # student[1] is name
print(f"\nDatabase names: {db_names}")

# Get names from face detector
fd_names = set(fd.known_faces.keys())
print(f"Face detector names: {fd_names}")

# Find faces that are in pickle but not in database
missing_in_db = fd_names - db_names

if missing_in_db:
    print(f"\n⚠️ Found {len(missing_in_db)} faces in detector but not in database:")
    for name in missing_in_db:
        print(f"   - {name}")
    
    print("\n" + "="*60)
    print("OPTIONS:")
    print("="*60)
    print("1. Delete these from face detector (clean up)")
    print("2. Add these to database (if you want to keep them)")
    print("3. Cancel")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🗑️ Removing extra faces from face detector...")
        for name in missing_in_db:
            if name in fd.known_faces:
                del fd.known_faces[name]
                print(f"   Removed: {name}")
        
        # Save updated pickle
        fd.save_known_faces()
        print("✅ Face detector cleaned up and saved")
        
    elif choice == "2":
        print("\n💾 Adding faces to database...")
        for name in missing_in_db:
            # Try to find image path
            image_path = os.path.join("data", "known_faces", f"{name}.jpg")
            if not os.path.exists(image_path):
                # Try with timestamp pattern
                import glob
                pattern = os.path.join("data", "known_faces", f"{name}*.jpg")
                matches = glob.glob(pattern)
                image_path = matches[0] if matches else None
            
            if image_path:
                db.add_known_person(name, image_path, f"Synced from face detector")
                print(f"   Added: {name}")
            else:
                print(f"   ⚠️ Skipped {name} - no image found")
        
        print("✅ Database updated")
    else:
        print("❌ Cancelled")
else:
    print("\n✅ Face detector and database are in sync!")

# Show final counts
students = db.get_known_persons()
print(f"\n" + "="*60)
print(f"FINAL STATE:")
print(f"="*60)
print(f"Database: {len(students)} students")
print(f"Face detector: {len(fd.known_faces)} known faces")
print("="*60 + "\n")
