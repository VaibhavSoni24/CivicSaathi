import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from 'next/router';
import Navbar from '../../components/Navbar';
import { complaintAPI } from '../../utils/api';
import Link from 'next/link';

export default function ComplaintDetail() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const { id } = router.query;
  const [complaint, setComplaint] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loadingData, setLoadingData] = useState(true);
  const [upvoting, setUpvoting] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    } else if (user && id) {
      fetchComplaintDetails();
    }
  }, [user, loading, id]);

  const fetchComplaintDetails = async () => {
    try {
      const [complaintResponse, logsResponse] = await Promise.all([
        complaintAPI.getComplaint(id),
        complaintAPI.getLogs(id).catch(() => ({ data: [] })),
      ]);
      setComplaint(complaintResponse.data);
      setLogs(logsResponse.data || []);
    } catch (error) {
      console.error('Error fetching complaint details:', error);
      if (error.response?.status === 404) {
        router.push('/complaints');
      }
    } finally {
      setLoadingData(false);
    }
  };

  const handleUpvote = async () => {
    if (upvoting) return;
    setUpvoting(true);
    try {
      await complaintAPI.upvote(id);
      await fetchComplaintDetails();
    } catch (error) {
      console.error('Error upvoting:', error);
      alert(error.response?.data?.error || 'Failed to upvote');
    } finally {
      setUpvoting(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusStyles = {
      'SUBMITTED': { bg: '#E3F2FD', color: '#1976D2', label: 'Submitted' },
      'FILTERING': { bg: '#FFF3E0', color: '#F57C00', label: 'Under Review' },
      'PENDING': { bg: '#FFF3E0', color: '#F57C00', label: 'Pending' },
      'ASSIGNED': { bg: '#E8F5E9', color: '#388E3C', label: 'Assigned' },
      'IN_PROGRESS': { bg: '#E1F5FE', color: '#0288D1', label: 'In Progress' },
      'RESOLVED': { bg: '#E8F5E9', color: '#2E7D32', label: 'Resolved' },
      'COMPLETED': { bg: '#C8E6C9', color: '#1B5E20', label: 'Completed' },
      'DECLINED': { bg: '#FFEBEE', color: '#C62828', label: 'Declined' },
      'REJECTED': { bg: '#FFEBEE', color: '#C62828', label: 'Rejected' },
    };

    const style = statusStyles[status] || statusStyles['SUBMITTED'];
    return (
      <span style={{
        padding: '6px 16px',
        borderRadius: '16px',
        fontSize: '14px',
        fontWeight: '600',
        backgroundColor: style.bg,
        color: style.color,
      }}>
        {style.label}
      </span>
    );
  };

  if (loading || loadingData) {
    return (
      <div style={styles.loadingContainer}>
        <div className="spinner"></div>
      </div>
    );
  }

  if (!user || !complaint) return null;

  return (
    <div style={styles.container}>
      <Navbar />
      
      <main style={styles.main}>
        <div style={styles.content}>
          {/* Back Button */}
          <Link href="/complaints" style={styles.backLink}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back to Complaints
          </Link>

          {/* Header */}
          <div className="card" style={styles.headerCard}>
            <div style={styles.headerTop}>
              <h1 style={styles.title}>{complaint.title}</h1>
              {getStatusBadge(complaint.status)}
            </div>

            <div style={styles.metaRow}>
              <div style={styles.metaItem}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span>Created {new Date(complaint.created_at).toLocaleDateString('en-US', { 
                  year: 'numeric', month: 'long', day: 'numeric' 
                })}</span>
              </div>

              <div style={styles.metaItem}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                <span>{complaint.user_username}</span>
              </div>

              <div style={styles.metaItem}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                  <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                </svg>
                <span>{complaint.category_name}</span>
              </div>
            </div>

            {/* Upvote Button */}
            <button
              onClick={handleUpvote}
              disabled={upvoting || complaint.user_has_voted}
              style={{
                ...styles.upvoteBtn,
                ...(complaint.user_has_voted ? styles.upvoteBtnActive : {}),
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill={complaint.user_has_voted ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                <path d="M12 19V6M5 12l7-7 7 7"/>
              </svg>
              <span>{complaint.upvote_count} {complaint.upvote_count === 1 ? 'Upvote' : 'Upvotes'}</span>
            </button>
          </div>

          <div style={styles.grid}>
            {/* Left Column */}
            <div style={styles.leftColumn}>
              {/* Description */}
              <div className="card" style={styles.section}>
                <h2 style={styles.sectionTitle}>Description</h2>
                <p style={styles.description}>{complaint.description}</p>
              </div>

              {/* Location */}
              <div className="card" style={styles.section}>
                <h2 style={styles.sectionTitle}>Location</h2>
                <div style={styles.locationInfo}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
                    <circle cx="12" cy="10" r="3"/>
                  </svg>
                  <div>
                    <p style={styles.locationAddress}>{complaint.location}</p>
                    <p style={styles.locationCity}>{complaint.city}, {complaint.state}</p>
                    {complaint.latitude && complaint.longitude && (
                      <p style={styles.locationCoords}>
                        {parseFloat(complaint.latitude).toFixed(6)}, {parseFloat(complaint.longitude).toFixed(6)}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Images */}
              {complaint.image && (
                <div className="card" style={styles.section}>
                  <h2 style={styles.sectionTitle}>Image</h2>
                  <img src={complaint.image} alt="Complaint" style={styles.image} />
                </div>
              )}

              {complaint.completion_image && (
                <div className="card" style={styles.section}>
                  <h2 style={styles.sectionTitle}>Completion Image</h2>
                  <img src={complaint.completion_image} alt="Completion" style={styles.image} />
                  {complaint.completion_note && (
                    <p style={styles.completionNote}>{complaint.completion_note}</p>
                  )}
                </div>
              )}

              {/* Declined/Rejected Reason */}
              {['DECLINED', 'REJECTED'].includes(complaint.status) && complaint.filter_reason && (
                <div className="card" style={{...styles.section, ...styles.warningCard}}>
                  <h2 style={styles.sectionTitle}>Reason</h2>
                  <p style={styles.description}>{complaint.filter_reason}</p>
                </div>
              )}
            </div>

            {/* Right Column */}
            <div style={styles.rightColumn}>
              {/* Details Card */}
              <div className="card" style={styles.section}>
                <h2 style={styles.sectionTitle}>Details</h2>
                <div style={styles.detailsList}>
                  <div style={styles.detailItem}>
                    <span style={styles.detailLabel}>Department</span>
                    <span style={styles.detailValue}>{complaint.department_name}</span>
                  </div>
                  <div style={styles.detailItem}>
                    <span style={styles.detailLabel}>Priority</span>
                    <span style={styles.detailValue}>
                      {complaint.priority === 1 ? 'Normal' : complaint.priority === 2 ? 'Medium' : 'High'}
                    </span>
                  </div>
                  <div style={styles.detailItem}>
                    <span style={styles.detailLabel}>Status</span>
                    <span style={styles.detailValue}>{complaint.status.replace('_', ' ')}</span>
                  </div>
                  {complaint.completed_at && (
                    <div style={styles.detailItem}>
                      <span style={styles.detailLabel}>Completed</span>
                      <span style={styles.detailValue}>
                        {new Date(complaint.completed_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Activity Log */}
              {logs.length > 0 && (
                <div className="card" style={styles.section}>
                  <h2 style={styles.sectionTitle}>Activity Log</h2>
                  <div style={styles.logsList}>
                    {logs.map((log, index) => (
                      <div key={index} style={styles.logItem}>
                        <div style={styles.logDot}></div>
                        <div style={styles.logContent}>
                          <p style={styles.logAction}>{log.action}</p>
                          <p style={styles.logTime}>
                            {new Date(log.created_at).toLocaleString()}
                          </p>
                          {log.notes && <p style={styles.logNotes}>{log.notes}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f8fafc',
  },
  loadingContainer: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f8fafc',
  },
  main: {
    paddingTop: '80px',
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '32px 24px',
  },
  backLink: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    color: '#64748b',
    textDecoration: 'none',
    fontSize: '14px',
    fontWeight: '500',
    marginBottom: '24px',
    transition: 'color 0.2s',
  },
  headerCard: {
    marginBottom: '24px',
  },
  headerTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: '16px',
    marginBottom: '16px',
  },
  title: {
    fontSize: '32px',
    fontWeight: '700',
    color: '#1e293b',
    flex: 1,
    lineHeight: '1.3',
  },
  metaRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '24px',
    marginBottom: '20px',
    paddingBottom: '20px',
    borderBottom: '1px solid #e2e8f0',
  },
  metaItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    color: '#64748b',
  },
  upvoteBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 20px',
    border: '2px solid #e2e8f0',
    borderRadius: '8px',
    background: 'white',
    color: '#64748b',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  upvoteBtnActive: {
    borderColor: '#f59e0b',
    color: '#f59e0b',
    background: '#fffbeb',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr',
    gap: '24px',
  },
  leftColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  rightColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  section: {
    display: 'flex',
    flexDirection: 'column',
  },
  sectionTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: '16px',
  },
  description: {
    fontSize: '15px',
    color: '#475569',
    lineHeight: '1.7',
  },
  locationInfo: {
    display: 'flex',
    gap: '12px',
  },
  locationAddress: {
    fontSize: '15px',
    color: '#1e293b',
    fontWeight: '500',
    marginBottom: '4px',
  },
  locationCity: {
    fontSize: '14px',
    color: '#64748b',
    marginBottom: '4px',
  },
  locationCoords: {
    fontSize: '13px',
    color: '#94a3b8',
    fontFamily: 'monospace',
  },
  image: {
    width: '100%',
    borderRadius: '8px',
    marginTop: '8px',
  },
  completionNote: {
    marginTop: '12px',
    fontSize: '14px',
    color: '#64748b',
    fontStyle: 'italic',
  },
  warningCard: {
    borderLeft: '4px solid #ef4444',
  },
  detailsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  detailItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  detailLabel: {
    fontSize: '14px',
    color: '#64748b',
    fontWeight: '500',
  },
  detailValue: {
    fontSize: '14px',
    color: '#1e293b',
    fontWeight: '600',
  },
  logsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  logItem: {
    display: 'flex',
    gap: '12px',
    position: 'relative',
  },
  logDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    backgroundColor: '#3b82f6',
    marginTop: '6px',
    flexShrink: 0,
  },
  logContent: {
    flex: 1,
  },
  logAction: {
    fontSize: '14px',
    color: '#1e293b',
    fontWeight: '500',
    marginBottom: '4px',
  },
  logTime: {
    fontSize: '12px',
    color: '#94a3b8',
    marginBottom: '4px',
  },
  logNotes: {
    fontSize: '13px',
    color: '#64748b',
    marginTop: '8px',
    padding: '8px 12px',
    backgroundColor: '#f8fafc',
    borderRadius: '6px',
  },
};
