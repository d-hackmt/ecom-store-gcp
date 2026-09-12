import { state } from '../state.js';

// This branch only ships the monolith — reads and writes are the same origin.
export const API_BASE = "";
export let INGESTION_API_BASE = '';

/**
 * Call once at app startup. Reads /config in case a future deploy mode ever
 * points writes elsewhere; a no-op today since the monolith always returns
 * the same origin.
 */
export async function initIngestionApiBase() {
  try {
    const res = await fetch(`${API_BASE}/config`);
    if (!res.ok) return;
    const data = await res.json();
    if (data.ingestion_base_url !== undefined && data.ingestion_base_url !== null) {
      INGESTION_API_BASE = data.ingestion_base_url;
    }
  } catch (err) {
    // Keep the same-origin default already assigned above.
  }
}

// Identifies the current user to the backend's admin-only routes.
export const adminHeaders = () => ({ 'X-User-Email': state.sessionId });
