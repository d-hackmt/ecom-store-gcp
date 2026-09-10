import { escapeHtml } from '../../utils/escapeHtml.js';

/**
 * Read-only order history list — no events to wire.
 */
export function renderOrderHistory(orders) {
  return `
    <div class="card">
      <h2 class="card-heading">Order History</h2>
      ${orders.length === 0
        ? `<p class="muted">No orders yet.</p>`
        : `<div class="list-stack">
             ${orders.map(o => `
               <div class="list-row">
                 <div>
                   <p style="font-weight: bold; color: #111827;">${escapeHtml(o.product_name)}</p>
                   <p class="muted" style="font-size: 0.85rem;">Qty: ${escapeHtml(o.quantity)}${o.created_at ? ` • ${new Date(o.created_at).toLocaleDateString()}` : ''}</p>
                 </div>
                 <p class="price-lg">₹${o.price * o.quantity}</p>
               </div>`).join('')}
           </div>`}
    </div>
  `;
}
