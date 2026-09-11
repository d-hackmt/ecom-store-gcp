import { state } from '../services/state.js';
import { getCart, placeOrder, clearCart, fetchProducts } from '../services/api_v2.js';
import { setCartCount } from '../services/cartCount.js';
import { escapeHtml } from '../utils/escapeHtml.js';
import { PLACEHOLDER_IMAGE } from '../utils/placeholder.js';

export async function renderCart() {
  document.getElementById('app').innerHTML = `
    <div class="container page page-lg">
      <h1 class="page-title">Your Cart</h1>
      <div id="cartContent"><p>Loading cart...</p></div>
    </div>
  `;
  const contentDiv = document.getElementById('cartContent');

  let cartItems;
  try {
    // The cart only stores product names + quantities; join against the catalog
    // for prices and images.
    const [rawCartItems, productsDB] = await Promise.all([
      getCart(state.sessionId),
      fetchProducts(),
    ]);
    cartItems = rawCartItems.map(item => {
      const match = productsDB.find(p => p.name === item.product_name) || {};
      return {
        ...item,
        price: match.price || 0,
        image: match.image || PLACEHOLDER_IMAGE,
      };
    });
  } catch (err) {
    console.error('Failed to load cart:', err);
    contentDiv.innerHTML = `<div class="empty-state"><p>Couldn't load your cart. Please try again.</p></div>`;
    return;
  }

  if (!cartItems.length) {
    contentDiv.innerHTML = `
      <div class="cart-empty">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🛒</div>
        <h2 style="font-size: 1.5rem; color: #4b5563; margin-bottom: 1rem;">Your cart is empty!</h2>
        <a href="#/" class="btn btn-primary">Continue Shopping</a>
      </div>
    `;
    setCartCount(0);
    return;
  }

  const total = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  setCartCount(cartItems.reduce((sum, item) => sum + (item.quantity || 0), 0));

  contentDiv.innerHTML = `
    <div class="card">
      <div class="list-stack">
        ${cartItems.map(renderCartItem).join('')}
      </div>
      <div class="cart-total-row">
        <h2 style="font-size: 1.5rem; font-weight: bold;">Total Due:</h2>
        <span style="font-size: 1.5rem; font-weight: bold; color: #111827;">₹${total}</span>
      </div>
      <div class="cart-actions">
        <a href="#/" class="btn btn-outline" style="flex: 1; text-align: center;">Keep Shopping</a>
        <button id="clearCartBtn" class="btn btn-outline btn-danger-outline" style="flex: 1;">Clear Cart 🗑️</button>
        <button id="buyAllBtn" class="btn btn-primary" style="flex: 2;">Buy All Now 🚀</button>
      </div>
    </div>
  `;

  wireClearCart();
  wireBuyAll(cartItems);
}

function renderCartItem(item) {
  return `
    <div class="cart-item">
      <img class="cart-item-img" src="${escapeHtml(item.image)}" alt="${escapeHtml(item.product_name)}" loading="lazy" />
      <div class="cart-item-info">
        <h3 style="font-weight: bold; font-size: 1.1rem; color: #111827;">${escapeHtml(item.product_name)}</h3>
        <p class="muted">Qty: ${escapeHtml(item.quantity)}</p>
      </div>
      <div class="price-lg">₹${escapeHtml(item.price)}</div>
    </div>`;
}

function wireClearCart() {
  document.getElementById('clearCartBtn')?.addEventListener('click', async (e) => {
    if (!confirm('Are you sure you want to clear your cart?')) return;
    const btn = e.target.closest('button');
    btn.disabled = true;
    btn.textContent = 'Clearing... ⏳';
    try {
      await clearCart(state.sessionId);
      setCartCount(0);
      renderCart();
    } catch (err) {
      alert(`Failed to clear cart: ${err.message}`);
      btn.disabled = false;
      btn.textContent = 'Clear Cart 🗑️';
    }
  });
}

function wireBuyAll(cartItems) {
  document.getElementById('buyAllBtn')?.addEventListener('click', async (e) => {
    const btn = e.target.closest('button');
    btn.disabled = true;
    btn.textContent = 'Processing... ⏳';
    try {
      await Promise.all(
        cartItems.map(item => placeOrder(state.sessionId, item.product_name, item.quantity, item.price)),
      );
      await clearCart(state.sessionId);
      setCartCount(0);
      btn.textContent = 'Order Successful! 🎉';
      btn.classList.add('btn-success');
      setTimeout(() => { window.location.hash = '#/'; }, 2000);
    } catch (err) {
      alert(`Failed to place the order: ${err.message}`);
      btn.disabled = false;
      btn.textContent = 'Buy All Now 🚀';
    }
  });
}
