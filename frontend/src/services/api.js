const RAW_API_BASE = import.meta.env.VITE_API_URL || '';
const API_BASE = RAW_API_BASE.replace(/\/+$/, '');

export async function sendChatMessage(query, options = {}) {
  const { top_k = 4, model, api_key, history = [], thread_id } = options;
  const payload = {
    query,
    top_k,
    history,
    thread_id: thread_id || undefined,
    model: model || undefined,
    api_key: api_key || undefined,
  };

  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error (${response.status}): ${errorText}`);
  }

  return response.json();
}

export async function fetchThreads() {
  try {
    const response = await fetch(`${API_BASE}/api/threads`);
    if (!response.ok) return [];
    return response.json();
  } catch (err) {
    console.error('Failed to fetch conversation threads:', err);
    return [];
  }
}

export async function fetchThreadDetail(threadId) {
  try {
    const response = await fetch(`${API_BASE}/api/threads/${threadId}`);
    if (!response.ok) return null;
    return response.json();
  } catch (err) {
    console.error('Failed to fetch thread detail:', err);
    return null;
  }
}

export async function createThread(title = 'New Conversation') {
  try {
    const response = await fetch(`${API_BASE}/api/threads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) return null;
    return response.json();
  } catch (err) {
    console.error('Failed to create thread:', err);
    return null;
  }
}

export async function deleteThread(threadId) {
  try {
    const response = await fetch(`${API_BASE}/api/threads/${threadId}`, {
      method: 'DELETE',
    });
    return response.ok;
  } catch (err) {
    console.error('Failed to delete thread:', err);
    return false;
  }
}

export async function fetchHealthStatus() {
  try {
    const response = await fetch(`${API_BASE}/api/health`);
    if (!response.ok) return null;
    return response.json();
  } catch (err) {
    console.error('Failed to fetch health status:', err);
    return null;
  }
}

export async function fetchProjects() {
  try {
    const response = await fetch(`${API_BASE}/api/projects`);
    if (!response.ok) return [];
    return response.json();
  } catch (err) {
    console.error('Failed to fetch projects:', err);
    return [];
  }
}
