import { state } from '../services/state.js';
import { navigate } from '../services/nav.js';
import { escapeHtml } from '../utils/escapeHtml.js';

const CATEGORIES = [
  { label: 'All', value: '' },
  { label: 'Men', value: 'men' },
  { label: 'Women', value: 'women' },
  { label: 'Kids', value: 'kids' },
];

const ICON_USER =
  '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>';
const ICON_CART =
  '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>';
const ICON_MENU =
  '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>';

/** Build the header markup (rendered into #site-header by mountHeader). */
export function renderHeader() {
  const { cartItemCount, isAdmin, isLoggedIn, username, currentCategory } = state;
  return `
  <header class="header">
    <div class="container header-inner">
      <div class="header-left">
        <button class="menu-btn" id="menuToggle" aria-label="Toggle menu">${ICON_MENU}</button>
        <button class="header-logo" data-nav="#/">LUXE</button>
        <nav class="nav" id="mainNav">
          ${CATEGORIES.map(c => `
            <button class="nav-link ${currentCategory === c.value ? 'active' : ''}" data-cat="${c.value}">${c.label}</button>
          `).join('')}
        </nav>
      </div>
      <div class="header-right">
        ${isAdmin ? `<button class="btn btn-primary header-admin-btn" data-nav="#/admin">Add Products</button>` : ''}
        <button class="icon-btn relative" title="${isLoggedIn ? escapeHtml(username) : 'Login'}" data-nav="#/profile">
          ${ICON_USER}
          ${isLoggedIn ? `<span class="cart-badge account-dot">•</span>` : ''}
        </button>
        <button class="icon-btn relative" data-nav="#/cart" aria-label="Cart">
          ${ICON_CART}
          ${cartItemCount > 0 ? `<span class="cart-badge">${cartItemCount}</span>` : ''}
        </button>
      </div>
    </div>
  </header>`;
}

/** Render the header into #site-header and wire its events. */
export function mountHeader() {
  const host = document.getElementById('site-header');
  if (!host) return;
  host.innerHTML = renderHeader();

  host.querySelectorAll('[data-nav]').forEach(el => {
    el.addEventListener('click', () => navigate(el.dataset.nav));
  });

  host.querySelectorAll('.nav-link[data-cat]').forEach(el => {
    el.addEventListener('click', () => {
      navigate(el.dataset.cat ? `#/?cat=${el.dataset.cat}` : '#/');
      host.querySelector('.header')?.classList.remove('nav-open');
    });
  });

  host.querySelector('#menuToggle')?.addEventListener('click', () => {
    host.querySelector('.header')?.classList.toggle('nav-open');
  });
}
