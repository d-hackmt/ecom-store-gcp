/**
 * Hash-based navigation helpers, kept dependency-free so both the router and the
 * header can import them without a circular reference.
 */

/** Navigate to a hash route, e.g. navigate('#/cart') or navigate('#/?cat=men'). */
export function navigate(path) {
  window.location.hash = path.startsWith('#') ? path : `#${path}`;
}

/**
 * Parse the current hash into a path and query params.
 * "#/?cat=men&min=500" -> { path: '/', params: URLSearchParams({cat, min}) }
 */
export function currentRoute() {
  const hash = window.location.hash.slice(1) || '/';
  const [path, query = ''] = hash.split('?');
  return { path: path || '/', params: new URLSearchParams(query) };
}
