import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import {
  Settings as SettingsIcon,
  Camera,
  Shield,
  Bell,
  Save,
  RefreshCw
} from 'lucide-react';
import api from '../services/api';
import './Settings.css';

const Settings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    camera_id: '0',
    camera_width: 640,
    camera_height: 480,
    detection_interval: 5,
    recognition_threshold: 0.4,
    enable_alerts: true,
    alert_cooldown: 300,
    enable_recording: false,
    recording_duration: 30,
    max_storage_gb: 50
  });

  // Load settings from backend on mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/settings');
      
      if (response.data.success) {
        setSettings(response.data.settings);
        toast.info('Settings loaded');
      } else {
        toast.error('Failed to load settings');
      }
    } catch (error) {
      console.error('Error loading settings:', error);
      toast.error('Error loading settings: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await api.put('/settings', settings);
      
      if (response.data.success) {
        toast.success(`Settings saved successfully (${response.data.updated_count} settings updated)`);
      } else {
        toast.error('Failed to save settings: ' + response.data.error);
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Error saving settings: ' + (error.response?.data?.error || error.message));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="settings-page">
        <div className="page-header">
          <h1>Settings</h1>
          <p className="subtitle">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p className="subtitle">Configure system parameters and preferences</p>
        </div>
        <button className="refresh-btn" onClick={loadSettings} disabled={loading}>
          <RefreshCw size={20} />
          Reload
        </button>
      </div>

      <div className="settings-grid">
        {/* Camera Settings  need to be changed*/}
        <div className="settings-section">
          <div className="section-header">
            <Camera size={24} />
            <h2>Camera Settings</h2>
          </div>

          <div className="setting-item">
            <label>Camera ID</label>
            <input 
              type="text" 
              value={settings.camera_id}
              onChange={(e) => handleChange('camera_id', e.target.value)}
              placeholder="0 or RTSP URL" 
            />
            <p className="setting-hint">Camera device ID or RTSP stream URL</p>
          </div>

          <div className="setting-row">
            <div className="setting-item">
              <label>Resolution Width</label>
              <input 
                type="number" 
                value={settings.camera_width}
                onChange={(e) => handleChange('camera_width', parseInt(e.target.value) || 640)}
              />
            </div>
            <div className="setting-item">
              <label>Resolution Height</label>
              <input 
                type="number" 
                value={settings.camera_height}
                onChange={(e) => handleChange('camera_height', parseInt(e.target.value) || 480)}
              />
            </div>
          </div>
        </div>

        {/* Detection Settings */}
        <div className="settings-section">
          <div className="section-header">
            <Shield size={24} />
            <h2>Detection Settings</h2>
          </div>

          <div className="setting-item">
            <label>Recognition Threshold</label>
            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.05"
              value={settings.recognition_threshold}
              onChange={(e) => handleChange('recognition_threshold', parseFloat(e.target.value))}
            />
            <p className="setting-hint">
              Similarity threshold for face recognition ({settings.recognition_threshold.toFixed(2)})
            </p>
          </div>

          <div className="setting-item">
            <label>Detection Interval (seconds)</label>
            <input 
              type="number" 
              value={settings.detection_interval}
              onChange={(e) => handleChange('detection_interval', parseInt(e.target.value) || 5)}
              min="1" 
              max="30" 
            />
            <p className="setting-hint">Time between detection cycles</p>
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
              <input 
                type="checkbox" 
                checked={settings.enable_alerts}
                onChange={(e) => handleChange('enable_alerts', e.target.checked)}
              />
              <span>Enable Alerts</span>
            </label>
          </div>

          <div className="setting-item">
            <label>Alert Cooldown (seconds)</label>
            <input 
              type="number" 
              value={settings.alert_cooldown}
              onChange={(e) => handleChange('alert_cooldown', parseInt(e.target.value) || 300)}
              min="10" 
              max="3600" 
            />
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
              <input 
                type="checkbox" 
                checked={settings.enable_recording}
                onChange={(e) => handleChange('enable_recording', e.target.checked)}
              />
              <span>Enable Recording</span>
            </label>
          </div>

          <div className="setting-item">
            <label>Recording Duration (seconds)</label>
            <input 
              type="number" 
              value={settings.recording_duration}
              onChange={(e) => handleChange('recording_duration', parseInt(e.target.value) || 30)}
              min="10" 
              max="600" 
            />
          </div>

          <div className="setting-item">
            <label>Max Storage (GB)</label>
            <input 
              type="number" 
              value={settings.max_storage_gb}
              onChange={(e) => handleChange('max_storage_gb', parseInt(e.target.value) || 50)}
              min="1" 
              max="1000" 
            />
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
        </div>
      </div>

      {/* Save Button */}
      <div className="settings-actions">
        <button 
          className="save-btn" 
          onClick={handleSave}
          disabled={saving}
        >
          <Save size={20} />
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
};

export default Settings;

