// Firebase Authentication Handler
import { auth, provider, signInWithPopup, signOut, onAuthStateChanged } from './firebase-config.js';
import { trackSignIn, trackSignUp } from './analytics.js';

// Global user state
let currentUser = null;

// Initialize authentication state listener
export function initAuth() {
    onAuthStateChanged(auth, (user) => {
        if (user) {
            currentUser = user;
            console.log("User signed in:", user.email);
            updateUIForSignedInUser(user);
        } else {
            currentUser = null;
            console.log("User signed out");
            updateUIForSignedOutUser();
        }
    });
}

// Sign in with Google
export async function signInWithGoogle() {
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        
        console.log("Successfully signed in:", user.email);
        
        // Check if this is a new user (sign-up) or existing user (sign-in)
        const isNewUser = result._tokenResponse?.isNewUser || false;
        
        // Track sign-in or sign-up
        if (isNewUser) {
            trackSignUp('google');
        } else {
            trackSignIn('google');
        }
        
        // Store user info in localStorage (compatible with existing system)
        const googleUser = {
            sub: user.uid,
            email: user.email,
            name: user.displayName,
            picture: user.photoURL
        };
        
        localStorage.setItem('userId', user.email);
        localStorage.setItem('googleUser', JSON.stringify(googleUser));
        
        // Check if user profile exists in backend
        await checkAndCreateProfile(user);
        
        // Trigger the existing checkAuthStatus function if it exists
        if (typeof window.checkAuthStatus === 'function') {
            window.checkAuthStatus();
        }
        
        // Return user info
        return {
            success: true,
            user: {
                uid: user.uid,
                email: user.email,
                displayName: user.displayName,
                photoURL: user.photoURL
            }
        };
    } catch (error) {
        console.error("Sign-in error:", error);
        
        // Ignore cancelled popup errors (user closed popup)
        if (error.code === 'auth/cancelled-popup-request' || 
            error.code === 'auth/popup-closed-by-user') {
            return { success: false, silent: true };
        }
        
        let errorMessage = "Authentication failed. Please try again.";
        
        if (error.code === 'auth/popup-blocked') {
            errorMessage = "Popup was blocked by browser. Please allow popups for this site.";
        } else if (error.code === 'auth/unauthorized-domain') {
            errorMessage = "This domain is not authorized. Please add 'localhost' to Firebase Console > Authentication > Settings > Authorized domains.";
        }
        
        return {
            success: false,
            error: errorMessage
        };
    }
}

// Check if user profile exists, create if not
async function checkAndCreateProfile(user) {
    try {
        const API_BASE = window.location.hostname === 'localhost' 
            ? 'http://localhost:5000' 
            : window.location.origin + '/api';
        
        // Check if profile exists
        const checkResponse = await fetch(`${API_BASE}/profile/${user.email}`);
        
        if (checkResponse.status === 404) {
            // Profile doesn't exist, we'll let user create it on profile page
            console.log('Profile not found, user needs to complete profile');
        } else if (checkResponse.ok) {
            const data = await checkResponse.json();
            if (data.success) {
                console.log('Profile exists:', data.profile);
            }
        }
    } catch (error) {
        console.error('Error checking profile:', error);
        // Continue anyway - user can create profile later
    }
}

// Sign out
export async function signOutUser() {
    try {
        await signOut(auth);
        console.log("User signed out successfully");
        return { success: true };
    } catch (error) {
        console.error("Sign-out error:", error);
        return { success: false, error: error.message };
    }
}

// Get current user
export function getCurrentUser() {
    return currentUser;
}

// Check if user is signed in
export function isSignedIn() {
    return currentUser !== null;
}

// Update UI for signed-in user
function updateUIForSignedInUser(user) {
    // Update Google Sign-In button area
    const googleSignInContainer = document.querySelector('.google-signin-container');
    if (googleSignInContainer) {
        googleSignInContainer.innerHTML = `
            <div class="alert alert-success d-flex align-items-center" role="alert">
                <img src="${user.photoURL || 'https://via.placeholder.com/40'}" 
                     alt="Profile" 
                     class="rounded-circle me-3" 
                     style="width: 40px; height: 40px;">
                <div class="flex-grow-1">
                    <strong>${user.displayName || user.email}</strong>
                    <br>
                    <small class="text-muted">${user.email}</small>
                </div>
                <button class="btn btn-sm btn-outline-danger" onclick="handleSignOut()">
                    Sign Out
                </button>
            </div>
        `;
    }
    
    // Pre-fill form if exists
    const fullNameInput = document.getElementById('fullName');
    if (fullNameInput && !fullNameInput.value) {
        fullNameInput.value = user.displayName || '';
        
        // Show editable badge and help text
        const editableBadge = document.getElementById('name-editable-badge');
        const helpText = document.getElementById('name-help-text');
        if (editableBadge) editableBadge.style.display = 'inline-block';
        if (helpText) helpText.style.display = 'block';
        
        // Add a subtle highlight animation
        fullNameInput.classList.add('border-info');
        setTimeout(() => {
            fullNameInput.classList.remove('border-info');
        }, 3000);
    }
    
    // Show authenticated badge
    const authBadge = document.getElementById('auth-badge');
    if (authBadge) {
        authBadge.style.display = 'inline-block';
    }
}

// Update UI for signed-out user
function updateUIForSignedOutUser() {
    // Reset Google Sign-In button area
    const googleSignInContainer = document.querySelector('.google-signin-container');
    if (googleSignInContainer) {
        googleSignInContainer.innerHTML = `
            <button class="btn btn-outline-primary btn-lg w-100" onclick="handleGoogleSignIn()">
                <i class="bi bi-google me-2"></i>
                Sign in with Google
            </button>
        `;
    }
    
    // Hide authenticated badge
    const authBadge = document.getElementById('auth-badge');
    if (authBadge) {
        authBadge.style.display = 'none';
    }
}

// Make functions available globally
window.handleGoogleSignIn = async function() {
    const result = await signInWithGoogle();
    if (result.success) {
        // Success - UI already updated
        return;
    }
    
    // Only show error if not silent (not cancelled by user)
    if (!result.silent && result.error) {
        alert(result.error);
    }
};

window.handleSignOut = async function() {
    const result = await signOutUser();
    if (result.success) {
        alert("Signed out successfully!");
    }
};

// Initialize on load
initAuth();
