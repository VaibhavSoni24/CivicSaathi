import { useState, useEffect } from 'react';
import { useAdminAuth } from '../../context/AdminAuthContext';
import { useRouter } from 'next/router';
import Head from 'next/head';
import AdminNavbar from '../../components/AdminNavbar';
import { adminWorkerAPI } from '../../utils/adminApi';

export default function AdminWorkers() {
  const { adminUser, loading } = useAdminAuth();
  const router = useRouter();
  const [workers, setWorkers] = useState([]);
  const [loadingData, setLoadingData] = useState(true);
  const [filters, setFilters] = useState({ department: 'all', city: 'all', search: '' });

  useEffect(() => {
    if (!loading && !adminUser) {
      router.push('/admin/login');
    } else if (adminUser) {
      fetchWorkers();
    }
  }, [adminUser, loading]);

  const fetchWorkers = async () => {
    try {
      const response = await adminWorkerAPI.getAll();
      setWorkers(response.data?.results || response.data || []);
    } catch (error) {
      console.error('Error fetching workers:', error);
      setWorkers([]);
    } finally {
      setLoadingData(false);
    }
  };

  if (loading || loadingData) {
    return <div style={styles.loadingContainer}><div className="spinner"></div></div>;
  }

  const filteredWorkers = workers.filter(w => {
    if (filters.department !== 'all' && w.department !== filters.department) return false;
    if (filters.city !== 'all' && w.city !== filters.city) return false;
    if (filters.search && !w.name?.toLowerCase().includes(filters.search.toLowerCase())) return false;
    return true;
  });

  return (
    <>
      <Head><title>Workers - Admin</title></Head>
      <div style={styles.container}>
        <AdminNavbar />
        <main style={styles.main}>
          <div style={styles.content}>
            <div style={styles.header}>
              <div>
                <h1 style={styles.title}>Worker Management</h1>
                <p style={styles.subtitle}>{filteredWorkers.length} of {workers.length} workers</p>
              </div>
              <button onClick={() => alert('Add worker functionality coming soon')} style={styles.addButton}>
                + Add Worker
              </button>
            </div>

            {/* Filters */}
            <div style={styles.filtersCard}>
              <input
                type="text"
                placeholder="Search by name..."
                value={filters.search}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
                style={styles.searchInput}
              />
            </div>

            {/* Workers Grid */}
            {filteredWorkers.length === 0 ? (
              <div style={styles.emptyState}>
                <h3>No workers found</h3>
                <p>Add workers to manage workforce</p>
              </div>
            ) : (
              <div style={styles.grid}>
                {filteredWorkers.map(worker => (
                  <div key={worker.id} style={styles.card}>
                    <div style={styles.workerHeader}>
                      <div style={styles.avatar}>{worker.name?.charAt(0) || 'W'}</div>
                      <div>
                        <h3 style={styles.cardTitle}>{worker.name}</h3>
                        <p style={styles.workerId}>ID: {worker.worker_id || worker.id}</p>
                      </div>
                    </div>
                    <div style={styles.workerMeta}>
                      <p>🏢 {worker.department}</p>
                      <p>📍 {worker.city}</p>
                      <p>📱 {worker.phone || 'N/A'}</p>
                      <p>📋 Active Tasks: {worker.active_tasks || 0}</p>
                    </div>
                    <button onClick={() => router.push(`/admin/workers/${worker.id}`)} style={styles.viewButton}>
                      View Details
                    </button>
                  </div>
                ))}
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
  content: { maxWidth: '1400px', margin: '0 auto', padding: '30px 20px' },
  loadingContainer: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '30px' },
  title: { fontSize: '28px', fontWeight: '700', color: '#111827', margin: '0 0 8px 0' },
  subtitle: { fontSize: '14px', color: '#6b7280' },
  addButton: { padding: '10px 20px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' },
  filtersCard: { background: 'white', borderRadius: '12px', padding: '20px', marginBottom: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  searchInput: { width: '100%', padding: '10px 16px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px', boxSizing: 'border-box' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' },
  card: { background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  workerHeader: { display: 'flex', gap: '12px', marginBottom: '16px', alignItems: 'center' },
  avatar: { width: '48px', height: '48px', borderRadius: '50%', background: '#3b82f6', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', fontWeight: '600' },
  cardTitle: { fontSize: '18px', fontWeight: '600', color: '#111827', margin: '0 0 4px 0' },
  workerId: { fontSize: '12px', color: '#9ca3af', margin: 0 },
  workerMeta: { fontSize: '14px', color: '#6b7280', marginBottom: '16px', lineHeight: '1.8' },
  viewButton: { width: '100%', padding: '10px', background: '#f3f4f6', color: '#374151', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' },
  emptyState: { textAlign: 'center', padding: '60px 20px', background: 'white', borderRadius: '12px' }
};
