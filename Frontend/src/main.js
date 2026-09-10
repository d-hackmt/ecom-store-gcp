import { router } from './router.js';
import { state } from './services/state.js';
import { checkIsAdmin, initIngestionApiBase } from './services/api_v2.js';
import { refreshCartCount } from './services/cartCount.js';

window.addEventListener('hashchange', router);

window.addEventListener('DOMContentLoaded', async () => {
  // Resolve the ingestion service URL, admin status and cart count before the
  // first render. If any of it fails, still render the page — a slow or
  // unreachable backend must not leave the user staring at a blank screen.
  try {
    await initIngestionApiBase();
    const [isAdmin] = await Promise.all([
      checkIsAdmin(state.sessionId),
      refreshCartCount(),
    ]);
    state.isAdmin = isAdmin;
  } catch (err) {
    console.error('Startup check failed:', err);
  }

  router();
});
