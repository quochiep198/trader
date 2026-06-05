import React, { useEffect, useState } from 'react';
import styles from '../styles/css/Sidebar.module.css';
import { useAuth } from '../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { logout } = useAuth();
  const [currentHash, setCurrentHash] = useState(window.location.hash || '#rules');


  useEffect(() => {
    const handleHashChange = () => {
      setCurrentHash(window.location.hash || '#rules');
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => {
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, []);

  const handleLogout = (e: React.MouseEvent) => {
    e.preventDefault();
    logout();
  };

  return (
    <aside className={styles.sidebar}>
      {/* Brand & Logo */}
      <div className={styles.logoSection}>
        <h1 className={styles.brandTitle}>TradeMind AI</h1>
        <p className={styles.brandSubtitle}>Discipline Coach</p>
      </div>

      {/* Navigation Links */}
      <nav className={styles.nav}>
        <a 
          href="#dashboard" 
          className={`${styles.navLink} ${currentHash === '#dashboard' ? styles.activeLink : ''}`}
        >
          <span className="material-symbols-outlined">dashboard</span>
          <span>Dashboard</span>
        </a>
        <a 
          href="#pre-trade" 
          className={`${styles.navLink} ${currentHash === '#pre-trade' ? styles.activeLink : ''}`}
        >
          <span className="material-symbols-outlined">assignment_turned_in</span>
          <span>Pre-trade Check</span>
        </a>
        <a 
          href="#journal" 
          className={`${styles.navLink} ${currentHash === '#journal' ? styles.activeLink : ''}`}
        >
          <span className="material-symbols-outlined">menu_book</span>
          <span>Trade Journal</span>
        </a>
        <a 
          href="#rules" 
          className={`${styles.navLink} ${currentHash === '#rules' ? styles.activeLink : ''}`}
        >
          <span className="material-symbols-outlined">gavel</span>
          <span>Trading Rules</span>
        </a>
        <a 
          href="#settings" 
          className={`${styles.navLink} ${currentHash === '#settings' ? styles.activeLink : ''}`}
        >
          <span className="material-symbols-outlined">settings</span>
          <span>Settings</span>
        </a>
      </nav>

      {/* Log Trade Button (UI Trigger) */}
      <div className={styles.actionSection}>
        <button 
          className={styles.logBtn} 
          onClick={() => alert('Log New Trade feature is coming soon!')}
        >
          <span className="material-symbols-outlined">add</span>
          <span>Log New Trade</span>
        </button>
      </div>

      {/* Footer Support & Sign Out */}
      <div className={styles.footerNav}>
        <a href="#support" className={styles.footerLink}>
          <span className="material-symbols-outlined">help_outline</span>
          <span>Support</span>
        </a>
        <a href="#logout" className={styles.footerLink} onClick={handleLogout}>
          <span className="material-symbols-outlined">logout</span>
          <span>Sign Out</span>
        </a>
      </div>
    </aside>
  );
};

export default Sidebar;
