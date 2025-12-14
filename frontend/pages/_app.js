import '../styles/globals.css';
import { AuthProvider } from '../context/AuthContext';
import { AdminAuthProvider } from '../context/AdminAuthContext';

export default function App({ Component, pageProps }) {
  return (
    <AuthProvider>
      <AdminAuthProvider>
        <Component {...pageProps} />
      </AdminAuthProvider>
    </AuthProvider>
  );
}
