import { useState, useEffect } from 'react';
import { useAdminAuth } from '../../context/AdminAuthContext';
import { useRouter } from 'next/router';
import Head from 'next/head';
import AdminNavbar from '../../components/AdminNavbar';
import adminCredentials from '../../../adminCredentials.json';

export default function AdminDepartments() {
  const { adminUser, loading, isRootAdmin, isSubAdmin, getAccessibleDepartments } = useAdminAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !adminUser) {
      router.push('/admin/login');
    }
  }, [adminUser, loading]);

  if (loading) {
    return <div style={styles.loadingContainer}><div className="spinner"></div></div>;
  }

  if (!adminUser || (!isRootAdmin && !isSubAdmin)) {
    return (
      <div style={styles.container}>
        <AdminNavbar />
        <div style={styles.errorContainer}>
          <h2>Access Denied</h2>
          <p>Only Root Admins and Sub-Admins can view all departments</p>
        </div>
      </div>
    );
  }

  const accessibleDepts = getAccessibleDepartments();
  const departments = adminCredentials.department_admins.filter(dept => 
    accessibleDepts.includes(dept.departmentId)
  );

  return (
    <>
      <Head><title>Departments - Admin</title></Head>
      <div style={styles.container}>
        <AdminNavbar />
        <main style={styles.main}>
          <div style={styles.content}>
            <h1 style={styles.title}>Department Overview</h1>
            <p style={styles.subtitle}>Managing {departments.length} departments</p>

            <div style={styles.grid}>
              {departments.map(dept => (
                <div key={dept.departmentId} style={styles.card}>
                  <h3 style={styles.cardTitle}>{dept.departmentName}</h3>
                  <p style={styles.cardId}>ID: {dept.departmentId}</p>
                  <div style={styles.badge}>{dept.category}</div>
                  <button onClick={() => router.push(`/admin/complaints?department=${dept.departmentId}`)} style={styles.viewButton}>
                    View Complaints
                  </button>
                </div>
              ))}
            </div>
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
  errorContainer: { padding: '60px 20px', textAlign: 'center' },
  title: { fontSize: '28px', fontWeight: '700', color: '#111827', margin: '0 0 8px 0' },
  subtitle: { fontSize: '14px', color: '#6b7280', marginBottom: '30px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' },
  card: { background: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
  cardTitle: { fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '8px' },
  cardId: { fontSize: '13px', color: '#6b7280', marginBottom: '12px' },
  badge: { display: 'inline-block', padding: '4px 12px', background: '#eff6ff', color: '#3b82f6', borderRadius: '12px', fontSize: '12px', fontWeight: '600', marginBottom: '16px' },
  viewButton: { width: '100%', padding: '10px', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' }
};
