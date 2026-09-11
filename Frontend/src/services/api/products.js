import { request } from './http.js';

// Caches in-flight/resolved product list fetches by query string, so pages
// that fetch the same catalog view (e.g. Home and Cart both fetching the
// unfiltered list) share one network request instead of each firing their own.
const productsCache = new Map();

/** Clears the product list cache; call after any write so stale data isn't served. */
export function invalidateProductsCache() {
  productsCache.clear();
}

/**
 * Fetch products, optionally filtering by category and/or price range.
 */
export async function fetchProducts(category = '', minPrice = null, maxPrice = null) {
  const params = new URLSearchParams();
  if (category) params.set('category', category);
  if (minPrice !== null) params.set('min_price', minPrice);
  if (maxPrice !== null) params.set('max_price', maxPrice);
  const query = params.toString() ? `?${params.toString()}` : '';

  if (productsCache.has(query)) return productsCache.get(query);
  const promise = request(`/products${query}`).catch(err => {
    productsCache.delete(query);
    throw err;
  });
  productsCache.set(query, promise);
  return promise;
}

/**
 * Fetch a single product by its ID.
 */
export async function fetchProduct(id) {
  return request(`/products/${id}`);
}

/**
 * Add a new product. `formData` must be a FormData carrying the fields and the image.
 */
export async function addProduct(formData) {
  const result = await request('/products', { method: 'POST', write: true, admin: true, body: formData });
  invalidateProductsCache();
  return result;
}

/**
 * Bulk-add products from an Excel file plus a zip of images.
 * The Excel 'image' column values must match filenames inside the zip.
 */
export async function bulkUploadProducts(excelFile, zipFile) {
  const formData = new FormData();
  formData.append('excel_file', excelFile);
  formData.append('images_zip', zipFile);
  const result = await request('/products/bulk-upload', { method: 'POST', write: true, admin: true, body: formData });
  invalidateProductsCache();
  return result;
}

/**
 * Update an existing product. `formData` must be a FormData (the endpoint is
 * multipart/form-data only); include only the fields being changed.
 */
export async function updateProduct(id, formData) {
  const result = await request(`/products/${id}`, { method: 'PUT', write: true, admin: true, body: formData });
  invalidateProductsCache();
  return result;
}

/**
 * Delete a product by its ID.
 */
export async function deleteProduct(id) {
  const result = await request(`/products/${id}`, { method: 'DELETE', write: true, admin: true });
  invalidateProductsCache();
  return result;
}

/**
 * Delete all products from the database.
 */
export async function deleteAllProducts() {
  const result = await request('/products', { method: 'DELETE', write: true, admin: true });
  invalidateProductsCache();
  return result;
}
