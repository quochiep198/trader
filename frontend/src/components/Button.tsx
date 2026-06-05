import React, { type ButtonHTMLAttributes } from 'react';
import styles from '../styles/css/Button.module.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ variant = 'primary', loading, children, ...props }) => {
  return (
    <button 
      className={`${styles.button} ${styles[variant]} ${loading ? styles.loading : ''}`} 
      disabled={loading || props.disabled}
      {...props}
    >
      {loading ? <span className={styles.spinner}></span> : children}
    </button>
  );
};
export default Button;
