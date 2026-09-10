import { request } from './http.js';

/**
 * Add an item to the shopping cart. If the same product is already there, the
 * backend increases its quantity instead of adding a duplicate row.
 */
export async function addToCart(userEmail, productName, quantity = 1) {
  return request('/cart/add', {
    method: 'POST',
    write: true,
    body: { user_email: userEmail, product_name: productName, quantity },
  });
}

/**
 * Fetch all items in the user's cart.
 */
export async function getCart(userEmail) {
  return request(`/cart/${encodeURIComponent(userEmail)}`);
}

/**
 * Clear the user's cart completely.
 */
export async function clearCart(userEmail) {
  return request(`/cart/${encodeURIComponent(userEmail)}`, { method: 'DELETE', write: true });
}
