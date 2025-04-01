import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Upload, message } from 'antd';
import { UserOutlined, MailOutlined, PictureOutlined, LockOutlined, CloseOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import type { UploadProps } from 'antd';
import { updateUserProfile, changePassword, updateProfilePhoto } from '../services/authService';

interface ProfilDüzenleFormProps {
  onCancel: () => void;
  onSuccess: () => void;
  initialValues: {
    username: string;
    email: string;
    bio: string;
    foto?: string;
    isim?: string;
    soyisim?: string;
  };
}

const ProfilDüzenleForm: React.FC<ProfilDüzenleFormProps> = ({ onCancel, onSuccess, initialValues }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [photoChanged, setPhotoChanged] = useState(false);

  // Eğer initialValues içinde foto varsa, fileList'i oluştur
  useEffect(() => {
    if (initialValues.foto && initialValues.foto !== '') {
      setFileList([
        {
          uid: '-1',
          name: 'profile-photo.jpg',
          status: 'done',
          url: initialValues.foto,
        },
      ]);
    }
  }, [initialValues.foto]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const userId = localStorage.getItem('userID');
      if (!userId) {
        throw new Error('Kullanıcı ID bulunamadı');
      }

      // 1. Fotoğraf yükleme işlemi
      let newPhotoUrl: string | null = null;
      if (photoChanged && fileList.length > 0 && fileList[0].originFileObj) {
        try {
          // Fotoğrafı PUT isteği ile yükle
          const photoResponse = await updateProfilePhoto(fileList[0].originFileObj);
          if (photoResponse && photoResponse.foto) {
            newPhotoUrl = photoResponse.foto;
            // Yeni fotoğraf URL'sini localStorage'a kaydet
            if (newPhotoUrl) {
              localStorage.setItem('userPhoto', newPhotoUrl);
            }
          }
        } catch (photoError: any) {
          console.error('Fotoğraf yükleme hatası:', photoError);
          message.error('Fotoğraf yüklenemedi: ' + (photoError.message || 'Bilinmeyen hata'));
          return; // Fotoğraf yüklenemezse işlemi durdur
        }
      }

      // 2. Profil bilgilerini güncelle
      const updateData = {
        first_name: values.isim,
        last_name: values.soyisim,
        bio: values.bio,
        foto: newPhotoUrl || localStorage.getItem('userPhoto') // Yeni fotoğraf yoksa mevcut fotoğrafı kullan
      };

      // Profil bilgilerini PUT isteği ile güncelle
      const profileUpdateResult = await updateUserProfile(userId, updateData);

      if (profileUpdateResult) {
        // Başarılı güncelleme durumunda localStorage'ı güncelle
        localStorage.setItem('userIsim', values.isim || '');
        localStorage.setItem('userSoyisim', values.soyisim || '');
        localStorage.setItem('userBio', values.bio || '');

        // 3. Şifre değiştirme işlemi (eğer gerekli alanlar doldurulmuşsa)
        if (values.currentPassword && values.newPassword && values.confirmPassword) {
          try {
            await changePassword(
              values.currentPassword,
              values.newPassword,
              values.confirmPassword
            );
            message.success('Profil bilgileri ve şifre başarıyla güncellendi');
          } catch (passwordError: any) {
            message.error('Şifre güncellenemedi: ' + (passwordError.message || 'Bilinmeyen hata'));
          }
        } else {
          message.success('Profil bilgileri başarıyla güncellendi');
        }

        // Modal'ı kapat ve ana sayfayı yenile
        onSuccess();
      }
    } catch (error: any) {
      console.error('Profil güncelleme hatası:', error);
      message.error('Profil güncellenirken bir hata oluştu: ' + (error.message || 'Bilinmeyen hata'));
    } finally {
      setLoading(false);
    }
  };

  const uploadProps: UploadProps = {
    onRemove: (file) => {
      const index = fileList.indexOf(file);
      const newFileList = fileList.slice();
      newFileList.splice(index, 1);
      setFileList(newFileList);
      setPhotoChanged(true);
    },
    beforeUpload: (file) => {
      // Dosya tipi kontrolü
      const isImage = file.type.startsWith('image/');
      if (!isImage) {
        message.error('Sadece resim dosyaları yükleyebilirsiniz!');
        return Upload.LIST_IGNORE;
      }
      
      // Dosya boyutu kontrolü (5MB)
      const isLessThan5M = file.size / 1024 / 1024 < 5;
      if (!isLessThan5M) {
        message.error('Resim 5MB\'den küçük olmalıdır!');
        return Upload.LIST_IGNORE;
      }
      
      // Yeni dosyayı fileList'e ekle
      setFileList([{
        uid: '-1',
        name: file.name,
        status: 'done',
        originFileObj: file
      }]);
      setPhotoChanged(true);
      return false;
    },
    fileList,
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={initialValues}
      className="w-full"
    >
      <div className="grid grid-cols-2 gap-6">
        {/* Sol Sütun - Kişisel Bilgiler */}
        <div className="space-y-4">
          <div className="flex justify-center mb-6">
            <Upload
              {...uploadProps}
              showUploadList={false}
            >
              <div className="relative group cursor-pointer">
                <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-white shadow-lg transition-transform duration-300 group-hover:scale-105">
                  {fileList.length > 0 ? (
                    <img 
                      src={fileList[0].originFileObj ? URL.createObjectURL(fileList[0].originFileObj) : fileList[0].url} 
                      alt="Avatar" 
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-r from-[#43426e] to-[#635e9c] flex items-center justify-center">
                      <UserOutlined className="text-white text-4xl" />
                    </div>
                  )}
                  
                  {/* Hover Overlay */}
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col items-center justify-center">
                    <PictureOutlined className="text-white text-2xl mb-2" />
                    <span className="text-white text-sm font-medium">Fotoğraf Değiştir</span>
                  </div>
                </div>

                {/* Remove Photo Button */}
                {fileList.length > 0 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setFileList([]);
                      setPhotoChanged(true);
                    }}
                    className="absolute -bottom-2 -right-2 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center shadow-md hover:bg-red-600 transition-colors duration-200 z-10"
                  >
                    <CloseOutlined style={{ fontSize: '14px' }} />
                  </button>
                )}

                {/* Loading Indicator */}
                {loading && (
                  <div className="absolute inset-0 bg-black/30 rounded-full flex items-center justify-center">
                    <div className="w-12 h-12">
                      <svg className="animate-spin" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="white" strokeWidth="4" fill="none" />
                        <path
                          className="opacity-75"
                          fill="white"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            </Upload>
          </div>

          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Kullanıcı adı gerekli' }]}
            className="mb-3"
          >
            <Input 
              prefix={<UserOutlined className="text-gray-400" />} 
              placeholder="Kullanıcı Adı"
              className="rounded-lg bg-gray-50"
              disabled
            />
          </Form.Item>

          <div className="grid grid-cols-2 gap-3">
            <Form.Item
              name="isim"
              rules={[{ required: true, message: 'İsim gerekli' }]}
              className="mb-3"
            >
              <Input 
                placeholder="İsim"
                className="rounded-lg"
              />
            </Form.Item>

            <Form.Item
              name="soyisim"
              rules={[{ required: true, message: 'Soyisim gerekli' }]}
              className="mb-3"
            >
              <Input 
                placeholder="Soyisim"
                className="rounded-lg"
              />
            </Form.Item>
          </div>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'E-posta gerekli' },
              { type: 'email', message: 'Geçersiz e-posta' }
            ]}
            className="mb-3"
          >
            <Input 
              prefix={<MailOutlined className="text-gray-400" />} 
              placeholder="E-posta"
              className="rounded-lg bg-gray-50"
              disabled
            />
          </Form.Item>

          <Form.Item
            name="bio"
            className="mb-3"
          >
            <Input.TextArea 
              placeholder="Biyografi"
              rows={3}
              className="rounded-lg"
            />
          </Form.Item>
        </div>

        {/* Sağ Sütun - Şifre Değiştirme */}
        <div className="space-y-4 border-l border-gray-100 pl-6 flex flex-col">
          <h3 className="font-medium text-gray-600 mb-2">Şifre Değiştirme</h3>
          
          <Form.Item
            name="currentPassword"
            rules={[
              { 
                required: false,
                validator: (_, value) => {
                  // Eğer şifre alanlarından herhangi biri doluysa, hepsi dolu olmalı
                  const { newPassword, confirmPassword } = form.getFieldsValue();
                  const anyPasswordFieldFilled = value || newPassword || confirmPassword;
                  
                  if (anyPasswordFieldFilled && !value) {
                    return Promise.reject('Mevcut şifre gerekli');
                  }
                  return Promise.resolve();
                }
              }
            ]}
            className="mb-3"
          >
            <Input.Password 
              prefix={<LockOutlined className="text-gray-400" />} 
              placeholder="Mevcut Şifre"
              className="rounded-lg"
            />
          </Form.Item>

          <Form.Item
            name="newPassword"
            dependencies={['currentPassword']}
            rules={[
              { 
                required: false,
                validator: (_, value) => {
                  // Eğer mevcut şifre doluysa, yeni şifre de dolu olmalı
                  const { currentPassword, confirmPassword } = form.getFieldsValue();
                  const anyPasswordFieldFilled = currentPassword || value || confirmPassword;
                  
                  if (anyPasswordFieldFilled && !value) {
                    return Promise.reject('Yeni şifre gerekli');
                  }
                  return Promise.resolve();
                }
              }
            ]}
            className="mb-3"
          >
            <Input.Password 
              prefix={<LockOutlined className="text-gray-400" />} 
              placeholder="Yeni Şifre"
              className="rounded-lg"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['newPassword', 'currentPassword']}
            rules={[
              { 
                required: false,
                validator: (_, value) => {
                  const { currentPassword, newPassword } = form.getFieldsValue();
                  const anyPasswordFieldFilled = currentPassword || newPassword || value;
                  
                  if (anyPasswordFieldFilled && !value) {
                    return Promise.reject('Şifre tekrarı gerekli');
                  }
                  
                  if (newPassword && value && newPassword !== value) {
                    return Promise.reject('Şifreler eşleşmiyor');
                  }
                  
                  return Promise.resolve();
                }
              }
            ]}
            className="mb-3"
          >
            <Input.Password 
              prefix={<LockOutlined className="text-gray-400" />} 
              placeholder="Yeni Şifre (Tekrar)"
              className="rounded-lg"
            />
          </Form.Item>
          
          <div className="flex-grow"></div>
          
          <div className="flex justify-end space-x-3 mt-auto pt-3">
            <Button 
              onClick={onCancel}
              className="px-4 rounded-lg border-[#43426e] text-[#43426e] hover:bg-gradient-to-r hover:from-[#43426e] hover:to-[#635e9c] hover:text-white hover:border-0 transition-all"
            >
              İptal
            </Button>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              className="custom-gradient-button border-0 px-4 rounded-lg"
            >
              Kaydet
            </Button>
          </div>
        </div>
      </div>
    </Form>
  );
};

export default ProfilDüzenleForm; 