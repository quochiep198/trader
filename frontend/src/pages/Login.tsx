import React, { useState } from 'react';
import Input from '../components/Input';
import Button from '../components/Button';
import styles from './Login.module.css';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
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
      setEmailError('Vui lòng nhập Email');
      valid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError('Email không đúng định dạng');
      valid = false;
    }

    if (!password) {
      setPasswordError('Vui lòng nhập mật khẩu');
      valid = false;
    } else if (password.length < 8) {
      setPasswordError('Mật khẩu tối thiểu phải từ 8 ký tự');
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
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        // Save token to localStorage as chotted in spec
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        console.log('Login successful!', data);
      } else {
        setApiError(data.detail || 'Mật khẩu hoặc email không chính xác');
      }
    } catch (error) {
      console.error('API connection failed', error);
      setApiError('Không thể kết nối tới máy chủ. Vui lòng kiểm tra lại backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.wrapper}>
      <div className={`${styles.card} fade-in pulse`}>
        <div className={styles.header}>
          <h1 className={styles.logo}>TradeMind AI</h1>
          <p className={styles.subtitle}>Quản lý cảm xúc, kỷ luật giao dịch chứng khoán</p>
        </div>

        <form onSubmit={handleLogin} noValidate>
          {apiError && (
            <div className={styles.errorAlert}>
              <span className={styles.alertIcon}>⚠️</span>
              <span className={styles.alertText}>{apiError}</span>
            </div>
          )}

          {success && (
            <div className={styles.successAlert}>
              <span className={styles.alertIcon}>✓</span>
              <span className={styles.alertText}>Đăng nhập thành công! Đang tải...</span>
            </div>
          )}

          <Input
            label="Email đăng nhập"
            type="email"
            placeholder="demo@trademind.ai"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={emailError}
            disabled={loading}
          />

          <Input
            label="Mật khẩu"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={passwordError}
            disabled={loading}
          />

          <div className={styles.actions}>
            <a href="#forgot" className={styles.forgot}>Quên mật khẩu?</a>
          </div>

          <Button type="submit" loading={loading}>
            Đăng nhập hệ thống
          </Button>
        </form>

        <div className={styles.footer}>
          <span>Chưa có tài khoản? </span>
          <a href="#register">Đăng ký ngay</a>
        </div>
        
        <div className={styles.disclaimer}>
          Disclaimer: Sản phẩm chỉ hỗ trợ quản trị cảm xúc & kỷ luật, không phải tư vấn đầu tư.
        </div>
      </div>
    </div>
  );
};
export default Login;
