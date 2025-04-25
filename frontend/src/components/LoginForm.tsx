import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message, Modal, Divider } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import '../styles/auth.css';
import { login } from '../services/authService';
import { signInWithGoogle } from '../services/googleAuthService';

// Define empty handler functions for pointer events
// const emptyPointerHandler = () => {};

// Yaygın şifrelerin listesi
const commonPasswords = [
  'password', '123456', '12345678', 'qwerty', '111111', 'abc123',
  'password123', 'admin', 'letmein', 'welcome', '123123', 'test'
];

// Şifre doğrulama fonksiyonu
const validatePassword = (password: string, username: string): { isValid: boolean; message: string } => {
  // Minimum uzunluk kontrolü
  if (password.length < 8) {
    return {
      isValid: false,
      message: 'Şifre en az 8 karakter uzunluğunda olmalıdır'
    };
  }

  // Tamamen sayısal şifre kontrolü
  if (/^\d+$/.test(password)) {
    return {
      isValid: false,
      message: 'Şifre sadece sayılardan oluşamaz'
    };
  }

  // Karmaşıklık kontrolü
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (!(hasLetter && hasNumber && hasSpecialChar)) {
    return {
      isValid: false,
      message: 'Şifre en az bir harf, bir rakam ve bir özel karakter içermelidir'
    };
  }

  // Yaygın şifre kontrolü
  if (commonPasswords.includes(password.toLowerCase())) {
    return {
      isValid: false,
      message: 'Bu şifre çok yaygın, lütfen daha güvenli bir şifre seçin'
    };
  }

  // Kullanıcı adı benzerlik kontrolü
  if (username && password.toLowerCase().includes(username.toLowerCase())) {
    return {
      isValid: false,
      message: 'Şifre, kullanıcı adınızı içeremez'
    };
  }

  return {
    isValid: true,
    message: ''
  };
};

interface LoginFormProps {
  onLogin: (values: any) => void;
  onShowRegister: () => void;
  initialValues?: {
    username?: string;
    email?: string;
  };
  visible: boolean;
  onCancel: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLogin, onShowRegister, initialValues, visible, onCancel }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [isUsernameEditable, setIsUsernameEditable] = useState(true);

  // Form değerlerini izle ve gerekli durumda güncelle
  useEffect(() => {
    if (visible) {
      // Form değerlerini sıfırla
      form.resetFields();
      
      // Eğer initialValues varsa ve username içeriyorsa
      if (initialValues?.username) {
        form.setFieldsValue({
          username: initialValues.username
        });
        setIsUsernameEditable(true); // Kullanıcı adı düzenlenebilir olsun
      } else {
        setIsUsernameEditable(true); // Normal giriş durumunda da düzenlenebilir
      }
    }
  }, [visible, initialValues, form]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      // Backend'e giriş isteği gönder
      const response = await login(values.username, values.password);
      
      // Parent component'e login bilgilerini gönder
      onLogin(response);
      onCancel(); // Modal'ı kapat
    } catch (error: any) {
      message.error(error.message || 'Giriş yapılırken bir hata oluştu. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  const handleUsernameClick = () => {
    // Kullanıcı adı alanına tıklandığında düzenlenebilir yap
    setIsUsernameEditable(true);
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      const response = await signInWithGoogle();
      onLogin(response);
      onCancel();
    } catch (error: any) {
      message.error(error.message || 'Google ile giriş yapılırken bir hata oluştu. Lütfen tekrar deneyin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      visible={visible}
      onCancel={onCancel}
      footer={null}
      width={420}
      className="auth-modal"
      maskClosable={false}
      centered
      style={{ borderRadius: '16px', overflow: 'hidden' }}
      bodyStyle={{ borderRadius: '16px' }}
    >
      <div className="w-full">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-[#43426e] mb-2">Giriş Yap</h2>
          <p className="text-gray-600">Hesabınıza giriş yaparak devam edin</p>
        </div>
        
        <Form
          form={form}
          name="login"
          onFinish={handleSubmit}
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: 'Lütfen kullanıcı adınızı girin' },
              { min: 3, message: 'Kullanıcı adı en az 3 karakter olmalıdır' }
            ]}
          >
            <Input
              prefix={<UserOutlined className="text-gray-400" />}
              placeholder="Kullanıcı Adı"
              size="large"
              className={`rounded-lg ${!isUsernameEditable ? 'cursor-pointer hover:border-[#43426e]' : ''}`}
              readOnly={!isUsernameEditable}
              onClick={handleUsernameClick}
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Lütfen şifrenizi girin' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value) {
                    return Promise.resolve();
                  }
                  const username = getFieldValue('username');
                  const validation = validatePassword(value, username);
                  if (!validation.isValid) {
                    return Promise.reject(new Error(validation.message));
                  }
                  return Promise.resolve();
                },
              })
            ]}
            hasFeedback
          >
            <Input.Password
              prefix={<LockOutlined className="text-gray-400" />}
              placeholder="Şifre"
              size="large"
              className="rounded-lg"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              loading={loading}
              className="w-full h-12 custom-gradient-button border-0 text-lg font-medium rounded-button"
            >
              {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
            </Button>
          </Form.Item>

          <div className="relative my-6">
            <Divider className="border-gray-200">
              <span className="text-gray-500 text-sm px-4">veya</span>
            </Divider>
          </div>

          <Button
            size="large"
            className="w-full h-12 bg-white hover:bg-gray-50 border border-gray-200 rounded-button flex items-center justify-center space-x-2 transition-colors group"
            onClick={handleGoogleLogin}
            loading={loading}
          >
            <div className="flex items-center justify-center space-x-3">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21.8055 10.0415H21V10H12V14H17.6515C16.827 16.3285 14.6115 18 12 18C8.6865 18 6 15.3135 6 12C6 8.6865 8.6865 6 12 6C13.5295 6 14.921 6.577 15.9805 7.5195L18.809 4.691C17.023 3.0265 14.634 2 12 2C6.4775 2 2 6.4775 2 12C2 17.5225 6.4775 22 12 22C17.5225 22 22 17.5225 22 12C22 11.3295 21.931 10.675 21.8055 10.0415Z" fill="#FFC107"/>
                <path d="M3.15302 7.3455L6.43852 9.755C7.32752 7.554 9.48052 6 12 6C13.5295 6 14.921 6.577 15.9805 7.5195L18.809 4.691C17.023 3.0265 14.634 2 12 2C8.15902 2 4.82802 4.1685 3.15302 7.3455Z" fill="#FF3D00"/>
                <path d="M12 22C14.583 22 16.93 21.0115 18.7045 19.404L15.6095 16.785C14.5718 17.5742 13.3038 18.001 12 18C9.39897 18 7.19047 16.3415 6.35847 14.027L3.09747 16.5395C4.75247 19.778 8.11347 22 12 22Z" fill="#4CAF50"/>
                <path d="M21.8055 10.0415H21V10H12V14H17.6515C17.2571 15.1082 16.5467 16.0766 15.608 16.7855L15.6095 16.785L18.7045 19.404C18.4855 19.6025 22 17 22 12C22 11.3295 21.931 10.675 21.8055 10.0415Z" fill="#1976D2"/>
              </svg>
              <span className="text-[15px] font-medium text-gray-600 group-hover:text-gray-800">
                Google ile Giriş Yap
              </span>
            </div>
          </Button>

          <div className="text-center text-gray-600 mt-6">
            Hesabınız yok mu?{' '}
            <button 
              onClick={onShowRegister}
              className="text-[#43426e] hover:text-[#635e9c] font-medium transition-colors duration-200"
            >
              Kayıt Ol
            </button>
          </div>
        </Form>
      </div>
    </Modal>
  );
};

export default LoginForm; 