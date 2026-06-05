import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import Bottombar from './Bottombar';
import styles from '../styles/css/Layout.module.css';

interface LayoutProps {
  title: string;
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ title, children }) => {
  return (
    <div className={styles.layoutContainer}>
      {/* Sidebar - fixed left */}
      <Sidebar />

      {/* Main area - right side */}
      <div className={styles.mainArea}>
        {/* Header - fixed top */}
        <Header title={title} />

        {/* Content area - flows below Header */}
        <main className={styles.content}>
          {children}
        </main>

        {/* Bottom bar - fixed bottom or flow at end of mainArea */}
        <Bottombar />
      </div>
    </div>
  );
};

export default Layout;
