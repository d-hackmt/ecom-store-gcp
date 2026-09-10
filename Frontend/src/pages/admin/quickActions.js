import { deleteAllProducts } from '../../services/api_v2.js';

/**
 * Header row: page title plus the "delete everything" button.
 */
export function renderQuickActions() {
  return `
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h1 class="admin-title">Add / Manage Products</h1>
      <div style="display: flex; gap: 0.5rem;">
        <button id="deleteAllBtn" class="btn btn-danger" style="font-weight: bold;">🧨 Delete All Products</button>
      </div>
    </div>
  `;
}

export function setupQuickActionsEvents(rerender) {
  document.getElementById('deleteAllBtn')?.addEventListener('click', async () => {
    if (confirm("Are you ABSOLUTELY sure you want to delete EVERY product in the store? This cannot be undone!")) {
      const btn = document.getElementById('deleteAllBtn');
      btn.textContent = "⏳ Deleting...";
      btn.disabled = true;
      try {
        await deleteAllProducts();
        alert('All products have been wiped from the database.');
        rerender();
      } catch (e) {
        alert(`Failed to delete products: ${e.message}`);
        btn.textContent = "🧨 Delete All Products";
        btn.disabled = false;
      }
    }
  });
}
