import React from 'react';
import styles from '../styles/css/Bottombar.module.css';
import { MessageProperties } from '../services/message';

export const Bottombar: React.FC = () => {
  return (
    <footer className={styles.bottombar}>
      <div className={styles.left}>
        <span>{MessageProperties.BOTTOMBAR_COPYRIGHT}</span>
      </div>
      <div className={styles.center}>
        <a href="#compliance" className={styles.link}>
          {MessageProperties.BOTTOMBAR_LICENSE}
        </a>
        <span className={styles.separator}>•</span>
        <a href="#disclaimer" className={styles.link}>
          {MessageProperties.BOTTOMBAR_DISCLAIMER}
        </a>
      </div>
      <div className={styles.right}>
        <span className={styles.statusDot}></span>
        <span className={styles.statusText}>{MessageProperties.BOTTOMBAR_API_STATUS}</span>
      </div>
    </footer>
  );
};

export default Bottombar;
