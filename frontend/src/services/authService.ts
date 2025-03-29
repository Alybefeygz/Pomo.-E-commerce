import axios, { AxiosError } from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

// Axios instance oluştur
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // CORS için gerekli
});

// Request interceptor - her istekte token'ı ekle
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Error handler
const handleError = (error: AxiosError) => {
  if (error.response) {
    // Backend'den gelen hata
    const errorData = error.response.data as Record<string, any>;
    if (errorData && typeof errorData === 'object') {
      const errorMessages = Object.entries(errorData)
        .map(([key, value]) => {
          if (Array.isArray(value)) {
            return `${key}: ${value[0]}`;
          }
          return `${key}: ${value}`;
        })
        .join('\n');
      throw new Error(errorMessages);
    }
    throw new Error((errorData as { detail?: string })?.detail || 'Bir hata oluştu');
  } else if (error.request) {
    // İstek yapıldı ama cevap alınamadı
    throw new Error('Sunucuya ulaşılamıyor. Lütfen internet bağlantınızı kontrol edin.');
  } else {
    // İstek oluşturulurken hata oluştu
    throw new Error('İstek oluşturulurken bir hata oluştu.');
  }
};

// Login işlemi
export const login = async (username: string, password: string) => {
  try {
    const response = await api.post('/rest-auth/login/', {
      username,
      password,
    });
    
    // Token'ı localStorage'a kaydet
    if (response.data.key) {
      localStorage.setItem('authToken', response.data.key);
    }
    
    return response.data;
  } catch (error) {
    handleError(error as AxiosError);
  }
};

// Kayıt işlemi
export const register = async (username: string, email: string, password1: string, password2: string) => {
  try {
    console.log('=== Registration Request Details ===');
    console.log('Endpoint:', '/rest-auth/registration/');
    console.log('Request Data:', {
      username,
      email,
      password1,
      password2
    });
    console.log('Headers:', {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });
    
    const response = await api.post('/rest-auth/registration/', {
      username,
      email,
      password1,
      password2,
    });
    
    console.log('=== Registration Response Details ===');
    console.log('Status:', response.status);
    console.log('Response Data:', response.data);
    
    // Token'ı localStorage'a kaydet
    if (response.data.key) {
      localStorage.setItem('authToken', response.data.key);
      console.log('Token saved to localStorage');
    }
    
    return response.data;
  } catch (error: any) {
    console.error('=== Registration Error Details ===');
    console.error('Error Type:', error.name);
    console.error('Error Message:', error.message);
    console.error('Response Status:', error.response?.status);
    console.error('Response Data:', JSON.stringify(error.response?.data, null, 2));
    console.error('Request Config:', {
      url: error.config?.url,
      method: error.config?.method,
      headers: error.config?.headers,
      data: error.config?.data
    });
    
    if (error.response?.data) {
      const errorData = error.response.data;
      if (typeof errorData === 'object') {
        const errorMessages = Object.entries(errorData)
          .map(([key, value]) => {
            if (Array.isArray(value)) {
              return `${key}: ${value[0]}`;
            }
            return `${key}: ${value}`;
          })
          .join('\n');
        throw new Error(errorMessages);
      }
    }
    
    throw new Error(error.message || 'Kayıt işlemi sırasında bir hata oluştu');
  }
};

// Çıkış işlemi
export const logout = async () => {
  try {
    await api.post('/rest-auth/logout/');
    localStorage.removeItem('authToken');
  } catch (error) {
    handleError(error as AxiosError);
  }
};

// Kullanıcı bilgilerini getir
export const getUserInfo = async () => {
  try {
    const response = await api.get('/rest-auth/user/');
    return response.data;
  } catch (error) {
    handleError(error as AxiosError);
  }
}; 