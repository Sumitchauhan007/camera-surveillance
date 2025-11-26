import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import {
  Bell,
  AlertTriangle,
  CheckCircle,
  X,
  RefreshCw
} from 'lucide-react';
import { alertsAPI } from '../services/api';
import './Alerts.css';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all'); // all, unacknowledged

  // Fetch alerts
  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await alertsAPI.getAll();
      if (response.data.success) {
        setAlerts(response.data.alerts);
      }
    } catch (error) {
      toast.error('Failed to fetch alerts');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  // Acknowledge alert
  const handleAcknowledge = async (alertId) => {
    try {
      const response = await alertsAPI.acknowledge(alertId);
      if (response.data.success) {
        toast.success('Alert acknowledged');
        fetchAlerts();
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error('Failed to acknowledge alert');
      console.error(error);
    }
  };

  // Filter alerts
  const filteredAlerts = filter === 'all'
    ? alerts
    : alerts.filter(alert => alert.acknowledged === 0);

  const unacknowledgedCount = alerts.filter(a => a.acknowledged === 0).length;

  return (
    <div className="alerts-page">
      <div className="page-header">
        <div>
          <h1>Alerts & Notifications</h1>
          <p className="subtitle">
            Manage system alerts and intruder notifications
          </p>
        </div>
        <button className="refresh-btn" onClick={fetchAlerts} disabled={loading}>
          <RefreshCw size={20} className={loading ? 'spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Alert Stats */}
      <div className="alert-stats">
        <div className="stat-item">
          <Bell size={20} />
          <span className="stat-count">{alerts.length}</span>
          <span className="stat-label">Total Alerts</span>
        </div>
        <div className="stat-item warning">
          <AlertTriangle size={20} />
          <span className="stat-count">{unacknowledgedCount}</span>
          <span className="stat-label">Unacknowledged</span>
        </div>
        <div className="stat-item success">
          <CheckCircle size={20} />
          <span className="stat-count">{alerts.length - unacknowledgedCount}</span>
          <span className="stat-label">Acknowledged</span>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="alert-filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Alerts ({alerts.length})
        </button>
        <button
          className={`filter-btn ${filter === 'unacknowledged' ? 'active' : ''}`}
          onClick={() => setFilter('unacknowledged')}
        >
          Unacknowledged ({unacknowledgedCount})
        </button>
      </div>

      {/* Alerts List */}
      <div className="alerts-list">
        {filteredAlerts.length === 0 ? (
          <div className="empty-state">
            <Bell size={64} />
            <p>
              {filter === 'all'
                ? 'No alerts to display'
                : 'No unacknowledged alerts'}
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`alert-item ${alert.acknowledged ? 'acknowledged' : 'unacknowledged'}`}
            >
              <div className="alert-icon">
                {alert.alert_type === 'INTRUDER' || alert.alert_type === 'UNKNOWN_PERSON' ? (
                  <AlertTriangle size={24} />
                ) : (
                  <Bell size={24} />
                )}
              </div>

              <div className="alert-content">
                <div className="alert-header">
                  <h3>{getAlertTitle(alert.alert_type)}</h3>
                  <span className="alert-time">
                    {formatTimestamp(alert.timestamp)}
                  </span>
                </div>

                <p className="alert-description">
                  {alert.description || 'No description provided'}
                </p>

                {alert.person_id && (
                  <div className="alert-details">
                    <span className="detail-label">Person ID:</span>
                    <span className="detail-value">{alert.person_id}</span>
                  </div>
                )}

                {!alert.acknowledged && (
                  <button
                    className="acknowledge-btn"
                    onClick={() => handleAcknowledge(alert.id)}
                  >
                    <CheckCircle size={16} />
                    Acknowledge
                  </button>
                )}
              </div>

              {alert.acknowledged ? (
                <div className="acknowledged-badge">
                  <CheckCircle size={16} />
                  Acknowledged
                </div>
              ) : (
                <div className="alert-status pending">
                  Pending
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// Helper functions
const getAlertTitle = (type) => {
  const titles = {
    'INTRUDER': 'Intruder Detected',
    'UNKNOWN_PERSON': 'Unknown Person Detected',
    'SYSTEM': 'System Alert',
    'WARNING': 'Warning',
  };
  return titles[type] || 'Alert';
};

const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
};

export default Alerts;
