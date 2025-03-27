import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message, Modal } from 'antd';
import { UserOutlined, MailOutlined, LockOutlined } from '@ant-design/icons';
import '../styles/auth.css';

// Define empty handler functions for pointer events
const emptyPointerHandler = () => {};

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
      // Simüle edilmiş başarılı kayıt
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Başarılı kayıt mesajı göster
      message.success('Kayıt başarılı! Giriş yapabilirsiniz.');
      
      // Parent component'e kayıt bilgilerini gönder
      onRegister(values);
      onCancel(); // Modal'ı kapat
    } catch (error: any) {
      message.error('Kayıt olurken bir hata oluştu. Lütfen tekrar deneyin.');
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
              prefix={<UserOutlined className="text-gray-400" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />}
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
              prefix={<MailOutlined className="text-gray-400" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />}
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
              { min: 6, message: 'Şifre en az 6 karakter olmalıdır' },
              {
                pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{6,}$/,
                message: 'Şifre en az bir harf ve bir rakam içermelidir'
              }
            ]}
            hasFeedback
          >
            <Input.Password
              prefix={<LockOutlined className="text-gray-400" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />}
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
              prefix={<LockOutlined className="text-gray-400" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />}
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