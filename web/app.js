const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const escapeHtml = (v) => String(v ?? '').replace(/[&<>"']/g, (ch) => ESCAPES[ch]);

const messagesEl = document.getElementById('messages');
const formEl = document.getElementById('form');
const inputEl = document.getElementById('input');
const sendEl = document.getElementById('send');

const messages = [];
let loading = false;

function render() {
  messagesEl.innerHTML =
    messages.map(renderMessage).join('') +
    (loading ? '<p class="typing">🤖 Typing…</p>' : '');
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderMessage(msg) {
  if (msg.sender === 'user') {
    return `<div class="message message-user"><p>${escapeHtml(msg.text)}</p></div>`;
  }
  if (msg.type === 'products') {
    const items = msg.data || [];
    const list = items.length === 0
      ? '<p class="note">No products found 😢</p>'
      : `<div class="products">${items.map((p) => `
          <div class="product">
            <img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.name)}" />
            <p>${escapeHtml(p.name)}</p>
            <p class="price">₹${escapeHtml(p.price)}</p>
          </div>`).join('')}</div>`;
    return `<div class="message message-bot">
      ${msg.message ? `<p class="note">${escapeHtml(msg.message)}</p>` : ''}
      ${list}
    </div>`;
  }
  return `<div class="message message-bot"><p>${escapeHtml(msg.message)}</p></div>`;
}

async function send(text) {
  messages.push({ sender: 'user', text });
  loading = true;
  render();
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    messages.push({ sender: 'bot', type: data.type, data: data.data, message: data.message });
  } catch {
    messages.push({ sender: 'bot', type: 'text', message: 'Sorry, something went wrong. Please try again.' });
  } finally {
    loading = false;
    render();
  }
}

formEl.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text || loading) return;
  inputEl.value = '';
  send(text);
});
