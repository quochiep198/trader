import React from 'react';
import styles from '../styles/css/Header.module.css';
import { useAuth } from '../context/AuthContext';

interface HeaderProps {
  title: string;
}

export const Header: React.FC<HeaderProps> = ({ title }) => {
  const { user } = useAuth();

  // Get user initials for placeholder avatar if no image is available
  const getInitials = () => {
    if (!user || !user.name) return 'TM';
    return user.name
      .split(' ')
      .map((n: string) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  };

  return (
    <header className={styles.header}>
      {/* Title & Page Navigation Context */}
      <div className={styles.leftSection}>
        <h2 className={styles.title}>{title}</h2>
        <nav className={styles.subnav}>
          <a href="#market-data" className={styles.subnavLink}>Market Data</a>
          <a href="#performance" className={styles.subnavLink}>Performance</a>
          <a href="#analytics" className={styles.subnavLink}>Analytics</a>
        </nav>
      </div>

      {/* Tools Section: Search, Notifications, Avatar */}
      <div className={styles.rightSection}>
        <div className={styles.searchWrapper}>
          <span className={`material-symbols-outlined ${styles.searchIcon}`}>search</span>
          <input 
            type="text" 
            placeholder="Search parameters..." 
            className={styles.searchInput}
          />
        </div>

        <button 
          className={styles.toolBtn} 
          onClick={() => alert('Notifications feature is coming soon!')}
          aria-label="Notifications"
        >
          <span className="material-symbols-outlined">notifications</span>
        </button>

        <div className={styles.userSection} title={user?.email || 'User Session'}>
          <div className={styles.avatar}>
            {user?.name ? (
              <span className={styles.avatarText}>{getInitials()}</span>
            ) : (
              <span className="material-symbols-outlined">person</span>
            )}
          </div>
          <span className={styles.userName}>{user?.name || 'Trader'}</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
