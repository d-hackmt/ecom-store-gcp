import { API_BASE, INGESTION_API_BASE, adminHeaders } from './common.js';

/**
 * The one fetch() wrapper the whole API layer goes through.
 *
 * Options:
 *   method   - HTTP verb (default 'GET')
 *   body     - a plain object is sent as JSON; a FormData is sent as-is
 *   headers  - extra request headers
 *   write    - true routes the call to the ingestion service instead of same-origin
 *   admin    - true adds the X-User-Email header the admin-only routes check
 *
 * Always resolves to the parsed JSON body (or null when there is none), and
 * throws Error(<backend detail>) on any non-2xx response or network failure —
 * so every caller can rely on "it returned" meaning "it worked".
 */
const REQUEST_TIMEOUT_MS = 20000;

export async function request(path, { method = 'GET', body, headers = {}, write = false, admin = false } = {}) {
  const base = write ? INGESTION_API_BASE : API_BASE;

  const opts = {
    method,
    headers: { ...(admin ? adminHeaders() : {}), ...headers },
  };
  if (body instanceof FormData) {
    opts.body = body;
  } else if (body !== undefined) {
    opts.body = JSON.stringify(body);
    opts.headers['Content-Type'] = 'application/json';
  }

  const timeoutController = new AbortController();
  const timeoutId = setTimeout(() => timeoutController.abort(), REQUEST_TIMEOUT_MS);
  opts.signal = timeoutController.signal;

  let res;
  try {
    res = await fetch(`${base}${path}`, opts);
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('The server is taking too long to respond. Please try again in a moment.');
    }
    throw new Error('Could not reach the server. Check your connection and try again.');
  } finally {
    clearTimeout(timeoutId);
  }

  const payload = await res.json().catch(() => null);

  if (!res.ok) {
    const detail = payload && payload.detail;
    throw new Error(typeof detail === 'string' ? detail : `Request failed (${res.status})`);
  }
  return payload;
}
