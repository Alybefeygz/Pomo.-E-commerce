import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message, Modal } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import '../styles/auth.css';
import { login } from '../services/authService';

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
      
      // Başarılı giriş mesajı göster
      message.success('Giriş başarılı!');
      
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

          <div className="text-center text-gray-600">
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