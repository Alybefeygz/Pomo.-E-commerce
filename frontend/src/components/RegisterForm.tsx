import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message, Modal } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined } from '@ant-design/icons';
import '../styles/auth.css';
import { register } from '../services/authService';

// Define empty handler functions for pointer events
const emptyPointerHandler = () => {};

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

interface RegisterFormProps {
  onRegister: (values: { username: string; email: string; password: string }) => void;
  onBackToLogin: () => void;
  visible: boolean;
  onCancel: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onRegister, onBackToLogin, visible, onCancel }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  // Form değerlerini sıfırla
  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible, form]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      // Backend'e kayıt isteği gönder
      const response = await register(
        values.username,
        values.email,
        values.password, // password1
        values.confirmPassword // password2
      );
      
      // Başarılı kayıt mesajı göster
      message.success('Kayıt başarılı! Giriş yapabilirsiniz.');
      
      // Parent component'e kayıt bilgilerini gönder
      onRegister({
        username: values.username,
        email: values.email,
        password: values.password
      });

      // Modal'ı kapat ve giriş formuna yönlendir
      onCancel();
      onBackToLogin();
    } catch (error: any) {
      // Backend'den gelen hata mesajlarını kontrol et
      if (error.response?.data) {
        const errors = error.response.data;
        Object.keys(errors).forEach(key => {
          if (Array.isArray(errors[key])) {
            message.error(`${key}: ${errors[key][0]}`);
          } else if (typeof errors[key] === 'string') {
            message.error(`${key}: ${errors[key]}`);
          }
        });
      } else {
        message.error(error.message || 'Kayıt olurken bir hata oluştu. Lütfen tekrar deneyin.');
      }
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
          <h2 className="text-2xl font-semibold text-[#43426e] mb-2">Kayıt Ol</h2>
          <p className="text-gray-600">Yeni bir hesap oluşturarak devam edin</p>
        </div>
        
        <Form
          form={form}
          name="register"
          onFinish={handleSubmit}
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: 'Lütfen kullanıcı adınızı girin' },
              { min: 3, message: 'Kullanıcı adı en az 3 karakter olmalıdır' },
              { pattern: /^[a-zA-Z0-9_]+$/, message: 'Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir' }
            ]}
            hasFeedback
          >
            <Input
              prefix={<UserOutlined className="text-gray-400" />}
              placeholder="Kullanıcı Adı"
              size="large"
              className="rounded-lg"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Lütfen e-posta adresinizi girin' },
              { type: 'email', message: 'Geçerli bir e-posta adresi girin' }
            ]}
            hasFeedback
          >
            <Input
              prefix={<MailOutlined className="text-gray-400" />}
              placeholder="E-posta"
              size="large"
              className="rounded-lg"
              autoComplete="email"
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
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            hasFeedback
            rules={[
              { required: true, message: 'Lütfen şifrenizi tekrar girin' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Şifreler eşleşmiyor'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined className="text-gray-400" />}
              placeholder="Şifre Tekrarı"
              size="large"
              className="rounded-lg"
              autoComplete="new-password"
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
              {loading ? 'Kayıt Yapılıyor...' : 'Kayıt Ol'}
            </Button>
          </Form.Item>

          <div className="text-center text-gray-600">
            Zaten hesabınız var mı?{' '}
            <button 
              onClick={onBackToLogin}
              className="text-[#43426e] hover:text-[#635e9c] font-medium transition-colors duration-200"
            >
              Giriş Yap
            </button>
          </div>
        </Form>
      </div>
    </Modal>
  );
};

export default RegisterForm; 