import { state } from '../services/state.js';
import { fetchProducts } from '../services/api_v2.js';
import { renderQuickActions, setupQuickActionsEvents } from './admin/quickActions.js';
import { renderBulkImport, setupBulkImportEvents } from './admin/bulkImport.js';
import { renderProductForm, setupProductFormEvents } from './admin/productForm.js';
import { renderProductList, setupProductListEvents } from './admin/productList.js';

/**
 * Render the Admin dashboard page to manage products.
 */
export async function renderAdmin() {
  try {
    state.productList = await fetchProducts();
  } catch (err) {
    console.error('Failed to load products:', err);
    state.productList = [];
  }

  document.getElementById('app').innerHTML = `
    <div class="admin-page">
      ${renderQuickActions()}
      ${renderBulkImport()}
      ${renderProductForm()}
      ${renderProductList()}
    </div>
  `;

  setupQuickActionsEvents(renderAdmin);
  setupBulkImportEvents(renderAdmin);
  setupProductFormEvents(renderAdmin);
  setupProductListEvents(renderAdmin);
}
