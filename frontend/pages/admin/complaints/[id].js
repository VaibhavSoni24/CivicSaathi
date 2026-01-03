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
  const [workerStats, setWorkerStats] = useState({});
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
    }
  }, [id, adminUser]);

  useEffect(() => {
    if (complaint && showAssignModal) {
      fetchWorkersForDepartment();
    }
  }, [complaint, showAssignModal]);

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

  const fetchWorkersForDepartment = async () => {
    if (!complaint?.department) {
      console.error('No department found in complaint');
      return;
    }

    try {
      // Fetch all workers
      const response = await adminWorkerAPI.getAll();
      const allWorkers = response.data?.results || response.data || [];
      
      // Filter workers by complaint's department
      const departmentWorkers = allWorkers.filter(w => w.department === complaint.department);
      setWorkers(departmentWorkers);
      
      // Fetch statistics for each worker
      const stats = {};
      await Promise.all(
        departmentWorkers.map(async (worker) => {
          try {
            const statResponse = await fetch(`http://localhost:8000/api/workers/${worker.id}/statistics/`);
            if (statResponse.ok) {
              const data = await statResponse.json();
              stats[worker.id] = data;
            }
          } catch (err) {
            console.error(`Error fetching stats for worker ${worker.id}:`, err);
            stats[worker.id] = {
              active_assignments: 0,
              completed_assignments: 0,
              total_assignments: 0
            };
          }
        })
      );
      setWorkerStats(stats);
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

            {/* SLA Timer Display */}
            {complaint.sla_timer && (
              <div style={{
                ...styles.timerCard,
                ...(complaint.sla_timer.status === 'completed' ? styles.timerCompleted :
                    complaint.sla_timer.status === 'declined' ? styles.timerDeclined :
                    complaint.sla_timer.status === 'pending' ? styles.timerPending :
                    complaint.sla_timer.status === 'overdue' ? styles.timerOverdue :
                    complaint.sla_timer.status === 'critical' ? styles.timerCritical :
                    complaint.sla_timer.status === 'warning' ? styles.timerWarning :
                    styles.timerOk)
              }}>
                <div style={styles.timerHeader}>
                  <span style={styles.timerIcon}>{complaint.sla_timer.icon}</span>
                  <h3 style={styles.timerTitle}>{complaint.sla_timer.title}</h3>
                  <span style={{
                    ...styles.priorityBadge,
                    backgroundColor: complaint.sla_timer.priority === 3 ? '#dc2626' : 
                                     complaint.sla_timer.priority === 2 ? '#ea580c' : '#3b82f6'
                  }}>
                    {complaint.sla_timer.priority_text}
                  </span>
                </div>
                
                {/* Hide timer stats for declined complaints */}
                {complaint.sla_timer.status !== 'declined' && (
                  <div style={styles.timerStats}>
                    <div style={styles.timerStat}>
                      <div style={styles.timerStatLabel}>
                        {complaint.sla_timer.status === 'completed' ? 'Total Time' : 'Time Elapsed'}
                      </div>
                      <div style={styles.timerStatValue}>{complaint.sla_timer.hours_elapsed}h</div>
                    </div>
                    {complaint.sla_timer.status !== 'completed' && (
                      <div style={styles.timerStat}>
                        <div style={styles.timerStatLabel}>
                          {complaint.sla_timer.is_overdue ? 'Overdue By' : 'Time Remaining'}
                        </div>
                        <div style={styles.timerStatValue}>
                          {complaint.sla_timer.is_overdue ? 
                            complaint.sla_timer.hours_overdue : 
                            complaint.sla_timer.hours_remaining}h
                        </div>
                      </div>
                    )}
                    <div style={styles.timerStat}>
                      <div style={styles.timerStatLabel}>SLA Deadline</div>
                      <div style={styles.timerStatValue}>{complaint.sla_timer.escalation_deadline}h</div>
                    </div>
                    <div style={styles.timerStat}>
                      <div style={styles.timerStatLabel}>Resolution Target</div>
                      <div style={styles.timerStatValue}>{complaint.sla_timer.resolution_deadline}h</div>
                    </div>
                  </div>
                )}

                {complaint.sla_timer.escalation_count > 0 && (
                  <div style={styles.escalationWarning}>
                    ⚠️ This complaint has been escalated {complaint.sla_timer.escalation_count} time(s)
                  </div>
                )}
              </div>
            )}

            <div style={styles.grid}>
              {/* Left Column - Complaint Details */}
              <div style={styles.leftColumn}>
                {/* Header Card */}
                <div style={styles.card}>
                  <div style={styles.cardHeader}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                        <h1 style={styles.complaintTitle}>{complaint.title}</h1>
                        <span style={{
                          ...styles.statusBadge,
                          backgroundColor: `${statusColor}20`,
                          color: statusColor
                        }}>
                          {complaint.status}
                        </span>
                      </div>
                      <p style={styles.complaintId}>Complaint ID: #{complaint.complaint_id || complaint.id}</p>
                    </div>
                  </div>

                  <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid var(--border-primary)' }}>
                    <div style={styles.metaGrid}>
                      <MetaItem icon="📍" label="Location" value={`${complaint.city}, ${complaint.state}`} />
                      <MetaItem icon="🏢" label="Department" value={complaint.department_name || 'N/A'} />
                      <MetaItem icon="🏫" label="Office" value={complaint.office_name || 'Not assigned'} />
                      <MetaItem icon="📅" label="Submitted on" value={new Date(complaint.created_at).toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })} />
                      <MetaItem icon="👤" label="Citizen" value={
                        complaint.user_first_name && complaint.user_last_name 
                          ? `${complaint.user_first_name} ${complaint.user_last_name} (${complaint.user_username})`
                          : complaint.user_username || 'Anonymous'
                      } />
                      <MetaItem icon="👍" label="Upvotes" value={complaint.upvote_count || 0} />
                      <MetaItem icon="👷" label="Worker Assigned" value={complaint.current_worker_name || 'Not assigned'} />
                    </div>
                  </div>
                </div>

                {/* Description Card */}
                <div style={styles.card}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                    <div style={styles.iconBadge}>📝</div>
                    <h3 style={styles.cardTitle}>Description</h3>
                  </div>
                  <p style={styles.description}>{complaint.description}</p>
                </div>

                {/* Images */}
                {complaint.image && (
                  <div style={styles.card}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                      <div style={styles.iconBadge}>📷</div>
                      <h3 style={styles.cardTitle}>Complaint Image</h3>
                    </div>
                    <div style={styles.imageContainer}>
                      <img src={complaint.image} alt="Complaint" style={styles.complaintImage} />
                    </div>
                  </div>
                )}

                {/* Completion Image */}
                {complaint.completion_image && (
                  <div style={styles.card}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                      <div style={{ ...styles.iconBadge, backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}>✅</div>
                      <h3 style={styles.cardTitle}>Completion Photo</h3>
                    </div>
                    <div style={styles.imageContainer}>
                      <img src={complaint.completion_image} alt="Completion" style={styles.complaintImage} />
                    </div>
                    {complaint.completion_note && (
                      <div style={styles.completionNote}>
                        <p><strong>Note:</strong> {complaint.completion_note}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Completion Section */}
                <div style={styles.card}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                    <div style={{ ...styles.iconBadge, backgroundColor: complaint.status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(100, 116, 139, 0.1)', color: complaint.status === 'COMPLETED' ? '#10b981' : '#64748b' }}>
                      {complaint.status === 'COMPLETED' ? '✅' : '⏳'}
                    </div>
                    <h3 style={styles.cardTitle}>Completion</h3>
                  </div>
                  {complaint.status === 'COMPLETED' ? (
                    <div>
                      {complaint.completion_image && (
                        <div style={styles.imageContainer}>
                          <img src={complaint.completion_image} alt="Completion" style={styles.complaintImage} />
                        </div>
                      )}
                      {complaint.completion_note ? (
                        <div style={{ ...styles.completionNote, marginTop: complaint.completion_image ? '16px' : '0' }}>
                          <p style={{ fontSize: '14px', color: '#cbd5e1', lineHeight: '1.6' }}>
                            <strong style={{ color: '#f1f5f9' }}>Worker's Note:</strong><br />
                            {complaint.completion_note}
                          </p>
                        </div>
                      ) : (
                        <p style={{ fontSize: '14px', color: '#94a3b8', fontStyle: 'italic' }}>No completion note provided</p>
                      )}
                    </div>
                  ) : (
                    <div style={{ padding: '20px', textAlign: 'center', backgroundColor: '#1e293b', borderRadius: '8px' }}>
                      <p style={{ fontSize: '14px', color: '#94a3b8', margin: 0 }}>Not completed yet</p>
                    </div>
                  )}
                </div>

                {/* Location Map */}
                {complaint.latitude && complaint.longitude && (
                  <div style={styles.card}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                      <div style={styles.iconBadge}>📍</div>
                      <h3 style={styles.cardTitle}>Location Details</h3>
                    </div>
                    <div style={styles.locationCard}>
                      <div style={styles.coordinatesRow}>
                        <div style={styles.coordinate}>
                          <span style={styles.coordLabel}>Latitude</span>
                          <span style={styles.coordValue}>{parseFloat(complaint.latitude).toFixed(6)}</span>
                        </div>
                        <div style={styles.coordinate}>
                          <span style={styles.coordLabel}>Longitude</span>
                          <span style={styles.coordValue}>{parseFloat(complaint.longitude).toFixed(6)}</span>
                        </div>
                      </div>
                      <a 
                        href={`https://www.google.com/maps?q=${complaint.latitude},${complaint.longitude}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={styles.mapButton}
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
                          <circle cx="12" cy="10" r="3"/>
                        </svg>
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
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                    <div style={styles.iconBadge}>⚡</div>
                    <h3 style={styles.cardTitle}>Quick Status Update</h3>
                  </div>
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
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                    <div style={styles.iconBadge}>🛠️</div>
                    <h3 style={styles.cardTitle}>Admin Actions</h3>
                  </div>
                  
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
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                      <div style={{ ...styles.iconBadge, backgroundColor: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' }}>👷</div>
                      <h3 style={styles.cardTitle}>Assigned Worker</h3>
                    </div>
                    <div style={styles.workerInfoCard}>
                      <div style={styles.workerInfoRow}>
                        <span style={styles.workerLabel}>Name:</span>
                        <span style={styles.workerValue}>{complaint.assigned_worker.name}</span>
                      </div>
                      <div style={styles.workerInfoRow}>
                        <span style={styles.workerLabel}>Worker ID:</span>
                        <span style={styles.workerValue}>{complaint.assigned_worker.id}</span>
                      </div>
                      <div style={styles.workerInfoRow}>
                        <span style={styles.workerLabel}>Contact:</span>
                        <span style={styles.workerValue}>{complaint.assigned_worker.phone || 'N/A'}</span>
                      </div>
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
            <div style={styles.workerTableContainer}>
              {workers.length === 0 ? (
                <p style={{ textAlign: 'center', color: '#94a3b8', padding: '20px' }}>
                  No workers available in this department
                </p>
              ) : (
                <table style={styles.workerTable}>
                  <thead>
                    <tr>
                      <th style={styles.workerTableHeader}>Select</th>
                      <th style={styles.workerTableHeader}>ID</th>
                      <th style={styles.workerTableHeader}>Name</th>
                      <th style={styles.workerTableHeader}>Active</th>
                      <th style={styles.workerTableHeader}>Completed</th>
                      <th style={styles.workerTableHeader}>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workers.map(worker => {
                      const stats = workerStats[worker.id] || { active_assignments: 0, completed_assignments: 0, total_assignments: 0 };
                      return (
                        <tr 
                          key={worker.id} 
                          style={{
                            ...styles.workerTableRow,
                            backgroundColor: selectedWorker === worker.id ? '#3b82f620' : 'transparent'
                          }}
                          onClick={() => setSelectedWorker(worker.id)}
                        >
                          <td style={styles.workerTableCell}>
                            <input 
                              type="radio" 
                              name="worker" 
                              checked={selectedWorker === worker.id}
                              onChange={() => setSelectedWorker(worker.id)}
                              style={{ cursor: 'pointer' }}
                            />
                          </td>
                          <td style={styles.workerTableCell}>{worker.id}</td>
                          <td style={styles.workerTableCell}>
                            <div style={{ fontWeight: '600' }}>
                              {worker.first_name} {worker.last_name}
                            </div>
                            <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                              {worker.role || 'Worker'}
                            </div>
                          </td>
                          <td style={{ ...styles.workerTableCell, color: '#f59e0b', fontWeight: '600' }}>
                            {stats.active_assignments}
                          </td>
                          <td style={{ ...styles.workerTableCell, color: '#10b981', fontWeight: '600' }}>
                            {stats.completed_assignments}
                          </td>
                          <td style={{ ...styles.workerTableCell, fontWeight: '600' }}>
                            {stats.total_assignments}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
            <textarea
              placeholder="Additional notes (optional)"
              value={actionNotes}
              onChange={(e) => setActionNotes(e.target.value)}
              style={styles.modalTextarea}
            />
            <div style={styles.modalActions}>
              <button onClick={() => setShowAssignModal(false)} style={styles.cancelButton}>Cancel</button>
              <button onClick={handleAssign} style={styles.confirmButton} disabled={processing || !selectedWorker}>
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
  backButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 18px', background: 'var(--bg-card)', border: '1px solid var(--border-primary)', borderRadius: 'var(--radius-md)', cursor: 'pointer', marginBottom: '24px', fontSize: '14px', fontWeight: '500', color: 'var(--text-primary)', transition: 'all 0.2s', ':hover': { backgroundColor: 'var(--bg-hover)', transform: 'translateX(-2px)' } },
  grid: { display: 'grid', gridTemplateColumns: '1fr 420px', gap: '24px' },
  leftColumn: { display: 'flex', flexDirection: 'column', gap: '24px' },
  rightColumn: { display: 'flex', flexDirection: 'column', gap: '24px' },
  card: { background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', padding: '28px', boxShadow: 'var(--shadow-md)', border: '1px solid var(--border-primary)', transition: 'box-shadow 0.2s' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '20px' },
  cardTitle: { fontSize: '16px', fontWeight: '600', color: 'var(--text-primary)', margin: 0 },
  iconBadge: { width: '32px', height: '32px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', backgroundColor: 'rgba(79, 70, 229, 0.1)', color: '#4f46e5', flexShrink: 0 },
  complaintTitle: { fontSize: '26px', fontWeight: '700', color: 'var(--text-primary)', margin: 0, lineHeight: '1.3' },
  complaintId: { fontSize: '13px', color: 'var(--text-secondary)', margin: 0, fontWeight: '500' },
  statusBadge: { padding: '8px 18px', borderRadius: '20px', fontSize: '12px', fontWeight: '700', border: '2px solid currentColor', textTransform: 'uppercase', letterSpacing: '0.5px' },
  statusSelect: { width: '100%', padding: '14px', border: '2px solid var(--border-secondary)', borderRadius: 'var(--radius-md)', fontSize: '14px', backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-primary)', cursor: 'pointer', fontWeight: '500', transition: 'border-color 0.2s', ':focus': { borderColor: '#4f46e5', outline: 'none' } },
  metaGrid: { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' },
  metaItem: { display: 'flex', gap: '12px', alignItems: 'flex-start', padding: '12px', backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' },
  metaIcon: { fontSize: '22px', flexShrink: 0 },
  metaLabel: { fontSize: '11px', color: 'var(--text-secondary)', margin: '0 0 4px 0', textTransform: 'uppercase', fontWeight: '600', letterSpacing: '0.5px' },
  metaValue: { fontSize: '14px', color: 'var(--text-primary)', fontWeight: '600', margin: 0 },
  description: { fontSize: '15px', color: 'var(--text-secondary)', lineHeight: '1.8', margin: 0 },
  imageContainer: { borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid var(--border-primary)', backgroundColor: 'var(--bg-tertiary)' },
  complaintImage: { width: '100%', display: 'block', objectFit: 'cover' },
  completionNote: { marginTop: '16px', padding: '12px 16px', backgroundColor: 'rgba(16, 185, 129, 0.05)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16, 185, 129, 0.2)', color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.6' },
  locationCard: { backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', padding: '20px', border: '1px solid var(--border-primary)' },
  coordinatesRow: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' },
  coordinate: { display: 'flex', flexDirection: 'column', gap: '6px', padding: '12px', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-primary)' },
  coordLabel: { fontSize: '11px', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: '600', letterSpacing: '0.5px' },
  coordValue: { fontSize: '14px', color: 'var(--text-primary)', fontWeight: '600', fontFamily: 'monospace' },
  mapButton: { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', width: '100%', padding: '12px', background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', color: 'white', textDecoration: 'none', borderRadius: 'var(--radius-md)', fontSize: '14px', fontWeight: '600', transition: 'transform 0.2s', ':hover': { transform: 'translateY(-1px)' } },
  actionsContainer: { display: 'flex', flexDirection: 'column', gap: '12px' },
  actionButton: { width: '100%', padding: '14px', background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)', color: 'white', border: 'none', borderRadius: 'var(--radius-md)', cursor: 'pointer', fontSize: '14px', fontWeight: '600', boxShadow: '0 2px 8px rgba(79, 70, 229, 0.3)', transition: 'all 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', ':hover': { transform: 'translateY(-2px)', boxShadow: '0 4px 12px rgba(79, 70, 229, 0.4)' } },
  workerInfoCard: { display: 'flex', flexDirection: 'column', gap: '12px' },
  workerInfoRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-primary)' },
  workerLabel: { fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '600' },
  workerValue: { fontSize: '14px', color: 'var(--text-primary)', fontWeight: '600' },
  modalOverlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000 },
  modal: { background: 'var(--bg-card)', borderRadius: 'var(--radius-xl)', maxWidth: '800px', width: '90%', maxHeight: '90vh', overflow: 'auto', border: '1px solid var(--border-primary)' },
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
  errorContainer: { padding: '60px 20px', textAlign: 'center', color: 'var(--text-secondary)' },
  // Timer styles
  timerCard: { marginBottom: '20px', padding: '24px', borderRadius: '12px', border: '2px solid', transition: 'all 0.3s ease', backgroundColor: 'var(--bg-secondary)' },
  timerCompleted: { borderColor: '#10b981', boxShadow: '0 0 20px rgba(16, 185, 129, 0.2)' },
  timerDeclined: { borderColor: '#6b7280', boxShadow: '0 0 20px rgba(107, 114, 128, 0.15)' },
  timerPending: { borderColor: '#3b82f6', boxShadow: '0 0 20px rgba(59, 130, 246, 0.15)' },
  timerOverdue: { borderColor: '#dc2626', boxShadow: '0 0 20px rgba(220, 38, 38, 0.15)' },
  timerCritical: { borderColor: '#ea580c', boxShadow: '0 0 20px rgba(234, 88, 12, 0.15)' },
  timerWarning: { borderColor: '#eab308', boxShadow: '0 0 20px rgba(234, 179, 8, 0.15)' },
  timerOk: { borderColor: '#10b981', boxShadow: '0 0 20px rgba(16, 185, 129, 0.15)' },
  timerHeader: { display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' },
  timerIcon: { fontSize: '32px' },
  timerTitle: { fontSize: '20px', fontWeight: '700', flex: 1, margin: 0, color: 'var(--text-primary)' },
  priorityBadge: { padding: '6px 14px', borderRadius: '16px', fontSize: '12px', fontWeight: '700', color: 'white', textTransform: 'uppercase', letterSpacing: '0.05em' },
  timerStats: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '16px' },
  timerStat: { textAlign: 'center', padding: '12px', backgroundColor: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-primary)' },
  timerStatLabel: { fontSize: '11px', fontWeight: '600', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' },
  timerStatValue: { fontSize: '24px', fontWeight: '700', color: 'var(--text-primary)' },
  escalationWarning: { marginTop: '16px', padding: '12px 16px', background: 'rgba(220, 38, 38, 0.1)', border: '1px solid rgba(220, 38, 38, 0.3)', borderRadius: '8px', fontSize: '14px', fontWeight: '600', color: '#dc2626', textAlign: 'center' },
  // Worker table styles
  workerTableContainer: { maxHeight: '400px', overflowY: 'auto', marginBottom: '16px', border: '1px solid var(--border-primary)', borderRadius: 'var(--radius-md)' },
  workerTable: { width: '100%', borderCollapse: 'collapse', fontSize: '14px' },
  workerTableHeader: { position: 'sticky', top: 0, padding: '12px', textAlign: 'left', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.5px', backgroundColor: 'var(--bg-tertiary)', color: 'var(--text-secondary)', borderBottom: '2px solid var(--border-primary)', zIndex: 1 },
  workerTableRow: { cursor: 'pointer', transition: 'background-color 0.2s', borderBottom: '1px solid var(--border-primary)' },
  workerTableCell: { padding: '14px 12px', color: 'var(--text-primary)', fontSize: '14px' }
};
