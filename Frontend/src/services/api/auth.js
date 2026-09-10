import { request } from './http.js';

/**
 * Check whether the given email is a configured admin. Returns false (never
 * throws) if the check can't be completed — "unknown" is treated as "not admin".
 */
export async function checkIsAdmin(email) {
  if (!email) return false;
  try {
    const data = await request(`/auth/is-admin?email=${encodeURIComponent(email)}`);
    return !!data.is_admin;
  } catch {
    return false;
  }
}

/**
 * Register a new account (username, email, password) — stored in MongoDB.
 */
export async function registerUser(username, email, password) {
  return request('/auth/register', { method: 'POST', write: true, body: { username, email, password } });
}

/**
 * Log in with an email or username, plus password.
 */
export async function loginUser(identifier, password) {
  return request('/auth/login', { method: 'POST', write: true, body: { identifier, password } });
}

/**
 * Fetch the Google OAuth Client ID the backend is configured with (public, not a
 * secret). Returns '' if it isn't configured or the call fails.
 */
export async function getGoogleClientId() {
  try {
    const data = await request('/auth/google-client-id');
    return data.client_id || '';
  } catch {
    return '';
  }
}

/**
 * Log in (or auto-register) using a verified Google Identity Services ID token.
 */
export async function googleLogin(credential) {
  return request('/auth/google', { method: 'POST', write: true, body: { credential } });
}

/**
 * Fetch a user's public profile (username, email, avatar).
 */
export async function getProfile(email) {
  return request(`/auth/profile?email=${encodeURIComponent(email)}`);
}

/**
 * Edit username/email/password. currentPassword must be correct to authorize the change.
 */
export async function updateProfile({ currentEmail, currentPassword, newUsername, newEmail, newPassword }) {
  return request('/auth/profile', {
    method: 'PUT',
    write: true,
    body: {
      current_email: currentEmail,
      current_password: currentPassword,
      new_username: newUsername || null,
      new_email: newEmail || null,
      new_password: newPassword || null,
    },
  });
}

/**
 * Upload/replace the current user's avatar image.
 */
export async function uploadAvatar(email, file) {
  const formData = new FormData();
  formData.append('email', email);
  formData.append('avatar', file);
  return request('/auth/avatar', { method: 'POST', write: true, body: formData });
}

/**
 * Permanently delete an account (requires password confirmation).
 */
export async function deleteAccount(email, password) {
  return request('/auth/account', { method: 'DELETE', write: true, body: { email, password } });
}
