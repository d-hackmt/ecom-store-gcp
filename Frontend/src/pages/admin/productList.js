import { state } from '../../services/state.js';
import { deleteProduct } from '../../services/api_v2.js';
import { escapeHtml } from '../../utils/escapeHtml.js';
import { editProduct } from './productForm.js';

/**
 * The grid of existing products with Edit/Delete actions.
 */
export function renderProductList() {
  return `
    <h2 class="product-list-title">Product List</h2>
    <div class="product-list-grid">
      ${state.productList.map(p => `
        <div class="product-list-item">
          <img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.name)}" />
          <h3>${escapeHtml(p.name)}</h3>
          <p>${escapeHtml(p.description)}</p>
          <p class="price">₹${escapeHtml(p.price)}</p>
          <p class="meta">Category: ${escapeHtml(p.category)}</p>
          <p class="meta">Sizes: ${escapeHtml(p.size?.join(', ') || 'N/A')}</p>
          <div class="product-actions">
            <button class="edit-btn" data-id="${escapeHtml(p.id)}">Edit</button>
            <button class="delete-btn" data-id="${escapeHtml(p.id)}">Delete</button>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

export function setupProductListEvents(rerender) {
  document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const product = state.productList.find(p => String(p.id) === String(btn.dataset.id));
      if (product) editProduct(product, rerender);
    });
  });

  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => handleDeleteProduct(btn.dataset.id, rerender));
  });
}

async function handleDeleteProduct(id, rerender) {
  if (!confirm('Delete this product? This cannot be undone.')) return;
  try {
    await deleteProduct(id);
  } catch (err) {
    alert(`Failed to delete product: ${err.message}`);
    return;
  }
  state.productList = state.productList.filter(p => String(p.id) !== String(id));
  rerender();
}
