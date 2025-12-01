import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import {
  Camera,
  CameraOff,
  Video,
  VideoOff,
  Image as ImageIcon,
  Users,
  AlertTriangle,
  Eye,
  Activity,
  RefreshCw
} from 'lucide-react';
import { cameraAPI, recordingAPI, reportsAPI, alertsAPI } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [cameraStatus, setCameraStatus] = useState({
    is_running: false,
    is_recording: false,
    faces_detected: 0
  });
  
  const [currentFrame, setCurrentFrame] = useState(null);
  const [statistics, setStatistics] = useState({
    total_detections: 0,
    known_persons: 0,
    detections_today: 0,
    pending_alerts: 0
  });
  
  const [recentDetections, setRecentDetections] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch camera status
  const fetchCameraStatus = useCallback(async () => {
    try {
      const response = await cameraAPI.getStatus();
      setCameraStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch camera status:', error);
    }
  }, []);

  // Fetch current frame
  const fetchFrame = useCallback(async () => {
    if (!cameraStatus.is_running) return;
    
    try {
      const response = await cameraAPI.getFrame();
      if (response.data.success) {
        setCurrentFrame(response.data.frame);
      }
    } catch (error) {
      console.error('Failed to fetch frame:', error);
    }
  }, [cameraStatus.is_running]);

  // Fetch statistics
  const fetchStatistics = useCallback(async () => {
    try {
      const response = await reportsAPI.getStatistics();
      if (response.data.success) {
        setStatistics(response.data.statistics);
      }
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  }, []);

  // Fetch recent detections
  const fetchRecentDetections = useCallback(async () => {
    try {
      const response = await reportsAPI.getDailyReport(
        new Date().toISOString().split('T')[0]
      );
      if (response.data.success) {
        setRecentDetections(response.data.intruders || []);
      }
    } catch (error) {
      console.error('Failed to fetch detections:', error);
    }
  }, []);

  // Start camera
  const handleStartCamera = async () => {
    setLoading(true);
    try {
      const response = await cameraAPI.start();
      if (response.data.success) {
        toast.success('Camera started successfully');
        fetchCameraStatus();
      } else {
        toast.error(response.data.message || 'Failed to start camera');
      }
    } catch (error) {
      toast.error('Failed to start camera');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Stop camera
  const handleStopCamera = async () => {
    setLoading(true);
    try {
      const response = await cameraAPI.stop();
      if (response.data.success) {
        toast.success('Camera stopped');
        setCameraStatus(prev => ({ ...prev, is_running: false, is_recording: false }));
        setCurrentFrame(null);
      } else {
        toast.error(response.data.message || 'Failed to stop camera');
      }
    } catch (error) {
      toast.error('Failed to stop camera');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Toggle recording
  const handleToggleRecording = async () => {
    setLoading(true);
    try {
      const response = cameraStatus.is_recording
        ? await recordingAPI.stop()
        : await recordingAPI.start();
      
      if (response.data.success) {
        toast.success(response.data.message);
        fetchCameraStatus();
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error('Failed to toggle recording');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Take snapshot
  const handleSnapshot = async () => {
    try {
      const response = await cameraAPI.takeSnapshot();
      if (response.data.success) {
        toast.success(`Snapshot saved: ${response.data.filename}`);
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error('Failed to take snapshot');
      console.error(error);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchCameraStatus();
    fetchStatistics();
    fetchRecentDetections();
  }, [fetchCameraStatus, fetchStatistics, fetchRecentDetections]);

  // Update frame periodically
  useEffect(() => {
    if (cameraStatus.is_running) {
      const interval = setInterval(fetchFrame, 500); // Update every 500ms for smooth video
      return () => clearInterval(interval);
    }
  }, [cameraStatus.is_running, fetchFrame]);

  // Update statistics periodically
  useEffect(() => {
    const interval = setInterval(() => {
      fetchStatistics();
      fetchRecentDetections();
    }, 5000); // Update every 5 seconds
    
    return () => clearInterval(interval);
  }, [fetchStatistics, fetchRecentDetections]);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p className="subtitle">Real-time surveillance monitoring</p>
        </div>
        <button className="refresh-btn" onClick={fetchStatistics}>
          <RefreshCw size={20} />
          Refresh
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon blue">
            <Eye size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{statistics.total_detections}</div>
            <div className="stat-label">Total Detections</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green">
            <Users size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{statistics.known_persons}</div>
            <div className="stat-label">Registered Students</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon orange">
            <Activity size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{statistics.detections_today}</div>
            <div className="stat-label">Today's Detections</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon red">
            <AlertTriangle size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{statistics.pending_alerts}</div>
            <div className="stat-label">Pending Alerts</div>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Camera Feed Section */}
        <div className="camera-section">
          <div className="section-card">
            <div className="card-header">
              <h2>Live Camera Feed</h2>
              <div className="status-badge">
                <div className={`status-dot ${cameraStatus.is_running ? 'active' : ''}`}></div>
                {cameraStatus.is_running ? 'Active' : 'Inactive'}
              </div>
            </div>

            <div className="camera-feed">
              {currentFrame ? (
                <img src={currentFrame} alt="Camera feed" className="feed-image" />
              ) : (
                <div className="feed-placeholder">
                  <CameraOff size={64} />
                  <p>Camera is not active</p>
                  <p className="feed-hint">Start the camera to view live feed</p>
                </div>
              )}
              
              {cameraStatus.is_recording && (
                <div className="recording-indicator">
                  <div className="rec-dot"></div>
                  REC
                </div>
              )}
              
              {cameraStatus.faces_detected > 0 && (
                <div className="faces-counter">
                  <Users size={16} />
                  {cameraStatus.faces_detected} face{cameraStatus.faces_detected !== 1 ? 's' : ''} detected
                </div>
              )}
            </div>

            <div className="camera-controls">
              {!cameraStatus.is_running ? (
                <button
                  className="control-btn primary"
                  onClick={handleStartCamera}
                  disabled={loading}
                >
                  <Camera size={20} />
                  Start Camera
                </button>
              ) : (
                <>
                  <button
                    className="control-btn danger"
                    onClick={handleStopCamera}
                    disabled={loading}
                  >
                    <CameraOff size={20} />
                    Stop Camera
                  </button>
                  
                  <button
                    className={`control-btn ${cameraStatus.is_recording ? 'warning' : 'success'}`}
                    onClick={handleToggleRecording}
                    disabled={loading}
                  >
                    {cameraStatus.is_recording ? (
                      <>
                        <VideoOff size={20} />
                        Stop Recording
                      </>
                    ) : (
                      <>
                        <Video size={20} />
                        Start Recording
                      </>
                    )}
                  </button>
                  
                  <button
                    className="control-btn secondary"
                    onClick={handleSnapshot}
                  >
                    <ImageIcon size={20} />
                    Snapshot
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Recent Activity Section */}
        <div className="activity-section">
          <div className="section-card">
            <div className="card-header">
              <h2>Recent Intruder Detections</h2>
            </div>

            <div className="activity-list">
              {recentDetections.length === 0 ? (
                <div className="empty-state">
                  <AlertTriangle size={48} />
                  <p>No intruders detected today</p>
                </div>
              ) : (
                recentDetections.slice(0, 5).map((detection, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-icon danger">
                      <AlertTriangle size={20} />
                    </div>
                    <div className="activity-content">
                      <div className="activity-title">Intruder Detected</div>
                      <div className="activity-time">
                        {new Date(detection.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                    <div className="activity-badge danger">Alert</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
