import React from 'react';
import { toast } from 'react-toastify';
import {
  Settings as SettingsIcon,
  Camera,
  Shield,
  Bell,
  Save
} from 'lucide-react';
import './Settings.css';

const Settings = () => {
  const handleSave = () => {
    toast.success('Settings saved successfully');
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p className="subtitle">Configure system parameters and preferences</p>
        </div>
      </div>

      <div className="settings-grid">
        {/* Camera Settings */}
        <div className="settings-section">
          <div className="section-header">
            <Camera size={24} />
            <h2>Camera Settings</h2>
          </div>

          <div className="setting-item">
            <label>Camera ID</label>
            <input type="text" defaultValue="0" placeholder="0 or RTSP URL" />
            <p className="setting-hint">Camera device ID or RTSP stream URL</p>
          </div>

          <div className="setting-row">
            <div className="setting-item">
              <label>Resolution Width</label>
              <input type="number" defaultValue="1280" />
            </div>
            <div className="setting-item">
              <label>Resolution Height</label>
              <input type="number" defaultValue="720" />
            </div>
          </div>

          <div className="setting-item">
            <label>Frame Rate (FPS)</label>
            <input type="number" defaultValue="30" min="1" max="60" />
          </div>
        </div>

        {/* Detection Settings */}
        <div className="settings-section">
          <div className="section-header">
            <Shield size={24} />
            <h2>Detection Settings</h2>
          </div>

          <div className="setting-item">
            <label>Detection Confidence Threshold</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              defaultValue="0.5"
            />
            <p className="setting-hint">Minimum confidence for face detection (0.5)</p>
          </div>

          <div className="setting-item">
            <label>Recognition Threshold</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              defaultValue="0.6"
            />
            <p className="setting-hint">Similarity threshold for face recognition (0.6)</p>
          </div>

          <div className="setting-item">
            <label>Detection Interval (frames)</label>
            <input type="number" defaultValue="1" min="1" max="10" />
            <p className="setting-hint">Process every Nth frame for better performance</p>
          </div>

          <div className="setting-item">
            <label>Minimum Face Size (pixels)</label>
            <input type="number" defaultValue="30" min="10" max="200" />
          </div>
        </div>

        {/* Alert Settings */}
        <div className="settings-section">
          <div className="section-header">
            <Bell size={24} />
            <h2>Alert Settings</h2>
          </div>

          <div className="setting-item">
            <label className="checkbox-label">
              <input type="checkbox" defaultChecked />
              <span>Enable Alerts</span>
            </label>
          </div>

          <div className="setting-item">
            <label className="checkbox-label">
              <input type="checkbox" defaultChecked />
              <span>Alert on Unknown Person</span>
            </label>
          </div>

          <div className="setting-item">
            <label>Alert Cooldown (seconds)</label>
            <input type="number" defaultValue="60" min="10" max="300" />
            <p className="setting-hint">Minimum time between alerts for the same person</p>
          </div>
        </div>

        {/* Recording Settings */}
        <div className="settings-section">
          <div className="section-header">
            <SettingsIcon size={24} />
            <h2>Recording Settings</h2>
          </div>

          <div className="setting-item">
            <label className="checkbox-label">
              <input type="checkbox" defaultChecked />
              <span>Enable Recording</span>
            </label>
          </div>

          <div className="setting-item">
            <label className="checkbox-label">
              <input type="checkbox" defaultChecked />
              <span>Record Only on Detection</span>
            </label>
          </div>

          <div className="setting-item">
            <label>Max Recording Duration (seconds)</label>
            <input type="number" defaultValue="300" min="60" max="3600" />
          </div>

          <div className="setting-item">
            <label>Video Codec</label>
            <select defaultValue="mp4v">
              <option value="mp4v">MP4V</option>
              <option value="XVID">XVID</option>
              <option value="H264">H264</option>
            </select>
          </div>
        </div>

        {/* System Info */}
        <div className="settings-section">
          <div className="section-header">
            <SettingsIcon size={24} />
            <h2>System Information</h2>
          </div>

          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Version:</span>
              <span className="info-value">1.0.0</span>
            </div>
            <div className="info-item">
              <span className="info-label">Backend:</span>
              <span className="info-value">Flask API</span>
            </div>
            <div className="info-item">
              <span className="info-label">Face Detection:</span>
              <span className="info-value">InsightFace RetinaFace</span>
            </div>
            <div className="info-item">
              <span className="info-label">Database:</span>
              <span className="info-value">SQLite</span>
            </div>
          </div>
        </div>

        {/* About */}
        <div className="settings-section">
          <div className="section-header">
            <Shield size={24} />
            <h2>About</h2>
          </div>

          <p className="about-text">
            AI Surveillance System is a comprehensive face detection and recognition
            platform powered by InsightFace and RetinaFace. It provides real-time
            monitoring, student management, intruder detection, and detailed reporting.
          </p>

          <div className="about-links">
            <button className="link-btn">Documentation</button>
            <button className="link-btn">Support</button>
            <button className="link-btn">License</button>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="settings-actions">
        <button className="save-btn" onClick={handleSave}>
          <Save size={20} />
          Save Settings
        </button>
      </div>
    </div>
  );
};

export default Settings;
