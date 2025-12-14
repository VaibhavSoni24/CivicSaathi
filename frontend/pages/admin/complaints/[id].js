import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAdminAuth } from '../../../context/AdminAuthContext';
import Head from 'next/head';
import AdminNavbar from '../../../components/AdminNavbar';
import { adminComplaintAPI, adminWorkerAPI } from '../../../utils/adminApi';

export default function ComplaintDetail() {
  const router = useRouter();
  const { id } = router.query;
  const { adminUser, hasPermission, isRootAdmin, isSubAdmin, canAccessDepartment, getAccessibleDepartments } = useAdminAuth();
  
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [workers, setWorkers] = useState([]);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [showReassignModal, setShowReassignModal] = useState(false);
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState('');
  const [actionNotes, setActionNotes] = useState('');
  const [completionImage, setCompletionImage] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [quickStatus, setQuickStatus] = useState('');

  useEffect(() => {
    if (id && adminUser) {
      fetchComplaintDetail();
      fetchWorkers();
    }
  }, [id, adminUser]);

  const fetchComplaintDetail = async () => {
    try {
      const response = await adminComplaintAPI.getComplaintDetail(id);
      setComplaint(response.data);
    } catch (error) {
      console.error('Error fetching complaint:', error);
      alert('Failed to load complaint details');
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkers = async () => {
    try {
      const response = await adminWorkerAPI.getAll();
      setWorkers(response.data?.results || response.data || []);
    } catch (error) {
      console.error('Error fetching workers:', error);
    }
  };

  const handleVerify = async () => {
    if (!confirm('Are you sure you want to verify this complaint as genuine?')) return;
    
    setProcessing(true);
    try {
      await adminComplaintAPI.verifyComplaint(id, { verified: true });
      alert('Complaint verified successfully');
      fetchComplaintDetail();
    } catch (error) {
      alert('Failed to verify complaint');
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!actionNotes.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    setProcessing(true);
    try {
      await adminComplaintAPI.rejectComplaint(id, actionNotes);
      alert('Complaint rejected successfully');
      setShowRejectModal(false);
      fetchComplaintDetail();
    } catch (error) {
      alert('Failed to reject complaint');
    } finally {
      setProcessing(false);
      setActionNotes('');
    }
  };

  const handleAssign = async () => {
    if (!selectedWorker) {
      alert('Please select a worker');
      return;
    }

    setProcessing(true);
    try {
      await adminComplaintAPI.assignToWorker(id, selectedWorker, actionNotes);
      alert('Complaint assigned successfully');
      setShowAssignModal(false);
      fetchComplaintDetail();
    } catch (error) {
      alert('Failed to assign complaint');
    } finally {
      setProcessing(false);
      setSelectedWorker('');
      setActionNotes('');
    }
  };

  const handleReassign = async () => {
    if (!selectedWorker) {
      alert('Please select a department');
      return;
    }

    setProcessing(true);
    try {
      await adminComplaintAPI.reassignDepartment(id, selectedWorker, actionNotes);
      alert('Complaint reassigned successfully');
      setShowReassignModal(false);
      fetchComplaintDetail();
    } catch (error) {
      alert('Failed to reassign complaint');
    } finally {
      setProcessing(false);
      setSelectedWorker('');
      setActionNotes('');
    }
  };

  const handleMarkCompleted = async () => {
    if (!completionImage) {
      alert('Please upload a completion photo');
      return;
    }

    setProcessing(true);
    try {
      await adminComplaintAPI.markCompleted(id, completionImage, actionNotes);
      alert('Complaint marked as completed');
      setShowCompletionModal(false);
      fetchComplaintDetail();
    } catch (error) {
      alert('Failed to mark complaint as completed');
    } finally {
      setProcessing(false);
      setCompletionImage(null);
      setActionNotes('');
    }
  };

  const handleQuickStatusChange = async (newStatus) => {
    if (!confirm(`Change complaint status to ${newStatus}?`)) return;

    setProcessing(true);
    try {
      await adminComplaintAPI.updateStatus(id, newStatus);
      alert('Status updated successfully');
      fetchComplaintDetail();
      setQuickStatus('');
    } catch (error) {
      alert('Failed to update status');
    } finally {
      setProcessing(false);
    }
  };

  const handleDelete = async () => {
    const reason = prompt('Please provide a reason for deleting this complaint:');
    if (!reason) return;

    if (!confirm('Are you sure you want to permanently delete this complaint? This action cannot be undone.')) return;

    setProcessing(true);
    try {
      await adminComplaintAPI.deleteComplaint(id, reason);
      alert('Complaint deleted successfully');
      router.push('/admin/complaints');
    } catch (error) {
      alert('Failed to delete complaint');
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div className="spinner"></div>
        <p>Loading complaint details...</p>
      </div>
    );
  }

  if (!complaint) {
    return (
      <div style={styles.container}>
        <AdminNavbar />
        <div style={styles.errorContainer}>
          <h2>Complaint not found</h2>
          <button onClick={() => router.push('/admin/complaints')}>
            Back to Complaints
          </button>
        </div>
      </div>
    );
  }

  const statusColor = getStatusColor(complaint.status);
  const accessibleDepts = getAccessibleDepartments();

  return (
    <>
      <Head>
        <title>Complaint #{complaint.complaint_id || id} - Admin</title>
      </Head>

      <div style={styles.container}>
        <AdminNavbar />
        
        <main style={styles.main}>
          <div style={styles.content}>
            {/* Back Button */}
            <button onClick={() => router.back()} style={styles.backButton}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="15 18 9 12 15 6" />
              </svg>
              Back to Complaints
            </button>

            <div style={styles.grid}>
              {/* Left Column - Complaint Details */}
              <div style={styles.leftColumn}>
                {/* Header Card */}
                <div style={styles.card}>
                  <div style={styles.cardHeader}>
                    <div>
                      <h1 style={styles.complaintTitle}>{complaint.title}</h1>
                      <p style={styles.complaintId}>ID: {complaint.complaint_id || complaint.id}</p>
                    </div>
                    <span style={{
                      ...styles.statusBadge,
                      backgroundColor: `${statusColor}20`,
                      color: statusColor
                    }}>
                      {complaint.status}
                    </span>
                  </div>

                  <div style={styles.metaGrid}>
                    <MetaItem icon="📍" label="Location" value={`${complaint.city}, ${complaint.state}`} />
                    <MetaItem icon="🏢" label="Department" value={complaint.department} />
                    <MetaItem icon="📂" label="Category" value={complaint.category || 'N/A'} />
                    <MetaItem icon="📅" label="Submitted" value={new Date(complaint.created_at).toLocaleString()} />
                    <MetaItem icon="👤" label="Citizen" value={complaint.citizen_name || 'Anonymous'} />
                    <MetaItem icon="👍" label="Upvotes" value={complaint.upvote_count || 0} />
                  </div>
                </div>

                {/* Description Card */}
                <div style={styles.card}>
                  <h3 style={styles.cardTitle}>Description</h3>
                  <p style={styles.description}>{complaint.description}</p>
                </div>

                {/* Images */}
                {complaint.image && (
                  <div style={styles.card}>
                    <h3 style={styles.cardTitle}>Complaint Image</h3>
                    <img src={complaint.image} alt="Complaint" style={styles.complaintImage} />
                  </div>
                )}

                {/* Location Map */}
                {complaint.latitude && complaint.longitude && (
                  <div style={styles.card}>
                    <h3 style={styles.cardTitle}>Location</h3>
                    <div style={styles.mapPlaceholder}>
                      <p>📍 Lat: {complaint.latitude}, Long: {complaint.longitude}</p>
                      <a 
                        href={`https://www.google.com/maps?q=${complaint.latitude},${complaint.longitude}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={styles.mapLink}
                      >
                        Open in Google Maps
                      </a>
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column - Admin Actions */}
              <div style={styles.rightColumn}>
                {/* Quick Status Change */}
                <div style={styles.card}>
                  <h3 style={styles.cardTitle}>Quick Status Update</h3>
                  <select
                    value={quickStatus}
                    onChange={(e) => {
                      const newStatus = e.target.value;
                      if (newStatus) {
                        setQuickStatus(newStatus);
                        handleQuickStatusChange(newStatus);
                      }
                    }}
                    style={styles.statusSelect}
                    disabled={processing}
                  >
                    <option value="">Change Status...</option>
                    <option value="PENDING">Pending</option>
                    <option value="VERIFIED">Verified</option>
                    <option value="IN_PROCESS">In Process</option>
                    <option value="COMPLETED">Completed</option>
                    <option value="REJECTED">Rejected</option>
                  </select>
                </div>

                {/* Action Controls */}
                <div style={styles.card}>
                  <h3 style={styles.cardTitle}>Admin Actions</h3>
                  
                  <div style={styles.actionsContainer}>
                    {/* Verify */}
                    {hasPermission('VERIFY_COMPLAINTS') && complaint.status === 'PENDING' && (
                      <button onClick={handleVerify} style={styles.actionButton} disabled={processing}>
                        ✅ Verify Complaint
                      </button>
                    )}

                    {/* Assign to Worker */}
                    {hasPermission('ASSIGN_TO_WORKERS') && ['PENDING', 'VERIFIED'].includes(complaint.status) && (
                      <button onClick={() => setShowAssignModal(true)} style={styles.actionButton}>
                        👷 Assign to Worker
                      </button>
                    )}

                    {/* Mark Completed */}
                    {hasPermission('MARK_COMPLETED') && complaint.status === 'IN_PROCESS' && (
                      <button onClick={() => setShowCompletionModal(true)} style={{...styles.actionButton, background: '#10b981'}}>
                        ✓ Mark as Completed
                      </button>
                    )}

                    {/* Reassign Department */}
                    {(isRootAdmin || isSubAdmin) && (
                      <button onClick={() => setShowReassignModal(true)} style={styles.actionButton}>
                        🔄 Reassign Department
                      </button>
                    )}

                    {/* Reject */}
                    {hasPermission('REJECT_COMPLAINTS') && !['REJECTED', 'SOLVED'].includes(complaint.status) && (
                      <button onClick={() => setShowRejectModal(true)} style={{...styles.actionButton, background: '#ef4444'}}>
                        ❌ Reject Complaint
                      </button>
                    )}

                    {/* Delete */}
                    {(isRootAdmin || isSubAdmin) && hasPermission('DELETE_INVALID') && (
                      <button onClick={handleDelete} style={{...styles.actionButton, background: '#dc2626', marginTop: '20px'}}>
                        🗑️ Delete Complaint
                      </button>
                    )}
                  </div>
                </div>

                {/* Worker Info */}
                {complaint.assigned_worker && (
                  <div style={styles.card}>
                    <h3 style={styles.cardTitle}>Assigned Worker</h3>
                    <div style={styles.workerInfo}>
                      <p><strong>Name:</strong> {complaint.assigned_worker.name}</p>
                      <p><strong>ID:</strong> {complaint.assigned_worker.id}</p>
                      <p><strong>Contact:</strong> {complaint.assigned_worker.phone || 'N/A'}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>

        {/* Modals */}
        {showAssignModal && (
          <Modal title="Assign to Worker" onClose={() => setShowAssignModal(false)}>
            <select 
              value={selectedWorker} 
              onChange={(e) => setSelectedWorker(e.target.value)}
              style={styles.modalSelect}
            >
              <option value="">Select a worker</option>
              {workers.map(w => (
                <option key={w.id} value={w.id}>{w.name} - {w.department}</option>
              ))}
            </select>
            <textarea
              placeholder="Additional notes (optional)"
              value={actionNotes}
              onChange={(e) => setActionNotes(e.target.value)}
              style={styles.modalTextarea}
            />
            <div style={styles.modalActions}>
              <button onClick={() => setShowAssignModal(false)} style={styles.cancelButton}>Cancel</button>
              <button onClick={handleAssign} style={styles.confirmButton} disabled={processing}>
                {processing ? 'Assigning...' : 'Assign'}
              </button>
            </div>
          </Modal>
        )}

        {showRejectModal && (
          <Modal title="Reject Complaint" onClose={() => setShowRejectModal(false)}>
            <textarea
              placeholder="Reason for rejection (required)"
              value={actionNotes}
              onChange={(e) => setActionNotes(e.target.value)}
              style={styles.modalTextarea}
              required
            />
            <div style={styles.modalActions}>
              <button onClick={() => setShowRejectModal(false)} style={styles.cancelButton}>Cancel</button>
              <button onClick={handleReject} style={{...styles.confirmButton, background: '#ef4444'}} disabled={processing}>
                {processing ? 'Rejecting...' : 'Reject'}
              </button>
            </div>
          </Modal>
        )}

        {showReassignModal && (
          <Modal title="Reassign to Department" onClose={() => setShowReassignModal(false)}>
            <select 
              value={selectedWorker} 
              onChange={(e) => setSelectedWorker(e.target.value)}
              style={styles.modalSelect}
            >
              <option value="">Select a department</option>
              {accessibleDepts.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
            <textarea
              placeholder="Reason for reassignment (required)"
              value={actionNotes}
              onChange={(e) => setActionNotes(e.target.value)}
              style={styles.modalTextarea}
            />
            <div style={styles.modalActions}>
              <button onClick={() => setShowReassignModal(false)} style={styles.cancelButton}>Cancel</button>
              <button onClick={handleReassign} style={styles.confirmButton} disabled={processing}>
                {processing ? 'Reassigning...' : 'Reassign'}
              </button>
            </div>
          </Modal>
        )}

        {showCompletionModal && (
          <Modal title="Mark as Completed" onClose={() => setShowCompletionModal(false)}>
            <div style={styles.fileUpload}>
              <label style={styles.fileLabel}>
                Upload Completion Photo (Required)
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setCompletionImage(e.target.files[0])}
                  style={styles.fileInput}
                />
              </label>
              {completionImage && <p style={styles.fileName}>✓ {completionImage.name}</p>}
            </div>
            <textarea
              placeholder="Completion notes (optional)"
              value={actionNotes}
              onChange={(e) => setActionNotes(e.target.value)}
              style={styles.modalTextarea}
            />
            <div style={styles.modalActions}>
              <button onClick={() => setShowCompletionModal(false)} style={styles.cancelButton}>Cancel</button>
              <button onClick={handleMarkCompleted} style={{...styles.confirmButton, background: '#10b981'}} disabled={processing}>
                {processing ? 'Saving...' : 'Mark Completed'}
              </button>
            </div>
          </Modal>
        )}
      </div>
    </>
  );
}

function MetaItem({ icon, label, value }) {
  return (
    <div style={styles.metaItem}>
      <span style={styles.metaIcon}>{icon}</span>
      <div>
        <p style={styles.metaLabel}>{label}</p>
        <p style={styles.metaValue}>{value}</p>
      </div>
    </div>
  );
}

function Modal({ title, children, onClose }) {
  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <h3 style={styles.modalTitle}>{title}</h3>
          <button onClick={onClose} style={styles.modalClose}>✕</button>
        </div>
        <div style={styles.modalBody}>{children}</div>
      </div>
    </div>
  );
}

function getStatusColor(status) {
  const colors = {
    'PENDING': '#f59e0b',
    'VERIFIED': '#3b82f6',
    'IN_PROCESS': '#8b5cf6',
    'COMPLETED': '#10b981',
    'SOLVED': '#06b6d4',
    'REJECTED': '#ef4444'
  };
  return colors[status] || '#6b7280';
}

const styles = {
  container: { minHeight: '100vh', backgroundColor: 'var(--bg-primary)' },
  main: { paddingTop: '70px' },
  content: { maxWidth: '1400px', margin: '0 auto', padding: '30px 20px' },
  loadingContainer: { minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px', backgroundColor: 'var(--bg-primary)', color: 'var(--text-secondary)' },
  backButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', background: 'var(--bg-card)', border: '1px solid var(--border-primary)', borderRadius: 'var(--radius-md)', cursor: 'pointer', marginBottom: '20px', fontSize: '14px', color: 'var(--text-primary)' },
  grid: { display: 'grid', gridTemplateColumns: '1fr 400px', gap: '20px' },
  leftColumn: { display: 'flex', flexDirection: 'column', gap: '20px' },
  rightColumn: { display: 'flex', flexDirection: 'column', gap: '20px' },
  card: { background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', padding: '24px', boxShadow: 'var(--shadow-md)', border: '1px solid var(--border-primary)' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', gap: '20px' },
  cardTitle: { fontSize: '18px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '16px' },
  complaintTitle: { fontSize: '24px', fontWeight: '700', color: 'var(--text-primary)', margin: '0 0 8px 0' },
  complaintId: { fontSize: '14px', color: 'var(--text-secondary)', margin: 0 },
  statusBadge: { padding: '6px 16px', borderRadius: '16px', fontSize: '13px', fontWeight: '600', border: '1px solid currentColor' },
  statusSelect: { width: '100%', padding: '12px', border: '2px solid var(--border-secondary)', borderRadius: 'var(--radius-md)', fontSize: '14px', backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-primary)', cursor: 'pointer', fontWeight: '500' },
  metaGrid: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' },
  metaItem: { display: 'flex', gap: '12px', alignItems: 'flex-start' },
  metaIcon: { fontSize: '20px' },
  metaLabel: { fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 4px 0' },
  metaValue: { fontSize: '14px', color: 'var(--text-primary)', fontWeight: '500', margin: 0 },
  description: { fontSize: '15px', color: 'var(--text-secondary)', lineHeight: '1.6' },
  complaintImage: { width: '100%', borderRadius: 'var(--radius-md)', marginTop: '12px' },
  mapPlaceholder: { padding: '20px', background: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', textAlign: 'center', border: '1px solid var(--border-primary)' },
  mapLink: { display: 'inline-block', marginTop: '12px', color: '#3b82f6', textDecoration: 'none', fontWeight: '500' },
  actionsContainer: { display: 'flex', flexDirection: 'column', gap: '10px' },
  actionButton: { width: '100%', padding: '12px', background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)', color: 'white', border: 'none', borderRadius: 'var(--radius-md)', cursor: 'pointer', fontSize: '14px', fontWeight: '600', boxShadow: '0 2px 8px rgba(79, 70, 229, 0.3)' },
  workerInfo: { fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.8' },
  modalOverlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000 },
  modal: { background: 'var(--bg-card)', borderRadius: 'var(--radius-xl)', maxWidth: '500px', width: '90%', maxHeight: '90vh', overflow: 'auto', border: '1px solid var(--border-primary)' },
  modalHeader: { padding: '20px', borderBottom: '1px solid var(--border-primary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  modalTitle: { fontSize: '18px', fontWeight: '600', margin: 0, color: 'var(--text-primary)' },
  modalClose: { background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: 'var(--text-secondary)' },
  modalBody: { padding: '20px' },
  modalSelect: { width: '100%', padding: '10px', border: '1px solid var(--border-secondary)', borderRadius: 'var(--radius-md)', marginBottom: '16px', fontSize: '14px', backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-primary)' },
  modalTextarea: { width: '100%', padding: '10px', border: '1px solid var(--border-secondary)', borderRadius: 'var(--radius-md)', minHeight: '100px', fontSize: '14px', marginBottom: '16px', boxSizing: 'border-box', backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-primary)' },
  fileUpload: { marginBottom: '16px' },
  fileLabel: { display: 'block', padding: '12px', background: 'var(--bg-tertiary)', border: '2px dashed var(--border-secondary)', borderRadius: 'var(--radius-md)', cursor: 'pointer', textAlign: 'center', fontSize: '14px', color: 'var(--text-secondary)' },
  fileInput: { display: 'none' },
  fileName: { marginTop: '8px', fontSize: '13px', color: '#10b981' },
  modalActions: { display: 'flex', gap: '12px', justifyContent: 'flex-end' },
  cancelButton: { padding: '10px 20px', background: 'var(--bg-tertiary)', border: 'none', borderRadius: 'var(--radius-md)', cursor: 'pointer', fontSize: '14px', fontWeight: '500', color: 'var(--text-primary)' },
  confirmButton: { padding: '10px 20px', background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)', color: 'white', border: 'none', borderRadius: 'var(--radius-md)', cursor: 'pointer', fontSize: '14px', fontWeight: '500', boxShadow: '0 2px 8px rgba(79, 70, 229, 0.3)' },
  errorContainer: { padding: '60px 20px', textAlign: 'center', color: 'var(--text-secondary)' }
};
