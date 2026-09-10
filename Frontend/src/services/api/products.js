import { request } from './http.js';

/**
 * Fetch products, optionally filtering by category and/or price range.
 */
export async function fetchProducts(category = '', minPrice = null, maxPrice = null) {
  const params = new URLSearchParams();
  if (category) params.set('category', category);
  if (minPrice !== null) params.set('min_price', minPrice);
  if (maxPrice !== null) params.set('max_price', maxPrice);
  const query = params.toString() ? `?${params.toString()}` : '';
  return request(`/products${query}`);
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
  return request('/products', { method: 'POST', write: true, admin: true, body: formData });
}

/**
 * Bulk-add products from an Excel file plus a zip of images.
 * The Excel 'image' column values must match filenames inside the zip.
 */
export async function bulkUploadProducts(excelFile, zipFile) {
  const formData = new FormData();
  formData.append('excel_file', excelFile);
  formData.append('images_zip', zipFile);
  return request('/products/bulk-upload', { method: 'POST', write: true, admin: true, body: formData });
}

/**
 * Update an existing product. `formData` must be a FormData (the endpoint is
 * multipart/form-data only); include only the fields being changed.
 */
export async function updateProduct(id, formData) {
  return request(`/products/${id}`, { method: 'PUT', write: true, admin: true, body: formData });
}

/**
 * Delete a product by its ID.
 */
export async function deleteProduct(id) {
  return request(`/products/${id}`, { method: 'DELETE', write: true, admin: true });
}

/**
 * Delete all products from the database.
 */
export async function deleteAllProducts() {
  return request('/products', { method: 'DELETE', write: true, admin: true });
}
