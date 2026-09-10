import { state } from './state.js';
import { addToCart } from './api/cart.js';
import { refreshCartCount } from './cartCount.js';

/**
 * Shared "Add to Cart" button behaviour: disables the button, calls the API,
 * refreshes the header cart count, and briefly shows a success state before
 * handing control back to the caller (each page re-renders differently after).
 */
export async function handleAddToCartClick(buttonEl, productName, { onSuccess, delay = 1000 } = {}) {
  const originalText = buttonEl.textContent;
  buttonEl.disabled = true;
  buttonEl.textContent = 'Adding...';
  try {
    await addToCart(state.sessionId, productName, 1);
    await refreshCartCount();
    buttonEl.textContent = 'Added! ✅';
    if (onSuccess) setTimeout(onSuccess, delay);
  } catch (err) {
    console.error('Failed to add to cart:', err);
    alert(`Failed to add to cart: ${err.message}`);
    buttonEl.disabled = false;
    buttonEl.textContent = originalText;
  }
}
