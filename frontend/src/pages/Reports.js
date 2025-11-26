import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import {
  FileText,
  Calendar,
  Users,
  AlertTriangle,
  Download,
  Filter
} from 'lucide-react';
import { reportsAPI } from '../services/api';
import './Reports.css';

const Reports = () => {
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [dailyReport, setDailyReport] = useState(null);
  const [intruderReport, setIntruderReport] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('daily');

  // Fetch daily report
  const fetchDailyReport = async (date) => {
    setLoading(true);
    try {
      const response = await reportsAPI.getDailyReport(date);
      if (response.data.success) {
        setDailyReport(response.data);
      }
    } catch (error) {
      toast.error('Failed to fetch daily report');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch intruder report
  const fetchIntruderReport = async () => {
    setLoading(true);
    try {
      const response = await reportsAPI.getIntruderReport();
      if (response.data.success) {
        setIntruderReport(response.data.intruders);
      }
    } catch (error) {
      toast.error('Failed to fetch intruder report');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'daily') {
      fetchDailyReport(selectedDate);
    } else {
      fetchIntruderReport();
    }
  }, [activeTab, selectedDate]);

  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
  };

  const exportReport = () => {
    toast.info('Export functionality coming soon');
  };

  return (
    <div className="reports-page">
      <div className="page-header">
        <div>
          <h1>Reports & Analytics</h1>
          <p className="subtitle">View detailed reports and detection history</p>
        </div>
        <button className="export-btn" onClick={exportReport}>
          <Download size={20} />
          Export Report
        </button>
      </div>

      {/* Tabs */}
      <div className="report-tabs">
        <button
          className={`tab-btn ${activeTab === 'daily' ? 'active' : ''}`}
          onClick={() => setActiveTab('daily')}
        >
          <Calendar size={20} />
          Daily Report
        </button>
        <button
          className={`tab-btn ${activeTab === 'intruders' ? 'active' : ''}`}
          onClick={() => setActiveTab('intruders')}
        >
          <AlertTriangle size={20} />
          Intruder History
        </button>
      </div>

      {/* Daily Report Tab */}
      {activeTab === 'daily' && (
        <div className="report-content">
          <div className="date-selector">
            <Calendar size={20} />
            <input
              type="date"
              value={selectedDate}
              onChange={handleDateChange}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>

          {loading ? (
            <div className="loading-state">Loading report...</div>
          ) : dailyReport ? (
            <>
              {/* Summary Cards */}
              <div className="summary-cards">
                <div className="summary-card">
                  <div className="summary-icon blue">
                    <FileText size={24} />
                  </div>
                  <div className="summary-content">
                    <div className="summary-value">{dailyReport.total_detections}</div>
                    <div className="summary-label">Total Detections</div>
                  </div>
                </div>

                <div className="summary-card">
                  <div className="summary-icon green">
                    <Users size={24} />
                  </div>
                  <div className="summary-content">
                    <div className="summary-value">
                      {Object.keys(dailyReport.students || {}).length}
                    </div>
                    <div className="summary-label">Students Detected</div>
                  </div>
                </div>

                <div className="summary-card">
                  <div className="summary-icon red">
                    <AlertTriangle size={24} />
                  </div>
                  <div className="summary-content">
                    <div className="summary-value">
                      {(dailyReport.intruders || []).length}
                    </div>
                    <div className="summary-label">Intruders Detected</div>
                  </div>
                </div>
              </div>

              {/* Students Table */}
              {dailyReport.students && Object.keys(dailyReport.students).length > 0 && (
                <div className="report-section">
                  <h3>Student Detections</h3>
                  <div className="data-table">
                    <table>
                      <thead>
                        <tr>
                          <th>Student Name</th>
                          <th>Detection Count</th>
                          <th>First Seen</th>
                          <th>Last Seen</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(dailyReport.students).map(([name, data]) => (
                          <tr key={name}>
                            <td className="name-cell">{name}</td>
                            <td>{data.count}</td>
                            <td>{new Date(data.first_seen).toLocaleTimeString()}</td>
                            <td>{new Date(data.last_seen).toLocaleTimeString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Intruders Section */}
              {dailyReport.intruders && dailyReport.intruders.length > 0 && (
                <div className="report-section">
                  <h3>Intruder Detections</h3>
                  <div className="intruders-grid">
                    {dailyReport.intruders.map((intruder, index) => (
                      <div key={index} className="intruder-card">
                        <div className="intruder-image">
                          {intruder.face_image_path ? (
                            <img
                              src={`http://localhost:5000/api/images/${intruder.face_image_path.split(/[/\\]/).pop()}`}
                              alt="Intruder"
                            />
                          ) : (
                            <div className="intruder-placeholder">
                              <AlertTriangle size={32} />
                            </div>
                          )}
                        </div>
                        <div className="intruder-info">
                          <div className="intruder-time">
                            {new Date(intruder.timestamp).toLocaleString()}
                          </div>
                          <div className="intruder-badge">Unknown Person</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Empty State */}
              {dailyReport.total_detections === 0 && (
                <div className="empty-state">
                  <FileText size={64} />
                  <p>No detections recorded for this date</p>
                </div>
              )}
            </>
          ) : null}
        </div>
      )}

      {/* Intruder Report Tab */}
      {activeTab === 'intruders' && (
        <div className="report-content">
          {loading ? (
            <div className="loading-state">Loading intruder history...</div>
          ) : intruderReport.length > 0 ? (
            <div className="intruders-history">
              <div className="history-header">
                <h3>All Intruder Detections</h3>
                <div className="filter-btn">
                  <Filter size={16} />
                  Filter
                </div>
              </div>
              
              <div className="intruders-grid">
                {intruderReport.map((intruder, index) => (
                  <div key={index} className="intruder-card">
                    <div className="intruder-image">
                      {intruder.face_image_path ? (
                        <img
                          src={`http://localhost:5000/api/images/${intruder.face_image_path.split(/[/\\]/).pop()}`}
                          alt="Intruder"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <div className="intruder-placeholder" style={{ display: intruder.face_image_path ? 'none' : 'flex' }}>
                        <AlertTriangle size={32} />
                      </div>
                    </div>
                    <div className="intruder-info">
                      <div className="intruder-time">
                        {new Date(intruder.timestamp).toLocaleString()}
                      </div>
                      <div className="intruder-id">ID: {intruder.person_id}</div>
                      <div className="intruder-badge">Unknown Person</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <AlertTriangle size={64} />
              <p>No intruders detected</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Reports;
