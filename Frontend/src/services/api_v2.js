// Barrel re-export: keeps existing `from '../services/api_v2.js'` imports
// working while the actual implementations live in services/api/*.js, split
// by domain. Every call goes through the shared `request()` helper in http.js.
export * from './api/common.js';
export * from './api/http.js';
export * from './api/auth.js';
export * from './api/products.js';
export * from './api/cart.js';
export * from './api/orders.js';
export * from './api/chat.js';
