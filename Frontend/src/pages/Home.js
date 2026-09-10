import { state } from '../services/state.js';
import { fetchProducts } from '../services/api_v2.js';
import { handleAddToCartClick } from '../services/cartActions.js';
import { renderHero, wireHeroEvents } from '../components/Hero.js';
import { navigate, currentRoute } from '../services/nav.js';
import { escapeHtml } from '../utils/escapeHtml.js';

// Price range options shown in the filter bar.
const PRICE_RANGES = [
  { label: 'All Prices', min: null, max: null },
  { label: 'Under ₹500',  min: null, max: 500 },
  { label: '₹500–₹1000',  min: 500,  max: 1000 },
  { label: '₹1000–₹2000', min: 1000, max: 2000 },
  { label: '₹2000–₹5000', min: 2000, max: 5000 },
  { label: 'Above ₹5000', min: 5000, max: null },
];

export async function renderHome() {
  // The catalog view is fully described by the hash: #/?cat=men&min=500&max=1000
  const { params } = currentRoute();
  state.currentCategory = params.get('cat') || '';
  state.priceFilter = {
    min: params.has('min') ? Number(params.get('min')) : null,
    max: params.has('max') ? Number(params.get('max')) : null,
  };

  try {
    state.products = await fetchProducts(state.currentCategory, state.priceFilter.min, state.priceFilter.max);
  } catch (err) {
    console.error('Failed to load products:', err);
    state.products = [];
  }

  document.getElementById('app').innerHTML = `
    ${renderHero()}
    <div class="products-section">
      <h2 class="section-title">Our Products</h2>
      <div class="price-filter-bar" id="price-filter-container">
        ${PRICE_RANGES.map(range => {
          const active = state.priceFilter.min === range.min && state.priceFilter.max === range.max;
          return `<button class="price-filter-btn ${active ? 'active' : ''}"
                    data-min="${range.min ?? ''}" data-max="${range.max ?? ''}">${range.label}</button>`;
        }).join('')}
      </div>
      <div class="products-grid">
        ${state.products.length === 0
          ? `<p class="products-empty">No products found for this filter.</p>`
          : state.products.map(renderProductCard).join('')}
      </div>
    </div>
  `;

  wireHeroEvents();
  wireHomeEvents();
}

function renderProductCard(p) {
  const id = escapeHtml(p.id);
  return `
    <div class="product-card" data-id="${id}">
      <div class="product-image">
        ${p.image
          ? `<img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.name)}" loading="lazy" />`
          : `<span class="product-placeholder">Product Image</span>`}
      </div>
      <div class="product-info">
        <h3 class="product-name">${escapeHtml(p.name)}</h3>
        <p class="product-desc">${escapeHtml(p.description)}</p>
        <div class="product-footer">
          <span class="product-price">₹${escapeHtml(p.price)}</span>
          <span class="product-category">${escapeHtml(p.category)}</span>
        </div>
        <button class="add-to-cart-btn" data-id="${id}">Add to Cart</button>
      </div>
    </div>`;
}

/** Build a "#/?cat=&min=&max=" hash from the current filter plus any overrides. */
function filterHash(overrides = {}) {
  const cat = 'cat' in overrides ? overrides.cat : state.currentCategory;
  const min = 'min' in overrides ? overrides.min : state.priceFilter.min;
  const max = 'max' in overrides ? overrides.max : state.priceFilter.max;
  const params = new URLSearchParams();
  if (cat) params.set('cat', cat);
  if (min != null) params.set('min', min);
  if (max != null) params.set('max', max);
  const query = params.toString();
  return query ? `#/?${query}` : '#/';
}

function wireHomeEvents() {
  document.querySelectorAll('#price-filter-container .price-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const min = btn.dataset.min !== '' ? Number(btn.dataset.min) : null;
      const max = btn.dataset.max !== '' ? Number(btn.dataset.max) : null;
      navigate(filterHash({ min, max }));
    });
  });

  document.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('click', async (e) => {
      if (e.target.classList.contains('add-to-cart-btn')) {
        e.stopPropagation();
        const product = state.products.find(p => String(p.id) === card.dataset.id) || { name: 'Unknown Product' };
        await handleAddToCartClick(e.target, product.name, { onSuccess: () => renderHome() });
      } else {
        navigate(`#/product/${card.dataset.id}`);
      }
    });
  });
}
