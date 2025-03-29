import React from 'react';
import { Input, Select, Button, Avatar } from 'antd';
import {
  MailOutlined,
  BoxPlotOutlined,
  DollarOutlined,
  CalculatorOutlined,
  UserOutlined,
  DownOutlined,
  UpOutlined,
  LogoutOutlined,
  LoginOutlined,
} from '@ant-design/icons';

interface MainContentProps {
  activeContainer: string;
  activeSection: string;
  email: string;
  isLoggedIn: boolean;
  username: string;
  handleEmailChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleLogout: () => void;
  handleCalculationsClick: () => void;
  toggleContainer: () => void;
  switchSection: (section: string) => void;
  // Add other necessary props
}

const MainContent: React.FC<MainContentProps> = ({
  activeContainer,
  activeSection,
  email,
  isLoggedIn,
  username,
  handleEmailChange,
  handleLogout,
  handleCalculationsClick,
  toggleContainer,
  switchSection,
  // Add other props
}) => {
  // Define empty handler functions for pointer events
  const emptyPointerHandler = () => {};

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col relative">
      {/* Top Navbar */}
      <div className="w-full bg-gray-50 pt-3 pb-2 px-4 flex justify-center">
        <div className="max-w-[1200px] w-full bg-white rounded-xl shadow-lg">
          <div className="flex items-center h-14 px-8 border-b border-gray-100">
            {/* Left: Logo with Navigation */}
            <div className="flex items-center">
              <div className="w-10 h-10 bg-[#43426e] rounded-lg flex items-center justify-center shadow-sm mr-6">
                <i className="fas fa-dog text-white text-xl"></i>
              </div>
              
              {/* Navigation */}
              <div className="flex">
                <button className="text-[#43426e] font-medium px-4 py-4 hover:bg-gray-50 transition-all relative group">
                  Hesaplamalar
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0 h-0.5 bg-[#43426e] group-hover:w-1/2 transition-all duration-300"></div>
                </button>
                <button className="text-[#43426e] font-medium px-4 py-4 hover:bg-gray-50 transition-all relative group">
                  Hizmetler
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0 h-0.5 bg-[#43426e] group-hover:w-1/2 transition-all duration-300"></div>
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
                    className="flex items-center px-3 py-1 text-[#43426e] transition-all duration-200 relative group"
                    onClick={() => console.log("Profile clicked")}
                  >
                    <UserOutlined className="mr-1" />
                    <span>Profil</span>
                    <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0 h-0.5 bg-[#e7bd99] group-hover:w-1/2 transition-all duration-300"></div>
                  </button>
                  <button 
                    className="flex items-center px-3 py-1 text-[#43426e] transition-all duration-200 relative group"
                    onClick={handleLogout}
                  >
                    <LogoutOutlined className="mr-1" />
                    <span>Çıkış</span>
                    <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0 h-0.5 bg-[#e7bd99] group-hover:w-1/2 transition-all duration-300"></div>
                  </button>
                  <div className="flex items-center px-3 py-1 ml-1">
                    <span className="text-[#43426e] font-medium mr-2">{username}</span>
                    <div className="relative">
                      <Avatar icon={<UserOutlined />} className="bg-gradient-to-r from-[#43426e] to-[#635e9c]" />
                      <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                    </div>
                  </div>
                </div>
              ) : (
                <button 
                  className="flex items-center text-[#43426e] border border-[#43426e] px-4 py-2 rounded-lg hover:bg-gray-50 transition-all shadow-sm relative group"
                  onClick={handleCalculationsClick}
                >
                  <LoginOutlined className="mr-2" />
                  <span className="font-medium">Giriş</span>
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-0 h-0.5 bg-[#e7bd99] group-hover:w-1/2 transition-all duration-300"></div>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex flex-col items-center pt-3 pb-6 px-4 overflow-hidden">
        {/* Container Wrapper */}
        <div className="max-w-[1200px] w-full relative" style={{ minHeight: '600px', height: 'auto' }}>
          {/* First Container */}
          <div 
            className={`absolute top-0 left-0 w-full transition-all duration-700 ease-in-out shadow-lg rounded-xl ${
              activeContainer === "first" 
                ? "opacity-100 transform translate-y-0 z-10" 
                : "opacity-0 transform -translate-y-20 z-0 pointer-events-none"
            }`}
          >
            {/* Add your existing container content here */}
          </div>
          
          {/* Second Container */}
          <div 
            className={`absolute top-0 left-0 w-full transition-all duration-700 ease-in-out shadow-lg rounded-xl ${
              activeContainer === "second" 
                ? "opacity-100 transform translate-y-0 z-10" 
                : "opacity-0 transform translate-y-20 z-0 pointer-events-none"
            }`}
          >
            {/* Add your existing second container content here */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainContent; 