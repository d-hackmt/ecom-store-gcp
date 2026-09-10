import { request } from './http.js';

/**
 * Place a new order.
 */
export async function placeOrder(userEmail, productName, quantity = 1, price = 0) {
  return request('/orders', {
    method: 'POST',
    write: true,
    body: { user_email: userEmail, product_name: productName, quantity, price },
  });
}

/**
 * Fetch a user's past orders, most recent first.
 */
export async function getOrderHistory(email) {
  return request(`/orders/${encodeURIComponent(email)}`);
}
