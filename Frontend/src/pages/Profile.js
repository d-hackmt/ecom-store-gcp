import { state, logout } from '../services/state.js';
import { getProfile, getOrderHistory, checkIsAdmin } from '../services/api_v2.js';
import { refreshCartCount } from '../services/cartCount.js';
import { renderAuthForms, setupAuthFormsEvents } from './profile/authForms.js';
import { renderProfileCard, setupProfileCardEvents } from './profile/profileCard.js';
import { renderOrderHistory } from './profile/orderHistory.js';
import { renderDangerZone, setupDangerZoneEvents } from './profile/dangerZone.js';

/**
 * The Profile page: email/username + password login & registration when logged
 * out, or the full account view (avatar, edit profile, order history, delete
 * account) when logged in. The open/closed state of the edit and delete panels
 * lives in state.ui and is reset by the router on navigation.
 */
export async function renderProfile() {
  if (!state.isLoggedIn) {
    document.getElementById('app').innerHTML = renderAuthForms();
    setupAuthFormsEvents(renderProfile);
    return;
  }

  let profile = { avatar: null };
  let orders = [];
  try {
    [profile, orders] = await Promise.all([
      getProfile(state.sessionId),
      getOrderHistory(state.sessionId),
    ]);
  } catch (err) {
    console.error('Failed to load profile data:', err);
  }

  document.getElementById('app').innerHTML = `
    <div class="container page page-md">
      <h1 class="page-title">Your Profile</h1>
      ${renderProfileCard(profile, state.ui.profileEditOpen)}
      ${renderOrderHistory(orders)}
      ${renderDangerZone(state.ui.profileDeleteOpen)}
      <button id="logoutBtn" class="btn btn-outline full-width">Logout</button>
    </div>
  `;

  setupProfileEvents();
}

function setupProfileEvents() {
  document.getElementById('toggleEditForm')?.addEventListener('click', () => {
    state.ui.profileEditOpen = !state.ui.profileEditOpen;
    renderProfile();
  });
  setupProfileCardEvents(renderProfile, () => {
    state.ui.profileEditOpen = false;
    renderProfile();
  });

  document.getElementById('deleteAccountBtn')?.addEventListener('click', () => {
    state.ui.profileDeleteOpen = true;
    renderProfile();
  });
  document.getElementById('cancelDeleteBtn')?.addEventListener('click', () => {
    state.ui.profileDeleteOpen = false;
    renderProfile();
  });
  setupDangerZoneEvents(() => {
    state.ui.profileDeleteOpen = false;
  });

  document.getElementById('logoutBtn')?.addEventListener('click', async () => {
    logout();
    state.isAdmin = await checkIsAdmin(state.sessionId);
    await refreshCartCount();
    renderProfile();
  });
}
