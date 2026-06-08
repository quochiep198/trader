import React, { useState } from 'react';
import styles from '../styles/css/Login.module.css';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { MessageProperties } from '../services/message';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  // Validation and API states
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const validate = () => {
    let valid = true;
    setEmailError('');
    setPasswordError('');

    if (!email) {
      setEmailError(MessageProperties.EMAIL_REQUIRED);
      valid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError(MessageProperties.EMAIL_INVALID);
      valid = false;
    }

    if (!password) {
      setPasswordError(MessageProperties.PASSWORD_REQUIRED);
      valid = false;
    } else if (password.length < 8) {
      setPasswordError(MessageProperties.PASSWORD_MIN_LENGTH);
      valid = false;
    }

    return valid;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError('');
    setSuccess(false);

    if (!validate()) return;

    setLoading(true);
    try {
      const response = await api.post('/auth/login', { email, password });

      if (response.status === 200) {
        // Visual transition corresponding to HTML JS mockup:
        // Delay 1s to show the beautiful visual success state transition
        setSuccess(true);
        setLoading(false);
        setTimeout(() => {
          login(response.data.access_token, response.data.user, rememberMe);
          window.location.hash = '#dashboard';
        }, 1000);
        console.log('Login successful!', response.data);
      }
    } catch (error: any) {
      console.error('API connection failed', error);
      if (error.response && error.response.data) {
        setApiError(error.response.data.detail || MessageProperties.LOGIN_FAILED_FALLBACK);
      } else {
        setApiError(MessageProperties.CONNECTION_FAILED);
      }
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className={styles.wrapper}>
      {/* Background Decor Blurs */}
      <div className={styles.decorLeft}></div>
      <div className={styles.decorRight}></div>

      <div className={styles.canvas}>
        {/* Brand Identity Section */}
        <header className={styles.header}>
          <div className={styles.brandIconContainer}>
            <span className={`material-symbols-outlined ${styles.brandIcon}`}>psychology</span>
          </div>
          <h1 className={styles.logo}>TradeMind AI</h1>
          <p className={styles.subtitle}>
            {MessageProperties.LOGIN_SUBTITLE}
          </p>
        </header>

        {/* Login Form Card */}
        <section className={styles.glassCard}>
          <form onSubmit={handleLogin} className={styles.form} noValidate>
            {apiError && (
              <div className={styles.errorAlert}>
                <span className={`material-symbols-outlined ${styles.alertIcon}`}>warning</span>
                <span className={styles.alertText}>{apiError}</span>
              </div>
            )}

            {/* Email Field */}
            <div className={styles.fieldGroup}>
              <label className={styles.label} htmlFor="email">
                {MessageProperties.LOGIN_EMAIL_LABEL}
              </label>
              <div className={styles.inputWrapper}>
                <span className={`material-symbols-outlined ${styles.inputIcon}`}>mail</span>
                <input
                  className={`${styles.input} ${emailError ? styles.errorInput : ''}`}
                  id="email"
                  type="email"
                  placeholder={MessageProperties.LOGIN_EMAIL_PLACEHOLDER}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading || success}
                  required
                />
              </div>
              {emailError && <span className={styles.errorText}>{emailError}</span>}
            </div>

            {/* Password Field */}
            <div className={styles.fieldGroup}>
              <div className={styles.labelRow}>
                <label className={styles.label} htmlFor="password">
                  {MessageProperties.LOGIN_PASSWORD_LABEL}
                </label>
                <a href="#forgot" className={styles.forgotLink}>
                  {MessageProperties.LOGIN_FORGOT_PASSWORD}
                </a>
              </div>
              <div className={styles.inputWrapper}>
                <span className={`material-symbols-outlined ${styles.inputIcon}`}>lock</span>
                <input
                  className={`${styles.input} ${passwordError ? styles.errorInput : ''}`}
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder={MessageProperties.LOGIN_PASSWORD_PLACEHOLDER}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading || success}
                  required
                />
                <button
                  type="button"
                  className={styles.eyeButton}
                  onClick={togglePasswordVisibility}
                  disabled={loading || success}
                >
                  <span className="material-symbols-outlined">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
              {passwordError && <span className={styles.errorText}>{passwordError}</span>}
            </div>

            {/* Options Checkbox */}
            <div className={styles.row}>
              <input
                className={styles.checkbox}
                id="remember"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={loading || success}
              />
              <label className={styles.checkboxLabel} htmlFor="remember">
                {MessageProperties.LOGIN_REMEMBER_ME}
              </label>
            </div>

            {/* Action Button with Micro-interactions */}
            <button
              className={`${styles.submitBtn} ${success ? styles.btnSuccess : ''}`}
              type="submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className={styles.spinner}></span>
                  {MessageProperties.LOGIN_BTN_VALIDATING}
                </>
              ) : success ? (
                <>
                  <span className="material-symbols-outlined">check_circle</span>
                  {MessageProperties.LOGIN_BTN_SUCCESS}
                </>
              ) : (
                <>
                  {MessageProperties.LOGIN_BTN_SIGNIN}
                  <span className="material-symbols-outlined">arrow_forward</span>
                </>
              )}
            </button>

            {/* Divider */}
            <div className={styles.divider}>
              <div className={styles.dividerLine}></div>
              <span className={styles.dividerText}>{MessageProperties.LOGIN_DIVIDER}</span>
              <div className={styles.dividerLine}></div>
            </div>

            {/* Secondary SSO Action */}
            <button className={styles.ssoBtn} type="button" disabled={loading || success}>
              <img
                alt="Google"
                className={styles.ssoIcon}
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuBcjShQ0z3oxdaFhceBMEzyA8-Npbshw_SfilGbZG4BoxnwM9KWsf1YBMKR8IHfyEcqfYCDM87vUEHes1j6Ojo0x0i32so6O87uuRT4oNnjWybC4J42zEyjqymBUj2IE6ubj1v1q2hAajOtLd-QOG7hWOTqOx3jNXPnlLw_i_Xd66uoGovSQVdsAtqYVFhFMfqmEQBHsJWKEUzi079QF7JKTmZssgfMMhlPg8j1BgMvIMQHfwm-MEm28andQWLxzcB7IpmTRxx9JnGW"
              />
              {MessageProperties.LOGIN_SSO_BTN}
            </button>
          </form>
        </section>

        {/* Footer Link */}
        <footer className={styles.footer}>
          {MessageProperties.LOGIN_FOOTER_PROMPT}{' '}
          <a href="#register" className={styles.footerLink}>
            {MessageProperties.LOGIN_FOOTER_LINK}
          </a>
        </footer>
      </div>

      {/* Legal Disclaimer Anchor */}
      <aside className={styles.disclaimerContainer}>
        <div className={styles.disclaimerContent}>
          <div className={styles.disclaimerRow}>
            <span className={`material-symbols-outlined ${styles.disclaimerIcon}`}>warning</span>
            <div className={styles.disclaimerTextContainer}>
              <h4 className={styles.disclaimerTitle}>{MessageProperties.LOGIN_DISCLAIMER_TITLE}</h4>
              <p className={styles.disclaimerText}>
                {MessageProperties.LOGIN_DISCLAIMER_TEXT}
              </p>
            </div>
          </div>

          <div className={styles.disclaimerFooter}>
            <p className={styles.disclaimerCopyright}>
              {MessageProperties.LOGIN_DISCLAIMER_COPYRIGHT}
            </p>
            <div className={styles.disclaimerLinks}>
              <a className={styles.disclaimerLink} href="#privacy">{MessageProperties.LOGIN_DISCLAIMER_PRIVACY}</a>
              <a className={styles.disclaimerLink} href="#terms">{MessageProperties.LOGIN_DISCLAIMER_TERMS}</a>
              <a className={styles.disclaimerLink} href="#compliance">{MessageProperties.LOGIN_DISCLAIMER_COMPLIANCE}</a>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
};

export default Login;
