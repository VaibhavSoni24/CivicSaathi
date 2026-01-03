import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from 'next/router';
import Navbar from '../../components/Navbar';
import { complaintAPI, departmentAPI } from '../../utils/api';

export default function NewComplaint() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [departments, setDepartments] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    department: '',
    location: '',
    latitude: '',
    longitude: '',
    city: user?.city || '',
    state: user?.state || '',
    image: null,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    } else if (user) {
      fetchDepartments();
      getLocation();
    }
  }, [user, loading]);

  const fetchDepartments = async () => {
    try {
      const response = await departmentAPI.getAll();
      setDepartments(response.data);
    } catch (error) {
      console.error('Error fetching departments:', error);
    }
  };

  const getLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            latitude: position.coords.latitude.toFixed(6),
            longitude: position.coords.longitude.toFixed(6),
          }));
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData(prev => ({ ...prev, image: file }));
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await complaintAPI.create(formData);
      setSuccess(true);
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to submit complaint');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
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
          <div style={styles.header}>
            <button onClick={() => router.back()} className="btn btn-secondary">
              ← Back
            </button>
            <h1 style={styles.title}>Submit New Complaint</h1>
            <p style={styles.subtitle}>Report a civic issue in your area</p>
          </div>

          <div className="card" style={styles.formCard}>
            {success ? (
              <div style={styles.successMessage}>
                <div style={styles.successIcon}>✓</div>
                <h2>Complaint Submitted Successfully!</h2>
                <p>Your complaint is being processed through our validation system.</p>
                <p>Redirecting to dashboard...</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} style={styles.form}>
                {error && (
                  <div style={styles.error}>{error}</div>
                )}

                <div style={styles.formGroup}>
                  <label style={styles.label}>Complaint Title *</label>
                  <input
                    type="text"
                    name="title"
                    className="input"
                    value={formData.title}
                    onChange={handleChange}
                    placeholder="Brief title describing the issue"
                    required
                  />
                </div>

                <div style={styles.formGroup}>
                  <label style={styles.label}>Department *</label>
                  <select
                    name="department"
                    className="select"
                    value={formData.department}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select a department</option>
                    {departments.map(dept => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={styles.formGroup}>
                  <label style={styles.label}>Description *</label>
                  <textarea
                    name="description"
                    className="textarea"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="Detailed description of the issue (minimum 20 characters)"
                    required
                    minLength="20"
                    style={{ minHeight: '120px' }}
                  />
                  <span style={styles.hint}>
                    {formData.description.length} characters (min: 20)
                  </span>
                </div>

                <div style={styles.formGroup}>
                  <label style={styles.label}>Location *</label>
                  <input
                    type="text"
                    name="location"
                    className="input"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="Specific address or landmark"
                    required
                  />
                </div>

                <div style={styles.row}>
                  <div style={styles.formGroup}>
                    <label style={styles.label}>City *</label>
                    <input
                      type="text"
                      name="city"
                      className="input"
                      value={formData.city}
                      onChange={handleChange}
                      placeholder="City name"
                      required
                    />
                  </div>

                  <div style={styles.formGroup}>
                    <label style={styles.label}>State *</label>
                    <input
                      type="text"
                      name="state"
                      className="input"
                      value={formData.state}
                      onChange={handleChange}
                      placeholder="State name"
                      required
                    />
                  </div>
                </div>

                <div style={styles.row}>
                  <div style={styles.formGroup}>
                    <label style={styles.label}>Latitude</label>
                    <input
                      type="text"
                      name="latitude"
                      className="input"
                      value={formData.latitude}
                      onChange={handleChange}
                      placeholder="Auto-detected"
                      readOnly
                    />
                  </div>

                  <div style={styles.formGroup}>
                    <label style={styles.label}>Longitude</label>
                    <input
                      type="text"
                      name="longitude"
                      className="input"
                      value={formData.longitude}
                      onChange={handleChange}
                      placeholder="Auto-detected"
                      readOnly
                    />
                  </div>
                </div>

                <div style={styles.formGroup}>
                  <label style={styles.label}>Upload Photo</label>
                  <div style={styles.imageUpload}>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      style={styles.fileInput}
                      id="imageUpload"
                    />
                    <label htmlFor="imageUpload" style={styles.uploadLabel}>
                      {imagePreview ? (
                        <img src={imagePreview} alt="Preview" style={styles.imagePreview} />
                      ) : (
                        <div style={styles.uploadPlaceholder}>
                          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                            <circle cx="8.5" cy="8.5" r="1.5"/>
                            <polyline points="21 15 16 10 5 21"/>
                          </svg>
                          <p>Click to upload photo</p>
                          <p style={styles.uploadHint}>PNG, JPG up to 10MB</p>
                        </div>
                      )}
                    </label>
                  </div>
                </div>

                <div style={styles.actions}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => router.back()}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <>
                        <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
                        Submitting...
                      </>
                    ) : (
                      'Submit Complaint'
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: 'var(--bg-primary)',
  },
  loadingContainer: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  main: {
    padding: '2rem 0',
  },
  content: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '0 1.5rem',
  },
  header: {
    marginBottom: '2rem',
  },
  title: {
    fontSize: '2rem',
    fontWeight: '700',
    marginTop: '1rem',
    marginBottom: '0.5rem',
  },
  subtitle: {
    color: 'var(--text-secondary)',
    fontSize: '1rem',
  },
  formCard: {
    padding: '2rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  row: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '1rem',
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: 'var(--text-primary)',
  },
  hint: {
    fontSize: '0.75rem',
    color: 'var(--text-muted)',
  },
  error: {
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid var(--accent-danger)',
    color: 'var(--accent-danger)',
    padding: '0.75rem',
    borderRadius: 'var(--radius-md)',
    fontSize: '0.875rem',
  },
  imageUpload: {
    position: 'relative',
  },
  fileInput: {
    display: 'none',
  },
  uploadLabel: {
    display: 'block',
    cursor: 'pointer',
    border: '2px dashed var(--border-primary)',
    borderRadius: 'var(--radius-lg)',
    padding: '2rem',
    textAlign: 'center',
    transition: 'all 0.2s',
    backgroundColor: 'var(--bg-tertiary)',
  },
  uploadPlaceholder: {
    color: 'var(--text-secondary)',
  },
  uploadHint: {
    fontSize: '0.75rem',
    marginTop: '0.5rem',
    color: 'var(--text-muted)',
  },
  imagePreview: {
    maxWidth: '100%',
    maxHeight: '300px',
    borderRadius: 'var(--radius-md)',
  },
  actions: {
    display: 'flex',
    gap: '1rem',
    justifyContent: 'flex-end',
    marginTop: '1rem',
  },
  successMessage: {
    textAlign: 'center',
    padding: '3rem',
  },
  successIcon: {
    width: '80px',
    height: '80px',
    margin: '0 auto 1.5rem',
    backgroundColor: 'rgba(16, 185, 129, 0.2)',
    color: 'var(--accent-success)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '3rem',
    fontWeight: '700',
  },
};
