import { useState, useEffect } from 'react';
import { useAdminAuth } from '../../context/AdminAuthContext';
import { useRouter } from 'next/router';
import Head from 'next/head';
import AdminNavbar from '../../components/AdminNavbar';
import { adminAttendanceAPI } from '../../utils/adminApi';

export default function AdminAttendance() {
  const { adminUser, loading, isDepartmentAdmin } = useAdminAuth();
  const router = useRouter();
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [cityPassword, setCityPassword] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [attendance, setAttendance] = useState([]);
  const [loadingData, setLoadingData] = useState(false);

  useEffect(() => {
    if (!loading && !adminUser) {
      router.push('/admin/login');
    }
  }, [adminUser, loading]);

  const handleAuthenticate = async () => {
    if (!selectedCity || !cityPassword) {
      alert('Please select city and enter password');
      return;
    }

    try {
      await adminAttendanceAPI.verifyCityPassword(
        selectedCity,
        isDepartmentAdmin ? adminUser.departmentId : null,
        cityPassword
      );
      setAuthenticated(true);
      fetchAttendance();
    } catch (error) {
      alert('Invalid city password');
    }
  };

  const fetchAttendance = async () => {
    setLoadingData(true);
    try {
      const response = await adminAttendanceAPI.getByCity(
        selectedCity,
        selectedDate,
        isDepartmentAdmin ? adminUser.departmentId : null
      );
      setAttendance(response.data?.results || response.data || []);
    } catch (error) {
      console.error('Error fetching attendance:', error);
      setAttendance([]);
    } finally {
      setLoadingData(false);
    }
  };

  if (loading) {
    return <div style={styles.loadingContainer}><div className="spinner"></div></div>;
  }

  return (
    <>
      <Head><title>Attendance System - Admin</title></Head>
      <div style={styles.container}>
        <AdminNavbar />
        <main style={styles.main}>
          <div style={styles.content}>
            <h1 style={styles.title}>🔒 City-Specific Attendance System</h1>
            <p style={styles.subtitle}>Secure attendance tracking with city-wise password protection</p>

            {!authenticated ? (
              <div style={styles.authCard}>
                <h3 style={styles.authTitle}>Authenticate City Access</h3>
                <p style={styles.authSubtitle}>Enter city-specific password to view and manage attendance</p>

                <div style={styles.formGrid}>
                  <div style={styles.inputGroup}>
                    <label style={styles.label}>Select City</label>
                    <select 
                      value={selectedCity}
                      onChange={(e) => setSelectedCity(e.target.value)}
                      style={styles.select}
                    >
                      <option value="">Choose a city</option>
                      <option value="Mumbai">Mumbai</option>
                      <option value="Delhi">Delhi</option>
                      <option value="Bangalore">Bangalore</option>
                      <option value="Pune">Pune</option>
                      <option value="Hyderabad">Hyderabad</option>
                    </select>
                  </div>

                  <div style={styles.inputGroup}>
                    <label style={styles.label}>City Password</label>
                    <input
                      type="password"
                      value={cityPassword}
                      onChange={(e) => setCityPassword(e.target.value)}
                      placeholder="Enter city-specific password"
                      style={styles.input}
                    />
                  </div>
                </div>

                <button onClick={handleAuthenticate} style={styles.authButton}>
                  🔓 Authenticate & Access
                </button>

                <div style={styles.infoBox}>
                  <h4 style={styles.infoTitle}>ℹ️ City-Specific Security</h4>
                  <p style={styles.infoText}>
                    Each city has a unique password for attendance access. This ensures that attendance 
                    data remains secure and can only be accessed by authorized personnel for that specific city.
                  </p>
                  <p style={styles.infoText}>
                    <strong>Multi-City Support:</strong> Department admins can log in to multiple cities 
                    simultaneously by opening separate sessions with respective city passwords.
                  </p>
                </div>
              </div>
            ) : (
              <div style={styles.attendanceSection}>
                <div style={styles.attendanceHeader}>
                  <div style={styles.cityBadge}>
                    📍 {selectedCity} - Authenticated ✓
                  </div>
                  <div style={styles.dateSelector}>
                    <label style={styles.dateLabel}>Date:</label>
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={(e) => { setSelectedDate(e.target.value); fetchAttendance(); }}
                      style={styles.dateInput}
                    />
                  </div>
                  <button onClick={() => setAuthenticated(false)} style={styles.logoutCityButton}>
                    🔒 Lock City
                  </button>
                </div>

                {loadingData ? (
                  <div style={styles.loadingCard}>Loading attendance...</div>
                ) : attendance.length === 0 ? (
                  <div style={styles.emptyState}>
                    <h3>No attendance records for {selectedDate}</h3>
                    <p>Workers attendance will appear here once marked</p>
                    <button onClick={() => alert('Mark attendance functionality')} style={styles.markButton}>
                      + Mark Attendance
                    </button>
                  </div>
                ) : (
                  <div style={styles.attendanceGrid}>
                    {attendance.map(record => (
                      <div key={record.id} style={styles.attendanceCard}>
                        <div style={styles.workerInfo}>
                          <div style={styles.workerAvatar}>{record.worker_name?.charAt(0) || 'W'}</div>
                          <div>
                            <h4 style={styles.workerName}>{record.worker_name}</h4>
                            <p style={styles.workerDept}>{record.department}</p>
                          </div>
                        </div>
                        <div style={styles.attendanceStatus}>
                          <span style={{
                            ...styles.statusBadge,
                            backgroundColor: record.status === 'PRESENT' ? '#d1fae5' : '#fee2e2',
                            color: record.status === 'PRESENT' ? '#065f46' : '#991b1b'
                          }}>
                            {record.status}
                          </span>
                        </div>
                        <p style={styles.timestamp}>
                          🕒 {record.marked_at ? new Date(record.marked_at).toLocaleTimeString() : 'N/A'}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                <div style={styles.summaryCard}>
                  <h3 style={styles.summaryTitle}>Daily Summary</h3>
                  <div style={styles.summaryGrid}>
                    <div style={styles.summaryItem}>
                      <span style={styles.summaryValue}>{attendance.filter(a => a.status === 'PRESENT').length}</span>
                      <span style={styles.summaryLabel}>Present</span>
                    </div>
                    <div style={styles.summaryItem}>
                      <span style={styles.summaryValue}>{attendance.filter(a => a.status === 'ABSENT').length}</span>
                      <span style={styles.summaryLabel}>Absent</span>
                    </div>
                    <div style={styles.summaryItem}>
                      <span style={styles.summaryValue}>{attendance.length}</span>
                      <span style={styles.summaryLabel}>Total</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  );
}

const styles = {
  container: { minHeight: '100vh', backgroundColor: '#f9fafb' },
  main: { paddingTop: '70px' },
  content: { maxWidth: '1200px', margin: '0 auto', padding: '30px 20px' },
  loadingContainer: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  title: { fontSize: '28px', fontWeight: '700', color: '#111827', margin: '0 0 8px 0' },
  subtitle: { fontSize: '14px', color: '#6b7280', marginBottom: '30px' },
  authCard: { background: 'white', borderRadius: '12px', padding: '40px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', maxWidth: '600px', margin: '0 auto' },
  authTitle: { fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '8px', textAlign: 'center' },
  authSubtitle: { fontSize: '14px', color: '#6b7280', marginBottom: '30px', textAlign: 'center' },
  formGrid: { display: 'grid', gap: '20px', marginBottom: '24px' },
  inputGroup: { display: 'flex', flexDirection: 'column', gap: '8px' },
  label: { fontSize: '14px', fontWeight: '600', color: '#374151' },
  select: { padding: '12px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px', backgroundColor: 'white' },
  input: { padding: '12px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' },
  authButton: { width: '100%', padding: '14px', background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '16px', fontWeight: '600', marginBottom: '20px' },
  infoBox: { background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '20px' },
  infoTitle: { fontSize: '15px', fontWeight: '600', color: '#1e40af', marginBottom: '12px' },
  infoText: { fontSize: '13px', color: '#1e40af', lineHeight: '1.6', margin: '8px 0' },
  attendanceSection: { background: 'white', borderRadius: '12px', padding: '30px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  attendanceHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px', flexWrap: 'wrap', gap: '16px' },
  cityBadge: { padding: '8px 16px', background: '#d1fae5', color: '#065f46', borderRadius: '8px', fontSize: '14px', fontWeight: '600' },
  dateSelector: { display: 'flex', alignItems: 'center', gap: '8px' },
  dateLabel: { fontSize: '14px', fontWeight: '600', color: '#374151' },
  dateInput: { padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '14px' },
  logoutCityButton: { padding: '8px 16px', background: '#fee2e2', color: '#991b1b', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' },
  loadingCard: { textAlign: 'center', padding: '40px', color: '#6b7280' },
  emptyState: { textAlign: 'center', padding: '60px 20px' },
  markButton: { marginTop: '20px', padding: '12px 24px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' },
  attendanceGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px', marginBottom: '30px' },
  attendanceCard: { background: '#f9fafb', borderRadius: '8px', padding: '16px', border: '1px solid #e5e7eb' },
  workerInfo: { display: 'flex', gap: '12px', marginBottom: '12px', alignItems: 'center' },
  workerAvatar: { width: '40px', height: '40px', borderRadius: '50%', background: '#3b82f6', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', fontWeight: '600' },
  workerName: { fontSize: '15px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' },
  workerDept: { fontSize: '12px', color: '#6b7280', margin: 0 },
  attendanceStatus: { marginBottom: '8px' },
  statusBadge: { padding: '4px 12px', borderRadius: '12px', fontSize: '12px', fontWeight: '600' },
  timestamp: { fontSize: '12px', color: '#6b7280', margin: 0 },
  summaryCard: { background: '#f9fafb', borderRadius: '8px', padding: '24px', border: '1px solid #e5e7eb' },
  summaryTitle: { fontSize: '16px', fontWeight: '600', color: '#111827', marginBottom: '16px' },
  summaryGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' },
  summaryItem: { textAlign: 'center' },
  summaryValue: { display: 'block', fontSize: '32px', fontWeight: '700', color: '#3b82f6', marginBottom: '4px' },
  summaryLabel: { display: 'block', fontSize: '13px', color: '#6b7280', fontWeight: '500' }
};
