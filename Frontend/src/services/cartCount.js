import { state } from './state.js';
import { getCart } from './api/cart.js';
import { mountHeader } from '../components/Header.js';

/**
 * The one place `state.cartItemCount` is written. Sets the badge count and
 * repaints the header so it shows immediately.
 */
export function setCartCount(count) {
  state.cartItemCount = count;
  mountHeader();
}

/**
 * Fetch the current cart and set the badge to the total item quantity.
 * Swallows failures (the badge is a convenience, not critical).
 */
export async function refreshCartCount() {
  try {
    const items = await getCart(state.sessionId);
    setCartCount(items.reduce((sum, item) => sum + (item.quantity || 0), 0));
  } catch (err) {
    console.error('Failed to refresh cart count:', err);
  }
}
