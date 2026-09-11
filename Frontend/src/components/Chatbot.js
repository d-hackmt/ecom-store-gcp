import { state } from '../services/state.js';
import { sendChatMessage } from '../services/api/chat.js';
import { navigate } from '../services/nav.js';
import { escapeHtml } from '../utils/escapeHtml.js';

const ROOT_ID = 'chatbot-root';

/** Render the chatbot into #chatbot-root and wire its events. Called once at
 *  startup and again on every chat state change (open/close, new message). */
export function mountChatbot() {
  const root = document.getElementById(ROOT_ID);
  if (!root) return;
  root.innerHTML = renderChatbot();
  wireChatbotEvents();
}

function renderChatbot() {
  const { chatOpen, chatLoading, chatMessages, chatInput } = state;
  return `
    <div class="chatbot-container">
      <button id="chatToggle" class="chatbot-toggle">💬 Chat</button>
      ${chatOpen ? `
        <div class="chatbot-window">
          <div class="chatbot-header">
            <span>AI Assistant</span>
            <button id="chatClear" class="chatbot-clear" title="Clear chat">Clear</button>
          </div>
          <div class="chatbot-messages" id="chatMessages">
            ${chatMessages.map(renderMessage).join('')}
            ${chatLoading ? '<p class="chatbot-typing">🤖 Typing...</p>' : ''}
          </div>
          <div class="chatbot-input">
            <input type="text" id="chatInput" value="${escapeHtml(chatInput)}"
                   placeholder="Ask about products..." ${chatLoading ? 'disabled' : ''} />
            <button id="chatSend" ${chatLoading ? 'disabled' : ''}>Send</button>
          </div>
        </div>` : ''}
    </div>`;
}

function renderMessage(msg) {
  if (msg.sender === 'user') {
    return `<div class="message message-user"><p>${escapeHtml(msg.text)}</p></div>`;
  }
  if (msg.type === 'products') {
    const items = msg.data || [];
    const list = items.length === 0
      ? '<p class="chatbot-note">No products found 😢</p>'
      : `<div class="message-products">
           ${items.map(p => `
             <div class="product-recommendation" data-id="${escapeHtml(p.id)}">
               <img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.name)}" />
               <p>${escapeHtml(p.name)}</p>
               <p class="price">₹${escapeHtml(p.price)}</p>
             </div>`).join('')}
         </div>`;
    return `
      <div class="message message-bot">
        ${msg.message ? `<p class="chatbot-note">${escapeHtml(msg.message)}</p>` : ''}
        ${list}
      </div>`;
  }
  return `<div class="message message-bot"><p>${escapeHtml(msg.message)}</p></div>`;
}

function wireChatbotEvents() {
  document.getElementById('chatToggle')?.addEventListener('click', () => {
    state.chatOpen = !state.chatOpen;
    mountChatbot();
  });

  document.getElementById('chatSend')?.addEventListener('click', sendCurrentMessage);

  document.getElementById('chatClear')?.addEventListener('click', () => {
    state.chatMessages = [];
    mountChatbot();
  });

  const input = document.getElementById('chatInput');
  input?.addEventListener('input', (e) => { state.chatInput = e.target.value; });
  input?.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendCurrentMessage(); });
  input?.focus();

  document.querySelectorAll('.product-recommendation').forEach(el => {
    el.addEventListener('click', () => navigate(`#/product/${el.dataset.id}`));
  });

  const messages = document.getElementById('chatMessages');
  if (messages) messages.scrollTop = messages.scrollHeight;
}

async function sendCurrentMessage() {
  const text = (state.chatInput || '').trim();
  if (!text || state.chatLoading) return;

  state.chatMessages = [...state.chatMessages, { sender: 'user', text }];
  state.chatInput = '';
  state.chatLoading = true;
  mountChatbot();

  try {
    const data = await sendChatMessage(text);
    state.chatMessages = [...state.chatMessages, {
      sender: 'bot', type: data.type, data: data.data, message: data.message,
    }];
  } catch (err) {
    console.error(err);
    state.chatMessages = [...state.chatMessages, {
      sender: 'bot', type: 'text', message: 'Sorry, something went wrong. Please try again.',
    }];
  } finally {
    state.chatLoading = false;
    mountChatbot();
  }
}
