import { useState, useEffect } from 'react';
import { useAdminAuth } from '../../context/AdminAuthContext';
import { useRouter } from 'next/router';
import Head from 'next/head';
import AdminNavbar from '../../components/AdminNavbar';
import { adminOfficeAPI } from '../../utils/adminApi';

export default function AdminOffices() {
  const { adminUser, loading } = useAdminAuth();
  const router = useRouter();
  const [offices, setOffices] = useState([]);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (!loading && !adminUser) {
      router.push('/admin/login');
    } else if (adminUser) {
      fetchOffices();
    }
  }, [adminUser, loading]);

  const fetchOffices = async () => {
    try {
      const response = await adminOfficeAPI.getAll();
      setOffices(response.data?.results || response.data || []);
    } catch (error) {
      console.error('Error fetching offices:', error);
      setOffices([]);
    } finally {
      setLoadingData(false);
    }
  };

  if (loading || loadingData) {
    return <div style={styles.loadingContainer}><div className="spinner"></div></div>;
  }

  return (
    <>
      <Head><title>Offices - Admin</title></Head>
      <div style={styles.container}>
        <AdminNavbar />
        <main style={styles.main}>
          <div style={styles.content}>
            <div style={styles.header}>
              <div>
                <h1 style={styles.title}>Office Management</h1>
                <p style={styles.subtitle}>{offices.length} offices registered</p>
              </div>
              <button onClick={() => alert('Create office functionality coming soon')} style={styles.addButton}>
                + Add Office
              </button>
            </div>

            {offices.length === 0 ? (
              <div style={styles.emptyState}>
                <h3>No offices found</h3>
                <p>Start by adding your first office location</p>
              </div>
            ) : (
              <div style={styles.grid}>
                {offices.map(office => (
                  <div key={office.id} style={styles.card}>
                    <h3 style={styles.cardTitle}>{office.name}</h3>
                    <p style={styles.cardMeta}>📍 {office.city}, {office.state}</p>
                    <p style={styles.cardMeta}>🏢 Department: {office.department}</p>
                    <p style={styles.cardMeta}>👷 Workers: {office.worker_count || 0}</p>
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
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' },
  card: { background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  cardTitle: { fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '12px' },
  cardMeta: { fontSize: '14px', color: '#6b7280', margin: '6px 0' },
  emptyState: { textAlign: 'center', padding: '60px 20px', background: 'white', borderRadius: '12px' }
};
