import { request } from './http.js';

/**
 * Send a message to the AI chatbot and await its response
 * ({ type: 'text' | 'products', message, data }).
 */
export async function sendChatMessage(message) {
  return request('/chat', { method: 'POST', body: { message } });
}
