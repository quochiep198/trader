import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import PersonalRules from './pages/PersonalRules';
import PreTradeCheck from './pages/PreTradeCheck';
import Layout from './components/Layout';
import { MessageProperties } from './services/message';
import './styles/css/App.css';

function AppContent() {
  const { isAuthenticated, loading } = useAuth();
  const [hash, setHash] = useState(window.location.hash);

  useEffect(() => {
    const handleHashChange = () => {
      setHash(window.location.hash);
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => {
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, []);

  useEffect(() => {
    if (isAuthenticated && (hash === '#login' || hash === '#register' || !hash)) {
      window.location.hash = '#dashboard';
    }
  }, [isAuthenticated, hash]);

  // Đang tải trạng thái xác thực
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh', 
        backgroundColor: '#0b0c10', 
        color: '#e4e2e4',
        fontFamily: 'sans-serif'
      }}>
        <p>Đang tải phiên đăng nhập...</p>
      </div>
    );
  }

  // Điều hướng bảo mật (Auth Guard)
  if (!isAuthenticated) {
    if (hash === '#register') {
      return <Register />;
    }
    return <Login />;
  }

  // Các trang chỉ dành cho người dùng đã đăng nhập
  switch (hash) {
    case '#pre-trade':
      return (
        <Layout title={MessageProperties.PRETRADE_PAGE_TITLE}>
          <PreTradeCheck />
        </Layout>
      );
    case '#rules':
    default:
      return (
        <Layout title={MessageProperties.RULES_PAGE_TITLE}>
          <PersonalRules />
        </Layout>
      );
  }
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

