"""
Test script to verify students database
"""
import sys
sys.path.append('.')

from database import SurveillanceDB

db = SurveillanceDB()

print("\n" + "="*50)
print("Students Database Test")
print("="*50)

# Get all students
students = db.get_known_persons()

print(f"\nTotal students in database: {len(students)}")

if students:
    print("\nStudents list:")
    print("-" * 50)
    for student in students:
        print(f"ID: {student[0]}")
        print(f"Name: {student[1]}")
        print(f"Date Added: {student[2]}")
        print(f"Image Path: {student[3]}")
        print(f"Notes: {student[4]}")
        print("-" * 50)
else:
    print("\n⚠️ No students found in database")
    print("Try adding a student through the web interface")

print("\n" + "="*50)
