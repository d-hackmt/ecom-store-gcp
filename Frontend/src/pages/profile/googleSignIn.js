import { state, login } from '../../services/state.js';
import { getGoogleClientId, googleLogin, checkIsAdmin } from '../../services/api_v2.js';
import { refreshCartCount } from '../../services/cartCount.js';

let scriptLoadPromise = null;

function loadGoogleScript() {
  if (window.google?.accounts?.id) return Promise.resolve();
  if (!scriptLoadPromise) {
    scriptLoadPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.onload = resolve;
      script.onerror = () => reject(new Error('Failed to load Google Sign-In'));
      document.head.appendChild(script);
    });
  }
  return scriptLoadPromise;
}

/**
 * Container Google's script will render its own button into.
 */
export function renderGoogleSignIn() {
  return `<div id="googleSignInDiv" class="google-signin"></div>`;
}

/**
 * Fetch the configured Client ID and mount the real Google Sign-In button.
 * Silently does nothing if Google Sign-In isn't configured on the backend yet,
 * so the rest of the login form still works without it.
 */
export async function setupGoogleSignIn(rerender) {
  const container = document.getElementById('googleSignInDiv');
  if (!container) return;

  const clientId = await getGoogleClientId();
  if (!clientId || clientId.includes('REPLACE_WITH')) return;

  try {
    await loadGoogleScript();
  } catch (err) {
    console.error(err);
    return;
  }

  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: async (response) => {
      try {
        const result = await googleLogin(response.credential);
        login(result.email, result.username);
        state.isAdmin = await checkIsAdmin(state.sessionId);
        await refreshCartCount();
        rerender();
      } catch (err) {
        alert(err.message);
      }
    },
  });

  window.google.accounts.id.renderButton(container, { theme: 'outline', size: 'large', width: 300 });
}
