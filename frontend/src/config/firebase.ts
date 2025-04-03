import { initializeApp } from 'firebase/app';
import { getAnalytics } from 'firebase/analytics';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyAaKoBYSTJDdtJDEDGRKUXiwN0i_CWRkfY",
  authDomain: "pomo-e-commerce.firebaseapp.com",
  projectId: "pomo-e-commerce",
  storageBucket: "pomo-e-commerce.firebasestorage.app",
  messagingSenderId: "237574052513",
  appId: "1:237574052513:web:37d6c06fdd69466313eee0",
  measurementId: "G-5BBFQQNDWZ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider(); 