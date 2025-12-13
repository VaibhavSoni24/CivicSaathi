import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from 'next/router';
import Navbar from '../../components/Navbar';
import { complaintAPI } from '../../utils/api';
import Link from 'next/link';

export default function AllComplaints() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [complaints, setComplaints] = useState([]);
  const [loadingData, setLoadingData] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    } else if (user) {
      fetchComplaints();
    }
  }, [user, loading]);

  const fetchComplaints = async () => {
    try {
      const response = await complaintAPI.getAllComplaints();
      // Handle paginated response
      const data = response.data.results || response.data;
      setComplaints(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching complaints:', error);
      setComplaints([]);
    } finally {
      setLoadingData(false);
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
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: '500',
        backgroundColor: style.bg,
        color: style.color,
      }}>
        {style.label}
      </span>
    );
  };

  const filteredComplaints = complaints.filter(complaint => {
    if (filter === 'all') return true;
    if (filter === 'active') return !['COMPLETED', 'RESOLVED', 'REJECTED', 'DECLINED'].includes(complaint.status);
    if (filter === 'completed') return ['COMPLETED', 'RESOLVED'].includes(complaint.status);
    return true;
  });

  if (loading || loadingData) {
    return (
      <div style={styles.loadingContainer}>
        <div className="spinner"></div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div style={styles.container}>
      <Navbar />
      
      <main style={styles.main}>
        <div style={styles.content}>
          {/* Header */}
          <div style={styles.header}>
            <div>
              <h1 style={styles.title}>All Complaints</h1>
              <p style={styles.subtitle}>
                Browse all civic complaints in {user.city}, {user.state}
              </p>
            </div>
            <Link href="/complaints/new">
              <button className="btn btn-primary" style={styles.newBtn}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                New Complaint
              </button>
            </Link>
          </div>

          {/* Filter Tabs */}
          <div style={styles.filterTabs}>
            <button
              onClick={() => setFilter('all')}
              style={{
                ...styles.filterTab,
                ...(filter === 'all' ? styles.filterTabActive : {}),
              }}
            >
              All ({complaints.length})
            </button>
            <button
              onClick={() => setFilter('active')}
              style={{
                ...styles.filterTab,
                ...(filter === 'active' ? styles.filterTabActive : {}),
              }}
            >
              Active ({complaints.filter(c => !['COMPLETED', 'RESOLVED', 'REJECTED', 'DECLINED'].includes(c.status)).length})
            </button>
            <button
              onClick={() => setFilter('completed')}
              style={{
                ...styles.filterTab,
                ...(filter === 'completed' ? styles.filterTabActive : {}),
              }}
            >
              Completed ({complaints.filter(c => ['COMPLETED', 'RESOLVED'].includes(c.status)).length})
            </button>
          </div>

          {/* Complaints List */}
          {filteredComplaints.length === 0 ? (
            <div style={styles.emptyState}>
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5">
                <path d="M9 11l3 3L22 4"></path>
                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"></path>
              </svg>
              <h3 style={styles.emptyTitle}>No complaints found</h3>
              <p style={styles.emptyText}>
                {filter === 'all' 
                  ? "No complaints have been submitted yet."
                  : `No ${filter} complaints found.`}
              </p>
            </div>
          ) : (
            <div style={styles.complaintsGrid}>
              {filteredComplaints.map((complaint) => (
                <Link key={complaint.id} href={`/complaints/${complaint.id}`}>
                  <div className="card" style={styles.complaintCard}>
                    <div style={styles.cardHeader}>
                      <h3 style={styles.complaintTitle}>{complaint.title}</h3>
                      {getStatusBadge(complaint.status)}
                    </div>
                    
                    <p style={styles.complaintDesc}>
                      {complaint.description.length > 150
                        ? complaint.description.substring(0, 150) + '...'
                        : complaint.description}
                    </p>

                    <div style={styles.complaintMeta}>
                      <div style={styles.metaItem}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                          <circle cx="12" cy="7" r="4"/>
                        </svg>
                        <span>{complaint.user_username}</span>
                      </div>

                      <div style={styles.metaItem}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
                          <circle cx="12" cy="10" r="3"/>
                        </svg>
                        <span>{complaint.location}</span>
                      </div>
                      
                      <div style={styles.metaItem}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2">
                          <circle cx="12" cy="12" r="10"></circle>
                          <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        <span>{new Date(complaint.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {complaint.upvote_count > 0 && (
                      <div style={styles.upvotes}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2">
                          <path d="M12 19V6M5 12l7-7 7 7"></path>
                        </svg>
                        <span>{complaint.upvote_count} upvotes</span>
                      </div>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
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
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '32px',
    gap: '24px',
  },
  title: {
    fontSize: '32px',
    fontWeight: '700',
    color: '#1e293b',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '16px',
    color: '#64748b',
  },
  newBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    whiteSpace: 'nowrap',
  },
  filterTabs: {
    display: 'flex',
    gap: '8px',
    marginBottom: '24px',
    borderBottom: '1px solid #e2e8f0',
  },
  filterTab: {
    padding: '12px 24px',
    border: 'none',
    background: 'none',
    fontSize: '14px',
    fontWeight: '500',
    color: '#64748b',
    cursor: 'pointer',
    borderBottom: '2px solid transparent',
    transition: 'all 0.2s',
  },
  filterTabActive: {
    color: '#3b82f6',
    borderBottomColor: '#3b82f6',
  },
  complaintsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
    gap: '24px',
  },
  complaintCard: {
    cursor: 'pointer',
    transition: 'all 0.2s',
    ':hover': {
      transform: 'translateY(-4px)',
      boxShadow: '0 12px 24px rgba(0,0,0,0.1)',
    },
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: '12px',
    marginBottom: '12px',
  },
  complaintTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1e293b',
    flex: 1,
  },
  complaintDesc: {
    fontSize: '14px',
    color: '#64748b',
    lineHeight: '1.6',
    marginBottom: '16px',
  },
  complaintMeta: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    paddingTop: '16px',
    borderTop: '1px solid #e2e8f0',
  },
  metaItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '13px',
    color: '#64748b',
  },
  upvotes: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    marginTop: '12px',
    fontSize: '13px',
    color: '#f59e0b',
    fontWeight: '500',
  },
  emptyState: {
    textAlign: 'center',
    padding: '64px 24px',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  emptyTitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#1e293b',
    marginTop: '16px',
    marginBottom: '8px',
  },
  emptyText: {
    fontSize: '14px',
    color: '#64748b',
  },
};
