import React, { useState, useEffect, useRef } from 'react';
import { toast } from 'react-toastify';
import {
  UserPlus,
  Search,
  Trash2,
  Eye,
  Camera,
  Upload,
  X
} from 'lucide-react';
import { studentsAPI, detectionsAPI } from '../services/api';
import './Students.css';

const Students = () => {
  const [students, setStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  // Fetch students
  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await studentsAPI.getAll();
      console.log('Students response:', response.data);
      if (response.data.success) {
        setStudents(response.data.students || []);
      } else {
        toast.error('Failed to load students: ' + response.data.message);
      }
    } catch (error) {
      console.error('Failed to fetch students:', error);
      toast.error('Failed to load students');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  // Filter students based on search
  const filteredStudents = students.filter(student =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Delete student
  const handleDeleteStudent = async (studentId, studentName) => {
    if (!window.confirm(`Are you sure you want to delete ${studentName}?`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await studentsAPI.delete(studentId);
      if (response.data.success) {
        toast.success(`${studentName} deleted successfully`);
        fetchStudents();
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error('Failed to delete student');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // View student details
  const handleViewDetails = async (student) => {
    setSelectedStudent(student);
    setShowDetailsModal(true);
    
    try {
      const response = await detectionsAPI.getByStudent(student.name);
      if (response.data.success) {
        setSelectedStudent(prev => ({
          ...prev,
          detections: response.data.detections
        }));
      }
    } catch (error) {
      console.error('Failed to fetch student detections:', error);
    }
  };

  return (
    <div className="students-page">
      <div className="page-header">
        <div>
          <h1>Student Management</h1>
          <p className="subtitle">Manage registered students and their face data</p>
        </div>
        <button
          className="add-student-btn"
          onClick={() => setShowAddModal(true)}
        >
          <UserPlus size={20} />
          Add Student
        </button>
      </div>

      {/* Search Bar */}
      <div className="search-bar">
        <Search size={20} />
        <input
          type="text"
          placeholder="Search students by name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Students Grid */}
      <div className="students-grid">
        {filteredStudents.length === 0 ? (
          <div className="empty-state">
            <UserPlus size={64} />
            <p>No students found</p>
            <button
              className="add-first-btn"
              onClick={() => setShowAddModal(true)}
            >
              Add your first student
            </button>
          </div>
        ) : (
          filteredStudents.map((student) => (
            <div key={student.id} className="student-card">
              <div className="student-image">
                {student.image_path ? (
                  <img
                    src={`http://localhost:5000/api/images/${student.image_path.split(/[/\\]/).pop()}`}
                    alt={student.name}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className="student-placeholder">
                  {student.name.charAt(0).toUpperCase()}
                </div>
              </div>
              
              <div className="student-info">
                <h3>{student.name}</h3>
                <p className="student-date">
                  Added: {new Date(student.date_added).toLocaleDateString()}
                </p>
                {student.notes && (
                  <p className="student-notes">{student.notes}</p>
                )}
              </div>

              <div className="student-actions">
                <button
                  className="action-btn view"
                  onClick={() => handleViewDetails(student)}
                  title="View Details"
                >
                  <Eye size={18} />
                </button>
                <button
                  className="action-btn delete"
                  onClick={() => handleDeleteStudent(student.id, student.name)}
                  disabled={loading}
                  title="Delete Student"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Student Modal */}
      {showAddModal && (
        <AddStudentModal
          onClose={() => setShowAddModal(false)}
          onSuccess={async () => {
            setShowAddModal(false);
            // Wait a moment for backend to process
            setTimeout(async () => {
              await fetchStudents();
              toast.success('Student list refreshed');
            }, 500);
          }}
        />
      )}

      {/* Student Details Modal */}
      {showDetailsModal && selectedStudent && (
        <StudentDetailsModal
          student={selectedStudent}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedStudent(null);
          }}
        />
      )}
    </div>
  );
};

// Add Student Modal Component
const AddStudentModal = ({ onClose, onSuccess }) => {
  const [name, setName] = useState('');
  const [notes, setNotes] = useState('');
  const [imageData, setImageData] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [useCamera, setUseCamera] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImageData(reader.result);
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      streamRef.current = stream;
      setUseCamera(true);
    } catch (error) {
      toast.error('Failed to access camera');
      console.error(error);
    }
  };

  const capturePhoto = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    const dataUrl = canvas.toDataURL('image/jpeg');
    setImageData(dataUrl);
    setImagePreview(dataUrl);
    
    stopCamera();
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setUseCamera(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name.trim()) {
      toast.error('Please enter student name');
      return;
    }
    
    if (!imageData) {
      toast.error('Please provide a face image');
      return;
    }

    setLoading(true);
    try {
      const response = await studentsAPI.add({
        name: name.trim(),
        notes: notes.trim(),
        image: imageData
      });

      if (response.data.success) {
        toast.success(response.data.message || 'Student added successfully');
        // Close modal and cleanup first
        stopCamera();
        // Call success callback to refresh the list
        onSuccess();
      } else {
        toast.error(response.data.message || 'Failed to add student');
      }
    } catch (error) {
      toast.error('Failed to add student: ' + (error.response?.data?.message || error.message));
      console.error('Add student error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add New Student</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label>Student Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter student name"
              required
            />
          </div>

          <div className="form-group">
            <label>Notes (Optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any notes about the student"
              rows="3"
            />
          </div>

          <div className="form-group">
            <label>Face Image *</label>
            
            {!imagePreview && !useCamera && (
              <div className="image-upload-options">
                <label className="upload-btn">
                  <Upload size={20} />
                  Upload Photo
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    hidden
                  />
                </label>
                
                <button
                  type="button"
                  className="camera-btn"
                  onClick={startCamera}
                >
                  <Camera size={20} />
                  Use Camera
                </button>
              </div>
            )}

            {useCamera && (
              <div className="camera-preview">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="video-preview"
                />
                <canvas ref={canvasRef} style={{ display: 'none' }} />
                <div className="camera-controls">
                  <button
                    type="button"
                    className="capture-btn"
                    onClick={capturePhoto}
                  >
                    <Camera size={20} />
                    Capture
                  </button>
                  <button
                    type="button"
                    className="cancel-btn"
                    onClick={stopCamera}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {imagePreview && !useCamera && (
              <div className="image-preview">
                <img src={imagePreview} alt="Preview" />
                <button
                  type="button"
                  className="remove-image-btn"
                  onClick={() => {
                    setImageData(null);
                    setImagePreview(null);
                  }}
                >
                  <X size={20} />
                  Remove
                </button>
              </div>
            )}
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="cancel-form-btn"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="submit-btn"
              disabled={loading}
            >
              {loading ? 'Adding...' : 'Add Student'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Student Details Modal Component
const StudentDetailsModal = ({ student, onClose }) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Student Details</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="details-content">
          <div className="details-header">
            <div className="details-image">
              {student.image_path ? (
                <img
                  src={`http://localhost:5000/api/images/${student.image_path.split(/[/\\]/).pop()}`}
                  alt={student.name}
                />
              ) : (
                <div className="details-placeholder">
                  {student.name.charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            <div className="details-info">
              <h3>{student.name}</h3>
              <p>Added: {new Date(student.date_added).toLocaleDateString()}</p>
              {student.notes && <p className="notes">{student.notes}</p>}
            </div>
          </div>

          <div className="detection-history">
            <h4>Detection History</h4>
            {student.detections && student.detections.length > 0 ? (
              <div className="detections-list">
                {student.detections.slice(0, 10).map((detection, index) => (
                  <div key={index} className="detection-item">
                    <div className="detection-time">
                      {new Date(detection.timestamp).toLocaleString()}
                    </div>
                    <div className="detection-confidence">
                      Confidence: {(detection.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-detections">No detections recorded yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Students;
