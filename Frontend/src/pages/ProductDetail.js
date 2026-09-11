import { state } from '../services/state.js';
import { fetchProduct, placeOrder } from '../services/api_v2.js';
import { handleAddToCartClick } from '../services/cartActions.js';
import { navigate } from '../services/nav.js';
import { escapeHtml } from '../utils/escapeHtml.js';
import { PLACEHOLDER_IMAGE } from '../utils/placeholder.js';

export async function renderProductDetail(id) {
  const app = document.getElementById('app');
  app.innerHTML = `<div class="loading">Loading…</div>`;

  let product;
  try {
    product = await fetchProduct(id);
  } catch (err) {
    console.error('Failed to load product:', err);
    app.innerHTML = `
      <div class="product-detail">
        <button class="back-btn" id="backBtn">← Back to Products</button>
        <div class="empty-state">
          <p>Sorry, we couldn't find that product.</p>
          <a href="#/" class="btn btn-primary">Browse all products</a>
        </div>
      </div>`;
    document.getElementById('backBtn')?.addEventListener('click', () => navigate('#/'));
    return;
  }

  const sizes = Array.isArray(product.size) ? product.size : [];
  const colors = Array.isArray(product.color) ? product.color : [];

  app.innerHTML = `
    <div class="product-detail">
      <button class="back-btn" id="backBtn">← Back to Products</button>
      <div class="product-detail-grid">
        <div class="product-detail-image">
          <img src="${escapeHtml(product.image || PLACEHOLDER_IMAGE)}" alt="${escapeHtml(product.name)}" loading="lazy" />
        </div>
        <div class="product-detail-info">
          <span class="product-detail-category">${escapeHtml(product.category)}</span>
          <h1>${escapeHtml(product.name)}</h1>
          <p class="product-detail-price">₹${escapeHtml(product.price)}</p>
          <p class="product-detail-desc">${escapeHtml(product.description)}</p>
          ${sizes.length ? `
            <div class="option-group">
              <h3 class="option-label">Sizes:</h3>
              <div class="option-values">
                ${sizes.map(s => `<span class="option-value">${escapeHtml(s)}</span>`).join('')}
              </div>
            </div>` : ''}
          ${colors.length ? `
            <div class="option-group">
              <h3 class="option-label">Colors:</h3>
              <div class="option-values">
                ${colors.map(c => `<span class="option-value">${escapeHtml(c)}</span>`).join('')}
              </div>
            </div>` : ''}
          <div class="detail-actions">
            <button class="detail-btn detail-btn-primary" id="btnAddToCart">Add to Cart</button>
            <button class="detail-btn detail-btn-secondary" id="btnBuyNow">Buy Now</button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.getElementById('backBtn')?.addEventListener('click', () => window.history.back());

  document.getElementById('btnAddToCart')?.addEventListener('click', (e) => {
    handleAddToCartClick(e.target, product.name, { onSuccess: () => renderProductDetail(id), delay: 1500 });
  });

  document.getElementById('btnBuyNow')?.addEventListener('click', async (e) => {
    e.target.disabled = true;
    e.target.textContent = 'Processing...';
    try {
      await placeOrder(state.sessionId, product.name, 1, product.price);
      e.target.textContent = 'Order Placed! 🚀';
      setTimeout(() => navigate('#/'), 2000);
    } catch (err) {
      console.error(err);
      alert(`Failed to place order: ${err.message}`);
      e.target.disabled = false;
      e.target.textContent = 'Buy Now';
    }
  });
}
