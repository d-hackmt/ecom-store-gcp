// Global application state

const GUEST_KEY = 'luxe_session';
const LOGIN_KEY = 'luxe_logged_in_email';
const USERNAME_KEY = 'luxe_username';

// Generate a random guest session email if one doesn't exist
const getGuestId = () => {
  let id = localStorage.getItem(GUEST_KEY);
  if (!id) {
    id = `guest_${Math.random().toString(36).substring(2, 9)}@luxe.com`;
    localStorage.setItem(GUEST_KEY, id);
  }
  return id;
};

const getLoggedInEmail = () => localStorage.getItem(LOGIN_KEY);

export const state = {
  sessionId: getLoggedInEmail() || getGuestId(),
  isLoggedIn: !!getLoggedInEmail(),
  username: getLoggedInEmail() ? (localStorage.getItem(USERNAME_KEY) || '') : '',
  isAdmin: false, // refreshed asynchronously via checkIsAdmin() — see main.js / Profile.js
  cartItemCount: 0,
  currentCategory: '',
  priceFilter: { min: null, max: null },  // price range filter
  products: [],
  productList: [],

  // Per-page UI toggles, cleared by resetTransientUi() on navigation.
  ui: {
    profileEditOpen: false,
    profileDeleteOpen: false,
    authMode: 'login',       // 'login' | 'register'
  },

  // State for admin
  isEditing: false,
  editId: null,
  adminForm: {
    name: '',
    description: '',
    price: 0,
    category: 'men',
    image: '',
    size: [],
    color: []
  },
  imageFile: null
};

/**
 * Reset the short-lived UI toggles. Called by the router whenever the route's
 * page changes, so opening the edit form on Profile and navigating away doesn't
 * leave it open on the next visit.
 */
export function resetTransientUi() {
  state.ui = {
    profileEditOpen: false,
    profileDeleteOpen: false,
    authMode: 'login',
  };
}


/**
 * Log in with a verified email + username (post password check) — replaces the guest session.
 */
export function login(email, username) {
  localStorage.setItem(LOGIN_KEY, email);
  localStorage.setItem(USERNAME_KEY, username);
  state.sessionId = email;
  state.username = username;
  state.isLoggedIn = true;
}

/**
 * Log out and fall back to an anonymous guest session.
 */
export function logout() {
  localStorage.removeItem(LOGIN_KEY);
  localStorage.removeItem(USERNAME_KEY);
  state.sessionId = getGuestId();
  state.username = '';
  state.isLoggedIn = false;
}

export function resetAdminForm() {
  state.isEditing = false;
  state.editId = null;
  state.imageFile = null;
  state.adminForm = {
    name: '',
    description: '',
    price: 0,
    category: 'men',
    image: '',
    size: [],
    color: []
  };
}
