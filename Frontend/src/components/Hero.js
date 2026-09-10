export function renderHero() {
  return `
  <div class="hero">
    <div class="container hero-grid">
      <div class="hero-content">
        <div class="hero-badge">
          <span>New Collection 2026</span>
        </div>
        <h1 class="hero-title">Elevate Your Style with Premium Fashion</h1>
        <p class="hero-desc">Discover our curated collection of timeless pieces that blend sophistication with modern design.</p>
        <div class="hero-actions">
          <button class="btn btn-primary" id="heroShopNow">Shop Now</button>
          <button class="btn btn-outline" id="heroViewCatalog">View Catalog</button>
        </div>
        <div class="hero-stats">
          <div class="hero-stat">
            <p>500+</p>
            <p>Premium Products</p>
          </div>
          <div class="hero-stat">
            <p>50K+</p>
            <p>Happy Customers</p>
          </div>
          <div class="hero-stat">
            <p>4.9</p>
            <p>Average Rating</p>
          </div>
        </div>
      </div>
      <div class="hero-image-container">
        <div class="hero-image-bg"></div>
        <img src="https://images.pexels.com/photos/1926769/pexels-photo-1926769.jpeg?auto=compress&cs=tinysrgb&w=800" alt="Fashion Model" class="hero-image" />
      </div>
    </div>
    <div class="hero-decoration-1"></div>
    <div class="hero-decoration-2"></div>
  </div>
`;
}

/** Both hero call-to-action buttons jump the user down to the product grid. */
export function wireHeroEvents() {
  const scrollToProducts = () =>
    document.querySelector('.products-section')?.scrollIntoView({ behavior: 'smooth' });
  document.getElementById('heroShopNow')?.addEventListener('click', scrollToProducts);
  document.getElementById('heroViewCatalog')?.addEventListener('click', scrollToProducts);
}
