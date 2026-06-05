import axios from 'axios';

// Lấy API base URL từ biến môi trường Vite hoặc mặc định là localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Hàm lấy giá trị cookie theo tên
export function getCookie(name: string): string | null {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
  }
  return null;
}

// Interceptor tự động thêm Bearer token vào header cho các request có xác thực
api.interceptors.request.use(
  (config) => {
    const token = getCookie('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor tự động xử lý khi nhận response lỗi 401 (Unauthorized) hoặc 403 (Forbidden)
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      // Xóa cookie token và dữ liệu localStorage
      document.cookie = 'access_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Lax';
      localStorage.removeItem('user');
      // Chuyển hướng về trang đăng nhập bằng hash routing
      window.location.hash = '#login';
      // Reload để làm sạch state trong React Context
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export default api;
