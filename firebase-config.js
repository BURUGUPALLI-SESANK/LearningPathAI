// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-analytics.js";
import { 
    getAuth, 
    signInWithPopup, 
    GoogleAuthProvider,
    signOut,
    onAuthStateChanged 
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Fetch Firebase configuration from backend (secure - from .env)
let app, analytics, auth, provider;

async function initializeFirebase() {
    try {
        const response = await fetch('/firebase-config');
        if (!response.ok) {
            throw new Error('Failed to fetch Firebase configuration');
        }
        
        const firebaseConfig = await response.json();
        
        // Initialize Firebase
        app = initializeApp(firebaseConfig);
        analytics = getAnalytics(app);
        auth = getAuth(app);
        provider = new GoogleAuthProvider();
        
        console.log('✅ Firebase initialized successfully');
        return true;
    } catch (error) {
        console.error('❌ Firebase initialization failed:', error);
        alert('Firebase configuration error. Please check your .env file and restart the server.');
        return false;
    }
}

// Initialize Firebase on module load
await initializeFirebase();

// Export for use in other files
export { auth, provider, signInWithPopup, signOut, onAuthStateChanged, analytics };
