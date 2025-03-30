// @ts-nocheck
import React, { useState, useEffect } from "react";
import { Input, Select, Button, message, Avatar, Dropdown, Menu, Layout, Form, Card, Typography } from "antd";
import {
  MailOutlined,
  BoxPlotOutlined,
  DollarOutlined,
  CalculatorOutlined,
  UserOutlined,
  LoginOutlined,
  LogoutOutlined,
  DownOutlined,
  UpOutlined,
  AppstoreOutlined,
  PercentageOutlined,
} from "@ant-design/icons";
import "./custom-button.css"; // Import custom CSS
import "./index.css";
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import { getUserInfo, getUserProfileById } from './services/authService';

// Define empty handler functions for pointer events
const emptyPointerHandler = () => {};

// CSS for container transitions
// const containerTransitionStyles = {
//   enter: "transition-all duration-500 ease-in-out transform opacity-0 translate-y-20",
//   enterActive: "opacity-100 translate-y-0",
//   exit: "transition-all duration-500 ease-in-out transform opacity-100 translate-y-0",
//   exitActive: "opacity-0 translate-y-20",
// };

// Kategori verileri
const categoryData = [
  {
    kategori_id: 1,
    kategori_adi: "Bahçe & Elektrikli El Aletleri",
    alt_kategoriler: [
      {
        alt_kategori_id: 101,
        alt_kategori_adi: "Bahçe",
        urun_gruplari: [
          {
            urun_grubu_id: 1001,
            urun_grubu_adi: "Bahçe Dekorasyonu, Çitler, Gübre, Kuzine ve Sobalar, Saksı, Şömine, Tohumlar, Torf ve Topraklar",
            komisyon_orani: "20.00"
          },
          {
            urun_grubu_id: 1002,
            urun_grubu_adi: "Bahçe Aletleri",
            komisyon_orani: "18.50"
          }
        ]
      },
      {
        alt_kategori_id: 102,
        alt_kategori_adi: "El Aletleri",
        urun_gruplari: [
          {
            urun_grubu_id: 1003,
            urun_grubu_adi: "Elektrikli El Aletleri",
            komisyon_orani: "15.00"
          },
          {
            urun_grubu_id: 1004,
            urun_grubu_adi: "Manuel El Aletleri",
            komisyon_orani: "12.50"
          }
        ]
      }
    ]
  },
  {
    kategori_id: 2,
    kategori_adi: "Elektronik",
    alt_kategoriler: [
      {
        alt_kategori_id: 201,
        alt_kategori_adi: "Bilgisayar",
        urun_gruplari: [
          {
            urun_grubu_id: 2001,
            urun_grubu_adi: "Dizüstü Bilgisayarlar",
            komisyon_orani: "10.00"
          },
          {
            urun_grubu_id: 2002,
            urun_grubu_adi: "Masaüstü Bilgisayarlar",
            komisyon_orani: "12.00"
          }
        ]
      },
      {
        alt_kategori_id: 202,
        alt_kategori_adi: "Telefon",
        urun_gruplari: [
          {
            urun_grubu_id: 2003,
            urun_grubu_adi: "Akıllı Telefonlar",
            komisyon_orani: "8.00"
          },
          {
            urun_grubu_id: 2004,
            urun_grubu_adi: "Telefon Aksesuarları",
            komisyon_orani: "25.00"
          }
        ]
      }
    ]
  }
];

const App: React.FC = () => {
  // const [form] = Form.useForm();
  const [email, setEmail] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [width, setWidth] = useState("");
  const [length, setLength] = useState("");
  const [height, setHeight] = useState("");
  const [weight, setWeight] = useState("");
  const [carrier, setCarrier] = useState("");
  const [shippingFee, setShippingFee] = useState(0);
  const [carrierName, setCarrierName] = useState("");
  // const [desiValue, setDesiValue] = useState(0);
  // const [desiKgValue, setDesiKgValue] = useState(0);
  const [username, setUsername] = useState("");
  const [showProfileOptions, setShowProfileOptions] = useState(false);
  const [activeContainer, setActiveContainer] = useState("first");
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentPage, setCurrentPage] = useState("home");
  
  // Komisyon hesaplama state'leri
  const [activeSection, setActiveSection] = useState("shipping"); // "shipping" veya "commission" veya "price"
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedSubCategory, setSelectedSubCategory] = useState(null);
  const [selectedProductGroup, setSelectedProductGroup] = useState(null);
  const [commissionRate, setCommissionRate] = useState(null);
  
  // Fiyat hesaplama state'leri
  const [productName, setProductName] = useState("");
  const [productCost, setProductCost] = useState("");
  const [packagingCost, setPackagingCost] = useState("");
  const [vatRate, setVatRate] = useState("");
  const [profitRate, setProfitRate] = useState("");
  const [priceCalculationResult, setPriceCalculationResult] = useState(null);
  
  // Dropdown için filtreleme state'leri
  const [categorySearchText, setCategorySearchText] = useState("");
  const [subCategorySearchText, setSubCategorySearchText] = useState("");
  const [productGroupSearchText, setProductGroupSearchText] = useState("");
  
  // Kullanılabilir kategorileri ve diğer seçenekleri filtreleme
  // const filteredCategories = categoryData.filter(category => 
  //   category.kategori_adi.toLowerCase().includes(categorySearchText.toLowerCase())
  // );
  
  // const filteredSubCategories = selectedCategory 
  //   ? selectedCategory.alt_kategoriler.filter(subCat => 
  //       subCat.alt_kategori_adi.toLowerCase().includes(subCategorySearchText.toLowerCase())
  //     )
  //   : [];
    
  // const filteredProductGroups = selectedSubCategory 
  //   ? selectedSubCategory.urun_gruplari.filter(group => 
  //       group.urun_grubu_adi.toLowerCase().includes(productGroupSearchText.toLowerCase())
  //     )
  //   : [];

  // const carriers = [
  //   { value: "fedex", label: "FedEx Express" },
  //   { value: "dhl", label: "DHL Global" },
  //   { value: "ups", label: "UPS Worldwide" },
  // ];

  // Kargo firmaları için API state'i
  const [kargoFirmalar, setKargoFirmalar] = useState([
    { value: "1", label: "Aras Kargo" },
    { value: "2", label: "MNG Kargo" },
    { value: "3", label: "Yurtiçi Kargo" },
    { value: "4", label: "PTT Kargo" },
    { value: "5", label: "Sürat Kargo" }
  ]);
  
  // Token kontrolü için useEffect
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const storedUsername = localStorage.getItem('username');
    const storedEmail = localStorage.getItem('email');
    
    if (token) {
      setIsLoggedIn(true);
      
      // Eğer localStorage'da username varsa, onu kullan
      if (storedUsername) {
        setUsername(storedUsername);
      }
      
      // Eğer localStorage'da email varsa, onu kullan
      if (storedEmail) {
        setEmail(storedEmail);
      }
      
      // Eğer username yoksa ama token varsa, kullanıcı bilgilerini almayı dene
      if (!storedUsername || !storedEmail) {
        getUserInfo().then(userData => {
          if (userData) {
            if (userData.username) {
              setUsername(userData.username);
              localStorage.setItem('username', userData.username);
            }
            
            if (userData.email) {
              setEmail(userData.email);
              localStorage.setItem('email', userData.email);
            }
            
            if (userData.id) {
              localStorage.setItem('userID', userData.id.toString());
            }
            
            if (userData.bio) {
              localStorage.setItem('userBio', userData.bio);
            }
            
            if (userData.foto) {
              localStorage.setItem('userPhoto', userData.foto);
            }
          }
        }).catch(error => {
          console.error("Kullanıcı bilgileri alınamadı:", error);
        });
      }
    }
  }, []);

  const validateEmail = (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  // const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  //   const newEmail = e.target.value;
  //   setEmail(newEmail);
  // };

  // const calculateShipping = async () => {
  //   if (!width || !length || !height || !weight || !carrier) {
  //     message.error("Lütfen tüm alanları doldurunuz.");
  //     return;
  //   }

  //   // API isteği yapacak gibi simüle edelim
  //   try {
  //     // Gerçek API çağrısı burada olacak
  //     // Örnek API yanıtı:
  //     const apiResponse = {
  //       shipping_cost: parseFloat(width) * parseFloat(length) * parseFloat(height) * parseFloat(weight) / 1000,
  //       desi: (parseFloat(width) * parseFloat(length) * parseFloat(height)) / 3000,
  //       desi_kg: Math.max((parseFloat(width) * parseFloat(length) * parseFloat(height)) / 3000, parseFloat(weight)),
  //       carrier_name: carriers.find(c => c.value === carrier)?.label || "Bilinmeyen"
  //     };

  //     setShippingFee(apiResponse.shipping_cost.toFixed(2));
  //     setCarrierName(apiResponse.carrier_name);
  //     
  //     setActiveContainer("second");
  //     setTimeout(() => {
  //       setIsAnimating(false);
  //     }, 500);
  //   } catch (error) {
  //     console.error("Error calculating shipping:", error);
  //     message.error("Kargo hesaplama sırasında bir hata oluştu.");
  //   }
  // };

  // const calculateCommission = () => {
  //   if (!selectedProductGroup) {
  //     message.error("Lütfen bir ürün grubu seçiniz.");
  //     return;
  //   }

  //   setCommissionRate(selectedProductGroup.komisyon_orani);
  // };

  // const calculatePrice = () => {
  //   if (!productCost || !packagingCost || !vatRate || !profitRate) {
  //     message.error("Lütfen tüm alanları doldurunuz.");
  //     return;
  //   }

  //   try {
  //     // Parse values to ensure they are numbers
  //     const cost = parseFloat(productCost);
  //     const packaging = parseFloat(packagingCost);
  //     const vat = parseFloat(vatRate) / 100;
  //     const profit = parseFloat(profitRate) / 100;

  //     // Base calculation
  //     const baseTotal = cost + packaging;
  //     const profitAmount = baseTotal * profit;
  //     const subtotal = baseTotal + profitAmount;
  //     const vatAmount = subtotal * vat;
  //     const totalPrice = subtotal + vatAmount;

  //     // Set the results
  //     setPriceCalculationResult({
  //       baseTotal: baseTotal.toFixed(2),
  //       profitAmount: profitAmount.toFixed(2),
  //       subtotal: subtotal.toFixed(2),
  //       vatAmount: vatAmount.toFixed(2),
  //       totalPrice: totalPrice.toFixed(2)
  //     });

  //   } catch (error) {
  //     console.error("Error calculating price:", error);
  //     message.error("Fiyat hesaplama sırasında bir hata oluştu.");
  //   }
  // };

  // const handleCategoryChange = (value) => {
  //   const category = categoryData.find(cat => cat.kategori_id === value);
  //   setSelectedCategory(category);
  //   setSelectedSubCategory(null);
  //   setSelectedProductGroup(null);
  //   setCommissionRate(null);
  // };
  
  // const handleSubCategoryChange = (value) => {
  //   const subCategory = selectedCategory.alt_kategoriler.find(subCat => subCat.alt_kategori_id === value);
  //   setSelectedSubCategory(subCategory);
  //   setSelectedProductGroup(null);
  //   setCommissionRate(null);
  // };
  
  // const handleProductGroupChange = (value) => {
  //   const productGroup = selectedSubCategory.urun_gruplari.find(group => group.urun_grubu_id === value);
  //   setSelectedProductGroup(productGroup);
  // };
  
  // const switchSection = (section) => {
  //   setActiveSection(section);
  // };

  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [registrationData, setRegistrationData] = useState<{ username?: string; email?: string }>({});

  const handleLogin = async (values: any) => {
    try {
      // Backend'den dönen yanıt artık token ve kullanıcı bilgilerini içeriyor
      // values parametresi artık login API'den dönen yanıtı içeriyor: {key: "token", user: {...}}
      console.log("Login response:", values);
      
      // Kullanıcı bilgilerini state'e kaydet
      setIsLoggedIn(true);
      
      // Backend'den gelen kullanıcı bilgilerini kullan
      if (values.user) {
        setUsername(values.user.username);
        setEmail(values.user.email);
        
        // Kullanıcı bilgilerini localStorage'a kaydet
        localStorage.setItem('username', values.user.username);
        localStorage.setItem('email', values.user.email);
        
        // Kullanıcı ID'sini localStorage'a kaydet
        if (values.user.id) {
          localStorage.setItem('userID', values.user.id.toString());
        }
        
        // Biyografi bilgisini localStorage'a kaydet
        if (values.user.bio) {
          localStorage.setItem('userBio', values.user.bio);
        }
        
        // Fotoğraf bilgisini de localStorage'a kaydedebilirsiniz (URL olarak)
        if (values.user.foto) {
          localStorage.setItem('userPhoto', values.user.foto);
        }
        
        // Diğer kullanıcı bilgileri de values.user içinde mevcut (id, foto, bio)
      }
      
      setShowLoginModal(false);
      setShowRegisterModal(false);
      
      // Ana sayfaya yönlendir
      setCurrentPage("home");
    } catch (error) {
      message.error('Giriş yapılırken bir hata oluştu');
    }
  };

  const handleRegister = async (values: { username: string; email: string; password: string }) => {
    try {
      // Simüle edilmiş API çağrısı
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Kayıt bilgilerini sakla
      setRegistrationData({
        username: values.username,
        email: values.email
      });
      
      // Giriş modalını göster
      setShowRegisterModal(false);
      setShowLoginModal(true);
    } catch (error) {
      message.error('Kayıt olurken bir hata oluştu');
    }
  };

  const handleLoginClick = () => {
    setShowLoginModal(true);
  };

  const handleShowRegister = () => {
    setShowLoginModal(false);
    setShowRegisterModal(true);
  };

  const handleBackToLogin = () => {
    setShowRegisterModal(false);
    setShowLoginModal(true);
  };

  const handleLogout = () => {
    // Tüm kullanıcı bilgilerini localStorage'dan sil
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    localStorage.removeItem('userID');
    localStorage.removeItem('userBio');
    localStorage.removeItem('userPhoto');
    
    // State'leri sıfırla
    setIsLoggedIn(false);
    setEmail("");
    setUsername("");
    setWidth("");
    setLength("");
    setHeight("");
    setWeight("");
    setCarrier("");
    setShippingFee(0);
    setProductName("");
    setProductCost("");
    setPackagingCost("");
    setVatRate("");
    setProfitRate("");
    setPriceCalculationResult(null);
    setShowProfileOptions(false);
    setActiveContainer("first");
    setCurrentPage("home");
  };
  
  // const toggleProfileOptions = () => {
  //   setShowProfileOptions(!showProfileOptions);
  // };

  const toggleContainer = () => {
    setIsAnimating(true);
    setTimeout(() => {
      setActiveContainer(activeContainer === "first" ? "second" : "first");
      setTimeout(() => {
        setIsAnimating(false);
      }, 50);
    }, 300);
  };

  // Get transition class based on container state - This is no longer needed
  // const getContainerClass = (container) => {
  //   if (container === activeContainer) {
  //     return isAnimating 
  //       ? "animate__animated animate__fadeIn" 
  //       : "";
  //   }
  //   return "hidden";
  // };

  // Reset functions
  // const resetForm = () => {
  //   setEmail("");
  //   setWidth("");
  //   setLength("");
  //   setHeight("");
  //   setWeight("");
  //   setCarrier("");
  //   setShippingFee(0);
  //   setCarrierName("");
  //   setActiveContainer("first");
  // };

  // const KargoHesaplamaForm = () => {
  //   // ... existing code ...
  // };

  const handleHomeClick = () => {
    setCurrentPage("home");
    setActiveContainer("first");
  };

  const handleCalculationsClick = () => {
    setCurrentPage("calculations");
    setActiveContainer("first");
    setActiveSection("shipping"); // Reset to shipping section
  };

  const handleServicesClick = () => {
    setCurrentPage("services");
    setActiveContainer("first");
  };

  const handleProfileClick = () => {
    setCurrentPage("profile");
    setActiveContainer("first");
    
    // Kullanıcı ID'sini localStorage'dan al
    const userId = localStorage.getItem('userID');
    
    // Eğer kullanıcı ID varsa, profil bilgilerini getir
    if (userId) {
      // Loading mesajı göster
      const loadingMessage = message.loading('Profil bilgileri yükleniyor...', 0);
      
      // API'den profil bilgilerini al
      getUserProfileById(userId)
        .then(profileData => {
          // Loading mesajını kapat
          loadingMessage();
          
          if (profileData) {
            console.log('Profil bilgileri alındı:', profileData);
            
            // Kullanıcı bilgilerini güncelle ve localStorage'a kaydet
            if (profileData.username) {
              setUsername(profileData.username);
              localStorage.setItem('username', profileData.username);
            }
            
            if (profileData.email) {
              setEmail(profileData.email);
              localStorage.setItem('email', profileData.email);
            }
            
            if (profileData.id) {
              localStorage.setItem('userID', profileData.id.toString());
            }
            
            if (profileData.bio) {
              localStorage.setItem('userBio', profileData.bio);
            }
            
            if (profileData.foto) {
              localStorage.setItem('userPhoto', profileData.foto);
            }
            
            // Başarı mesajı göster
            message.success('Profil bilgileri güncellendi');
          }
        })
        .catch(error => {
          // Loading mesajını kapat
          loadingMessage();
          
          // Hata mesajı göster
          message.error('Profil bilgileri alınırken bir hata oluştu');
          console.error('Profil bilgileri hatası:', error);
        });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col relative">
      {/* Top Navbar */}
      <div className="w-full bg-gray-50 pt-3 pb-2 px-4 flex justify-center">
        <div className="max-w-[1200px] w-full bg-white rounded-xl shadow-lg">
          <div className="flex items-center h-14 px-8 border-b border-gray-100">
            {/* Left: Logo with Navigation */}
            <div className="flex items-center">
              <div 
                className="w-10 h-10 bg-[#43426e] rounded-lg flex items-center justify-center shadow-sm mr-6 cursor-pointer hover:bg-[#635e9c] transition-colors"
                onClick={handleHomeClick}
              >
                <i className="fas fa-dog text-white text-xl"></i>
              </div>
              
              {/* Navigation */}
              <div className="flex">
                <button 
                  className={`text-[#43426e] font-medium px-4 py-4 hover:bg-gray-50 transition-all relative group ${currentPage === "calculations" ? "text-[#635e9c]" : ""}`}
                  onClick={handleCalculationsClick}
                >
                  Hesaplamalar
                  <div className={`absolute bottom-0 left-1/2 transform -translate-x-1/2 h-0.5 bg-[#43426e] transition-all duration-300 ${currentPage === "calculations" ? "w-1/2" : "w-0 group-hover:w-1/2"}`}></div>
                </button>
                <button 
                  className={`text-[#43426e] font-medium px-4 py-4 hover:bg-gray-50 transition-all relative group ${currentPage === "services" ? "text-[#635e9c]" : ""}`}
                  onClick={handleServicesClick}
                >
                  Hizmetler
                  <div className={`absolute bottom-0 left-1/2 transform -translate-x-1/2 h-0.5 bg-[#43426e] transition-all duration-300 ${currentPage === "services" ? "w-1/2" : "w-0 group-hover:w-1/2"}`}></div>
                </button>
              </div>
            </div>
            
            {/* Empty flex spacer */}
            <div className="flex-1"></div>
            
            {/* Right: User area */}
            <div className="w-[400px] flex items-center justify-end">
              {isLoggedIn ? (
                <div className="flex items-center space-x-2">
                  <button 
                    className={`flex items-center px-3 py-1 text-[#43426e] transition-all duration-200 relative group ${currentPage === "profile" ? "text-[#635e9c]" : ""}`}
                    onClick={handleProfileClick}
                  >
                    <UserOutlined className="mr-1" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                    <span>Profil</span>
                    <div className={`absolute bottom-0 left-1/2 transform -translate-x-1/2 h-0.5 bg-[#e7bd99] transition-all duration-300 ${currentPage === "profile" ? "w-1/2" : "w-0 group-hover:w-1/2"}`}></div>
                  </button>
                  <button 
                    className="flex items-center px-3 py-1 text-[#43426e] transition-all duration-200 relative group"
                    onClick={handleLogout}
                  >
                    <LogoutOutlined className="mr-1" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                    <span>Çıkış</span>
                    <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0 h-0.5 bg-[#e7bd99] group-hover:w-1/2 transition-all duration-300"></div>
                  </button>
                  <div className="flex items-center px-4 py-2 bg-gradient-to-r from-[#43426e]/5 to-[#635e9c]/5 rounded-lg border border-[#43426e]/10">
                    <span className="text-[#43426e] font-semibold mr-2">{username}</span>
                    <div className="relative">
                      <Avatar icon={<UserOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />} className="bg-gradient-to-r from-[#43426e] to-[#635e9c]" />
                      <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                    </div>
                  </div>
                </div>
              ) : (
                <button 
                  className="flex items-center text-[#43426e] border border-[#43426e] px-4 py-2 rounded-lg hover:bg-gray-50 transition-all shadow-sm relative group"
                  onClick={handleLoginClick}
                >
                  <LoginOutlined className="mr-2" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                  <span className="font-medium">Giriş</span>
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0 h-0.5 bg-[#e7bd99] group-hover:w-1/2 transition-all duration-300"></div>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content - Using Transition Classes */}
      <div className="flex flex-col items-center pt-3 pb-6 px-4 overflow-hidden">
        {/* Container Wrapper with fixed height */}
        <div className="max-w-[1200px] w-full relative" style={{ minHeight: '600px', height: 'auto' }}>
          {/* First Container */}
          <div 
            className={`absolute top-0 left-0 w-full transition-all duration-700 ease-in-out shadow-lg rounded-xl ${
              activeContainer === "first" 
                ? "opacity-100 transform translate-y-0 z-10" 
                : "opacity-0 transform -translate-y-20 z-0 pointer-events-none"
            }`}
          >
            <div className="bg-white rounded-xl shadow-lg flex flex-col min-h-[600px]">
              {/* Content */}
              <div className="flex px-6 py-5 flex-grow relative">
                {currentPage === "home" ? (
                  <div className="w-full flex items-center justify-center">
                    <h1 className="text-3xl font-bold text-[#43426e]">Ana Sayfa</h1>
                  </div>
                ) : currentPage === "services" ? (
                  <div className="w-full flex items-center justify-center">
                    <h1 className="text-3xl font-bold text-[#43426e]">Hizmetler daha yapılmadı</h1>
                  </div>
                ) : currentPage === "calculations" ? (
                  <div className="w-full flex items-center justify-center">
                    <h1 className="text-3xl font-bold text-[#43426e]">Hesaplamalar daha yapılmadı</h1>
                  </div>
                ) : currentPage === "profile" ? (
                  <div className="w-full flex flex-col items-center">
                    <div className="w-full grid grid-cols-2 gap-8">

                      {/* Sol Panel - Profil Kartı */}
                      <div className="relative overflow-hidden rounded-lg border border-gray-100 p-6 bg-white shadow-sm">
                        <div className="flex items-start justify-between">
                          <h2 className="text-2xl font-medium text-gray-700 mb-6">Profil Bilgileri</h2>
                        </div>

                        <div className="flex items-center mb-6">
                          <div className="relative mr-6">
                            <Avatar 
                              size={80} 
                              icon={!localStorage.getItem('userPhoto') && <UserOutlined style={{ fontSize: '36px' }} onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />}
                              src={localStorage.getItem('userPhoto') || undefined}
                              className="bg-gradient-to-r from-[#43426e] to-[#635e9c]"
                            />
                            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
                          </div>
                          <div>
                            <div className="text-3xl font-bold text-[#43426e]">{username}</div>
                            <div className="text-gray-500">{localStorage.getItem('userID') ? `ID: ${localStorage.getItem('userID')}` : ''}</div>
                          </div>
                        </div>

                        <div className="space-y-4 mb-8">
                          <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-1">E-posta Adresi</h3>
                            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100 flex items-center">
                              <MailOutlined className="text-[#43426e] mr-3" />
                              <span className="text-gray-700">{email}</span>
                            </div>
                          </div>
                          
                          <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-1">Biyografi</h3>
                            <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                              <p className="text-gray-700">
                                {localStorage.getItem('userBio') || "Henüz biyografi girilmemiş."}
                              </p>
                            </div>
                          </div>
                        </div>

                        <Button 
                          type="primary" 
                          className="custom-gradient-button border-0 rounded-lg w-full mb-3"
                        >
                          Profil Fotoğrafını Güncelle
                        </Button>
                        <Button 
                          className="rounded-lg w-full border-[#43426e] text-[#43426e] hover:bg-gradient-to-r hover:from-[#43426e] hover:to-[#635e9c] hover:text-white hover:border-0 transition-all"
                        >
                          Şifreyi Değiştir
                        </Button>
                      </div>

                      {/* Sağ Panel - Hesap Etkinliği */}
                      <div className="relative overflow-hidden rounded-lg border border-gray-100 p-6 bg-white shadow-sm">
                        <div className="flex flex-col items-center justify-center">
                          <div 
                            className="w-32 h-32 bg-[#43426e] rounded-lg flex items-center justify-center shadow-sm mb-6"
                          >
                            <UserOutlined style={{ fontSize: '48px', color: 'white' }} />
                          </div>
                          
                          <div className="bg-gradient-to-r from-[#43426e] to-[#635e9c] p-[2px] rounded-xl w-full mb-6">
                            <div className="bg-white p-5 rounded-xl">
                              <h2 className="text-xl text-gray-600 mb-2 text-center">Hesap Durumu</h2>
                              <div className="text-2xl font-medium text-[#43426e] text-center">
                                Aktif
                              </div>
                            </div>
                          </div>

                          <div className="w-full p-4 bg-gray-50 rounded-lg border border-gray-100 mb-4">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-gray-600">Son Giriş:</span>
                              <span className="text-[#43426e] font-medium">Bugün</span>
                            </div>
                          </div>

                          <div className="w-full p-4 bg-gray-50 rounded-lg border border-gray-100">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-gray-600">Üyelik Tarihi:</span>
                              <span className="text-[#43426e] font-medium">2025</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : showLoginModal ? (
                  <div className="w-full flex items-center justify-center">
                    <LoginForm 
                      onLogin={handleLogin} 
                      onShowRegister={handleShowRegister}
                      initialValues={registrationData}
                      visible={showLoginModal}
                      onCancel={() => setShowLoginModal(false)}
                    />
                  </div>
                ) : showRegisterModal ? (
                  <div className="w-full flex items-center justify-center">
                    <RegisterForm 
                      onRegister={handleRegister}
                      onBackToLogin={handleBackToLogin}
                      visible={showRegisterModal}
                      onCancel={() => setShowRegisterModal(false)}
                    />
                  </div>
                ) : (
                  <>
                    {/* Left Panel */}
                    <div className="w-2/5 pr-8 border-r border-gray-100 flex items-center justify-center">
                      <div className="text-center w-full">
                        <div className="bg-gradient-to-r from-[#43426e] to-[#e7bd99] p-[2px] rounded-xl">
                          <div className="bg-white p-5 rounded-xl">
                            <h2 className="text-xl text-gray-600 mb-2">Hesaplamalar</h2>
                            <div className="text-2xl font-medium text-[#43426e]">
                              Hesaplamalar daha yapılmadı
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Navigation Buttons - Added to the center left of panel */}
                    {(shippingFee > 0 || commissionRate || (activeSection === "price" && priceCalculationResult)) && (
                      <div className="absolute left-4 bottom-4 z-20">
                        <button
                          onClick={toggleContainer}
                          className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-[#43426e] to-[#635e9c] text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:transform hover:scale-110 hover:rotate-12 relative"
                        >
                          {activeContainer === "first" ? (
                            <DownOutlined style={{ fontSize: '18px' }} />
                          ) : (
                            <UpOutlined style={{ fontSize: '18px' }} />
                          )}
                          <div className="absolute inset-0 rounded-full bg-white opacity-0 hover:opacity-20 transition-opacity duration-300"></div>
                        </button>
                      </div>
                    )}
                    
                    {/* Right Panel */}
                    <div className="w-3/5 pl-8 flex flex-col justify-center">
                      <div className="mb-6">
                        <h2 className="text-2xl font-bold text-[#43426e]">Hesaplamalar</h2>
                        <div className="w-16 h-1 bg-[#7b79ae] my-3"></div>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="bg-gray-50 p-6 rounded-xl">
                          <div className="text-xl font-medium text-[#43426e] text-center">
                            Hesaplamalar daha yapılmadı
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        
          {/* Second Container - Positioned below */}
          <div 
            className={`absolute top-0 left-0 w-full transition-all duration-700 ease-in-out shadow-lg rounded-xl ${
              activeContainer === "second" 
                ? "opacity-100 transform translate-y-0 z-10" 
                : "opacity-0 transform translate-y-20 z-0 pointer-events-none"
            }`}
          >
            <div className="bg-white rounded-xl shadow-lg flex flex-col min-h-[600px]">
              <div className="flex px-6 py-5 flex-grow relative">
                {/* Kargo Hesaplama Sonuçları */}
                {activeSection === "shipping" && (
                  <div className="w-full flex rounded-lg p-8">
                    {/* Left Panel - Kargo firması logosu */}
                    <div className="w-2/5 border-r border-gray-200 pr-6">
                      <div className="flex flex-col items-center justify-center space-y-6">
                        <div className="text-center">
                          <h2 className="text-xl text-gray-600 mb-2">Kargo Firması</h2>
                          <div className="w-32 h-32 flex items-center justify-center bg-white shadow-inner rounded-lg p-4">
                            {carrierName && (
                              <div className="text-xl font-bold text-[#43426e] text-center">{carrierName}</div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Right Panel - Hesaplama Sonuçları */}
                    <div className="w-3/5 pl-8 flex flex-col justify-center">
                      <div className="mb-6">
                        <h2 className="text-2xl font-bold text-[#43426e]">Hesaplamalar</h2>
                        <div className="w-16 h-1 bg-[#7b79ae] my-3"></div>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="bg-gray-50 p-6 rounded-xl">
                          <div className="text-xl font-medium text-[#43426e] text-center">
                            Hesaplamalar daha yapılmadı
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Komisyon Hesaplama Sonuçları */}
                {activeSection === "commission" && (
                  <>
                    {/* Left Panel - Komisyon görseli */}
                    <div className="w-2/5 pr-8 border-r border-gray-100 flex items-center justify-center">
                      <div className="text-center w-full">
                        <div className="bg-gradient-to-r from-[#43426e] to-[#e7bd99] p-[2px] rounded-xl">
                          <div className="bg-white p-5 rounded-xl">
                            <h2 className="text-xl text-gray-600 mb-2">Komisyon Oranı</h2>
                            <div className="text-4xl font-bold text-[#43426e]">
                              %{commissionRate || "0"}
                            </div>
                          </div>
                        </div>
                        <div className="mt-4 p-3 bg-gray-50 rounded-xl">
                          <div className="flex flex-col items-center">
                            <DollarOutlined style={{ fontSize: '48px', color: '#43426e' }} />
                            <div className="text-lg font-medium text-[#43426e] mt-2">
                              KDV Hariç Fiyat
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Right Panel - Komisyon Sonuçları */}
                    <div className="w-3/5 pl-8 flex flex-col justify-center">
                      <div className="flex justify-center mb-5">
                        <h2 className="text-2xl font-bold text-[#43426e]">Hesaplamalar</h2>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="bg-gray-50 p-6 rounded-xl">
                          <div className="text-xl font-medium text-[#43426e] text-center">
                            Hesaplamalar daha yapılmadı
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
                
                {/* Fiyat Hesaplama Sonuçları */}
                {activeSection === "price" && priceCalculationResult && (
                  <>
                    {/* Left Panel - Fiyat görseli */}
                    <div className="w-2/5 pr-8 border-r border-gray-100 flex items-center justify-center">
                      <div className="text-center w-full">
                        <div className="bg-gradient-to-r from-[#43426e] to-[#e7bd99] p-[2px] rounded-xl">
                          <div className="bg-white p-5 rounded-xl">
                            <h2 className="text-xl text-gray-600 mb-2">Satış Fiyatı</h2>
                            <div className="text-4xl font-bold text-[#43426e]">
                              ₺{parseFloat(priceCalculationResult.priceWithVAT).toFixed(2)}
                            </div>
                          </div>
                        </div>
                        <div className="mt-4 p-3 bg-gray-50 rounded-xl">
                          <div className="flex flex-col items-center">
                            <DollarOutlined style={{ fontSize: '48px', color: '#43426e' }} />
                            <div className="text-lg font-medium text-[#43426e] mt-2">
                              KDV Hariç Fiyat
                            </div>
                            <div className="text-2xl font-normal text-[#43426e] mt-1">
                              ₺{priceCalculationResult.priceWithoutVAT}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Right Panel - Fiyat Hesaplama Sonuçları */}
                    <div className="w-3/5 pl-8 flex flex-col justify-center">
                      <div className="flex justify-center mb-5">
                        <h2 className="text-2xl font-bold text-[#43426e]">Hesaplamalar</h2>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="bg-gray-50 p-6 rounded-xl">
                          <div className="text-xl font-medium text-[#43426e] text-center">
                            Hesaplamalar daha yapılmadı
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
                
                {/* Navigation Button for Second Container */}
                <div className="absolute left-4 bottom-4 z-20">
                  <button
                    onClick={toggleContainer}
                    className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-[#43426e] to-[#635e9c] text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:transform hover:scale-110 hover:rotate-12 relative"
                  >
                    {activeContainer === "second" ? (
                      <UpOutlined style={{ fontSize: '18px' }} />
                    ) : (
                      <DownOutlined style={{ fontSize: '18px' }} />
                    )}
                    <div className="absolute inset-0 rounded-full bg-white opacity-0 hover:opacity-20 transition-opacity duration-300"></div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Auth Modals */}
      <LoginForm
        onLogin={handleLogin}
        onShowRegister={handleShowRegister}
        initialValues={registrationData}
        visible={showLoginModal}
        onCancel={() => setShowLoginModal(false)}
      />
      
      <RegisterForm
        onRegister={handleRegister}
        onBackToLogin={handleBackToLogin}
        visible={showRegisterModal}
        onCancel={() => setShowRegisterModal(false)}
      />
    </div>
  );
};

export default App;
