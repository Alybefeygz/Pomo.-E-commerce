import { signInWithPopup, GoogleAuthProvider, User } from 'firebase/auth';
import { auth, googleProvider } from '../config/firebase';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

export const signInWithGoogle = async () => {
  try {
    console.log('Starting Google sign in process...');
    
    // Sign in with Google using Firebase
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    
    console.log('Google sign in successful, user data:', {
      email: user.email,
      displayName: user.displayName,
      photoURL: user.photoURL,
      uid: user.uid
    });

    // Send user data to your backend
    const requestData = {
      email: user.email,
      username: user.displayName || user.email?.split('@')[0],
      photo_url: user.photoURL,
      google_id: user.uid
    };
    
    console.log('Sending data to backend:', requestData);
    
    const response = await axios.post(`${API_URL}/rest-auth/google/`, requestData);
    
    console.log('Backend response:', response.data);

    // Store the token and user data
    if (response.data.key) {
      localStorage.setItem('authToken', response.data.key);
      localStorage.setItem('username', user.displayName || user.email?.split('@')[0] || '');
      localStorage.setItem('email', user.email || '');
      
      // Backend'den gelen kullanıcı ID'sini kaydet
      if (response.data.user && response.data.user.id) {
        localStorage.setItem('userID', response.data.user.id.toString());
      }
    }

    return response.data;
  } catch (error: any) {
    console.error('Google sign in error:', error);
    console.error('Error response:', error.response?.data);
    throw error;
  }
}; 