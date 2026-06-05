import React, { useState } from 'react';
import styles from '../styles/css/Register.module.css';
import api from '../services/api';
import { MessageProperties } from '../services/message';

export const Register: React.FC = () => {
  const [fullname, setFullname] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);

  // Validation & API States
  const [fullnameError, setFullnameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');
  const [agreeError, setAgreeError] = useState('');
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const validate = () => {
    let valid = true;
    setFullnameError('');
    setEmailError('');
    setPasswordError('');
    setConfirmPasswordError('');
    setAgreeError('');

    if (!fullname.trim()) {
      setFullnameError(MessageProperties.FULLNAME_REQUIRED);
      valid = false;
    }

    if (!email) {
      setEmailError(MessageProperties.EMAIL_REQUIRED);
      valid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError(MessageProperties.EMAIL_INVALID);
      valid = false;
    }

    // Password Policy: tối thiểu 8 ký tự, ít nhất 1 chữ hoa, 1 chữ thường, 1 chữ số
    if (!password) {
      setPasswordError(MessageProperties.PASSWORD_REQUIRED);
      valid = false;
    } else {
      let policyErrors = [];
      if (password.length < 8) {
        policyErrors.push(MessageProperties.PASSWORD_POLICY_MIN_LENGTH);
      }
      if (!/[A-Z]/.test(password)) {
        policyErrors.push(MessageProperties.PASSWORD_POLICY_UPPERCASE);
      }
      if (!/[a-z]/.test(password)) {
        policyErrors.push(MessageProperties.PASSWORD_POLICY_LOWERCASE);
      }
      if (!/[0-9]/.test(password)) {
        policyErrors.push(MessageProperties.PASSWORD_POLICY_NUMBER);
      }
      
      if (policyErrors.length > 0) {
        setPasswordError(`${MessageProperties.PASSWORD_POLICY_PREFIX}${policyErrors.join(', ')}`);
        valid = false;
      }
    }

    if (password && password !== confirmPassword) {
      setConfirmPasswordError(MessageProperties.PASSWORD_MISMATCH);
      valid = false;
    }

    if (!agreeTerms) {
      setAgreeError(MessageProperties.TERMS_REQUIRED);
      valid = false;
    }

    return valid;
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError('');
    setSuccess(false);

    if (!validate()) return;

    setLoading(true);
    try {
      const response = await api.post('/auth/register', {
        email,
        password,
        name: fullname
      });

      if (response.status === 200 || response.status === 201) {
        setSuccess(true);
        setSuccessMessage(response.data.message || MessageProperties.REGISTER_SUCCESS_FALLBACK);
        
        // Reset form fields
        setFullname('');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
        setAgreeTerms(false);
      }
    } catch (error: any) {
      console.error('Registration failed', error);
      if (error.response && error.response.data) {
        setApiError(error.response.data.detail || MessageProperties.REGISTER_FAILED_FALLBACK);
      } else {
        setApiError(MessageProperties.CONNECTION_FAILED);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.wrapper}>
      {/* Background Decor Blurs */}
      <div className={styles.decorLeft}></div>
      <div className={styles.decorRight}></div>

      <div className={styles.canvas}>
        {/* Brand Header */}
        <header className={styles.header}>
          <h1 className={styles.logo}>TradeMind AI</h1>
          <p className={styles.subtitle}>{MessageProperties.REGISTER_SUBTITLE}</p>
        </header>

        {/* Register Panel */}
        <main className={styles.glassPanel}>
          <div className={styles.accentLine}></div>
          <h2 className={styles.title}>{MessageProperties.REGISTER_TITLE}</h2>
          <p className={styles.cardSubtitle}>{MessageProperties.REGISTER_CARD_SUBTITLE}</p>

          <form onSubmit={handleRegister} className={styles.form} noValidate>
            {apiError && (
              <div className={styles.errorAlert}>
                <span className={`material-symbols-outlined ${styles.alertIcon}`}>warning</span>
                <span className={styles.alertText}>{apiError}</span>
              </div>
            )}

            {success && (
              <div className={styles.successAlert}>
                <span className={`material-symbols-outlined ${styles.alertIcon}`}>check_circle</span>
                <span className={styles.alertText}>{successMessage}</span>
              </div>
            )}

            {/* Full Name */}
            <div className={styles.fieldGroup}>
              <label className={styles.label} htmlFor="fullname">{MessageProperties.REGISTER_FULLNAME_LABEL}</label>
              <div className={`${styles.inputInset} ${fullnameError ? styles.errorInset : ''}`}>
                <span className={`material-symbols-outlined ${styles.inputIcon}`}>person</span>
                <input
                  className={styles.input}
                  id="fullname"
                  type="text"
                  placeholder={MessageProperties.REGISTER_FULLNAME_PLACEHOLDER}
                  value={fullname}
                  onChange={(e) => setFullname(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>
              {fullnameError && <span className={styles.errorText}>{fullnameError}</span>}
            </div>

            {/* Email Address */}
            <div className={styles.fieldGroup}>
              <label className={styles.label} htmlFor="email">{MessageProperties.REGISTER_EMAIL_LABEL}</label>
              <div className={`${styles.inputInset} ${emailError ? styles.errorInset : ''}`}>
                <span className={`material-symbols-outlined ${styles.inputIcon}`}>mail</span>
                <input
                  className={styles.input}
                  id="email"
                  type="email"
                  placeholder={MessageProperties.REGISTER_EMAIL_PLACEHOLDER}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>
              {emailError && <span className={styles.errorText}>{emailError}</span>}
            </div>

            {/* Passwords (Side by side on desktop) */}
            <div className={styles.gridRow}>
              {/* Password */}
              <div className={styles.fieldGroup}>
                <label className={styles.label} htmlFor="password">{MessageProperties.REGISTER_PASSWORD_LABEL}</label>
                <div className={`${styles.inputInset} ${passwordError ? styles.errorInset : ''}`}>
                  <span className={`material-symbols-outlined ${styles.inputIcon}`}>lock</span>
                  <input
                    className={styles.input}
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                    required
                  />
                </div>
                {passwordError && <span className={styles.errorText}>{passwordError}</span>}
              </div>

              {/* Confirm Password */}
              <div className={styles.fieldGroup}>
                <label className={styles.label} htmlFor="confirm_password">{MessageProperties.REGISTER_CONFIRM_PASSWORD_LABEL}</label>
                <div className={`${styles.inputInset} ${confirmPasswordError ? styles.errorInset : ''}`}>
                  <span className={`material-symbols-outlined ${styles.inputIcon}`}>lock_reset</span>
                  <input
                    className={styles.input}
                    id="confirm_password"
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={loading}
                    required
                  />
                </div>
                {confirmPasswordError && <span className={styles.errorText}>{confirmPasswordError}</span>}
              </div>
            </div>

            {/* Agreement Terms */}
            <div className={styles.fieldGroup}>
              <div className={styles.agreementRow}>
                <input
                  className={styles.checkbox}
                  id="terms"
                  type="checkbox"
                  checked={agreeTerms}
                  onChange={(e) => setAgreeTerms(e.target.checked)}
                  disabled={loading}
                  required
                />
                <label className={styles.agreementLabel} htmlFor="terms">
                  {MessageProperties.REGISTER_AGREE_TERMS_1}
                  <a className={styles.agreementLink} href="#terms">{MessageProperties.LOGIN_DISCLAIMER_TERMS}</a>
                  {MessageProperties.REGISTER_AGREE_TERMS_2}
                  <a className={styles.agreementLink} href="#privacy">{MessageProperties.LOGIN_DISCLAIMER_PRIVACY}</a>
                  {MessageProperties.REGISTER_AGREE_TERMS_3}
                </label>
              </div>
              {agreeError && <span className={styles.errorText}>{agreeError}</span>}
            </div>

            {/* Action Button */}
            <button className={styles.submitBtn} type="submit" disabled={loading}>
              {loading ? (
                <span className={styles.spinner}></span>
              ) : (
                <>
                  <span>{MessageProperties.REGISTER_BTN_CREATE}</span>
                  <span className={`material-symbols-outlined ${styles.submitIcon}`}>arrow_forward</span>
                </>
              )}
            </button>
          </form>

          {/* Footer Link */}
          <div className={styles.footer}>
            {MessageProperties.REGISTER_FOOTER_PROMPT}{' '}
            <a href="#login" className={styles.footerLink}>{MessageProperties.REGISTER_FOOTER_LINK}</a>
          </div>
        </main>

        {/* Side Content / Brand Illustration Placeholders */}
        <div className={styles.illustrationRow}>
          <div className={styles.illustrationCard}>
            <span className={`material-symbols-outlined ${styles.illustrationIcon}`}>monitoring</span>
            <p className={styles.illustrationText}>{MessageProperties.REGISTER_ILLUST_MIRROR}</p>
          </div>
          <div className={styles.illustrationCard}>
            <span className={`material-symbols-outlined ${styles.illustrationIcon}`}>psychology</span>
            <p className={styles.illustrationText}>{MessageProperties.REGISTER_ILLUST_AI}</p>
          </div>
          <div className={styles.illustrationCard}>
            <span className={`material-symbols-outlined ${styles.illustrationIcon}`}>security</span>
            <p className={styles.illustrationText}>{MessageProperties.REGISTER_ILLUST_SECURITY}</p>
          </div>
        </div>

        {/* Mandatory Disclaimer Footer */}
        <footer className={styles.disclaimerContainer}>
          <div className={styles.disclaimerBox}>
            <h3 className={styles.disclaimerTitle}>
              <span className={`material-symbols-outlined ${styles.disclaimerWarningIcon}`}>warning</span>
              {MessageProperties.REGISTER_DISCLAIMER_TITLE}
            </h3>
            <p className={styles.disclaimerText}>
              {MessageProperties.REGISTER_DISCLAIMER_TEXT}
            </p>
          </div>
          <p className={styles.disclaimerCopyright}>{MessageProperties.REGISTER_DISCLAIMER_COPYRIGHT}</p>
        </footer>
      </div>
    </div>
  );
};

export default Register;
