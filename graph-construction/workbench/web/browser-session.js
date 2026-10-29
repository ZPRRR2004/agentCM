// An open connection tracks the page even when background-tab timers are paused.
let connection;
let identity;
let workspaceToken;

function connect() {
  if (connection || !workspaceToken) return;
  identity = crypto.randomUUID();
  const query = new URLSearchParams({ id: identity, token: workspaceToken });
  connection = new EventSource(`/api/session/events?${query}`);
}

function disconnect() {
  if (!connection) return;
  connection.close();
  connection = null;
  fetch('/api/session/close', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Workspace-Token': workspaceToken },
    body: JSON.stringify({ id: identity }),
    keepalive: true,
  }).catch(() => {});
}

export function startBrowserSession(token) {
  workspaceToken = token;
  connect();
}

window.addEventListener('pagehide', disconnect);
window.addEventListener('pageshow', connect);
