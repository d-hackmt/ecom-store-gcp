import { state } from '../state.js';

// Reads (this file is served by the retrieval service) use relative paths.
export const API_BASE = "";

// Writes go to the separate ingestion service. On Cloud Run (or any deploy
// where the two services get unrelated hostnames, not same-host-different-port)
// there is no way to guess this — it's resolved at startup via initIngestionApiBase(),
// which asks the retrieval service's own /config endpoint (it's told the
// ingestion service's real URL via the INGESTION_SERVICE_URL env var at deploy
// time). This local-dev heuristic is just the fallback until that resolves.
export let INGESTION_API_BASE = window.location.port === '8000'
  ? `${window.location.protocol}//${window.location.hostname}:8001`
  : '';

/**
 * Call once at app startup (before any write call can happen) to resolve the
 * real ingestion service URL for the current deployment. Safe to call even
 * when /config doesn't exist or returns nothing — keeps the local-dev guess.
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
    // Keep the local-dev fallback already assigned above.
  }
}

// Identifies the current user to the backend's admin-only routes.
export const adminHeaders = () => ({ 'X-User-Email': state.sessionId });
