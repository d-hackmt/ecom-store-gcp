import { state, login } from '../../services/state.js';
import { loginUser, registerUser, checkIsAdmin } from '../../services/api_v2.js';
import { refreshCartCount } from '../../services/cartCount.js';
import { renderGoogleSignIn, setupGoogleSignIn } from './googleSignIn.js';

/**
 * Email/username + password login & registration forms, shown when logged out.
 * `state.ui.authMode` ('login' | 'register') is reset by the router on navigation.
 */
export function renderAuthForms() {
  const isLogin = state.ui.authMode === 'login';
  return `
    <div class="container page page-sm">
      <h1 class="page-title">Your Profile</h1>
      <div class="card">
        ${isLogin ? `
          <h2 class="card-heading">Login</h2>
          ${renderGoogleSignIn()}
          <div class="divider">or</div>
          <input placeholder="Email or username" class="form-input field" id="loginIdentifier" />
          <input type="password" placeholder="Password" class="form-input field" id="loginPassword" />
          <button id="loginBtn" class="btn btn-primary full-width">Login</button>
          <p style="text-align: center; margin-top: 1rem; font-size: 0.9rem;">
            No account? <a href="#" id="showRegister" class="text-link">Register</a>
          </p>
        ` : `
          <h2 class="card-heading">Register</h2>
          <input placeholder="Username" class="form-input field" id="regUsername" />
          <input type="email" placeholder="Email" class="form-input field" id="regEmail" />
          <input type="password" placeholder="Password (min 6 characters)" class="form-input field" id="regPassword" />
          <button id="registerBtn" class="btn btn-success full-width">Create Account</button>
          <p style="text-align: center; margin-top: 1rem; font-size: 0.9rem;">
            Already have an account? <a href="#" id="showLogin" class="text-link">Login</a>
          </p>
        `}
      </div>
    </div>
  `;
}

export function setupAuthFormsEvents(rerender) {
  if (state.ui.authMode === 'login') {
    setupGoogleSignIn(rerender);
  }

  document.getElementById('showRegister')?.addEventListener('click', (e) => {
    e.preventDefault();
    state.ui.authMode = 'register';
    rerender();
  });

  document.getElementById('showLogin')?.addEventListener('click', (e) => {
    e.preventDefault();
    state.ui.authMode = 'login';
    rerender();
  });

  document.getElementById('loginBtn')?.addEventListener('click', async () => {
    const identifier = document.getElementById('loginIdentifier').value.trim();
    const password = document.getElementById('loginPassword').value;
    if (!identifier || !password) {
      alert('Please enter your email/username and password.');
      return;
    }
    const btn = document.getElementById('loginBtn');
    btn.textContent = 'Logging in...';
    btn.disabled = true;
    try {
      const result = await loginUser(identifier, password);
      login(result.email, result.username);
      state.isAdmin = await checkIsAdmin(state.sessionId);
      await refreshCartCount();
      rerender();
    } catch (e) {
      alert(e.message);
      btn.textContent = 'Login';
      btn.disabled = false;
    }
  });

  document.getElementById('registerBtn')?.addEventListener('click', async () => {
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    if (!username || !email || !password) {
      alert('Please fill in username, email, and password.');
      return;
    }
    const btn = document.getElementById('registerBtn');
    btn.textContent = 'Creating account...';
    btn.disabled = true;
    try {
      const result = await registerUser(username, email, password);
      login(result.email, result.username);
      state.isAdmin = await checkIsAdmin(state.sessionId);
      await refreshCartCount();
      alert('Account created! You are now logged in.');
      rerender();
    } catch (e) {
      alert(e.message);
      btn.textContent = 'Create Account';
      btn.disabled = false;
    }
  });
}
