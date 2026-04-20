/**
 * API Client — Handles all backend requests with JWT auth.
 */

const API_BASE = '/api/v1';

function getToken() {
  return localStorage.getItem('impetusai_token');
}

function setToken(token) {
  localStorage.setItem('impetusai_token', token);
}

function clearToken() {
  localStorage.removeItem('impetusai_token');
}

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401 && !path.startsWith('/auth/')) {
    clearToken();
    window.location.href = '/login';
    throw new Error('Session expired');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────
export async function signup(email, password, fullName, department) {
  const user = await request('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: fullName, department }),
  });
  return user;
}

export async function login(email, password) {
  const data = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data;
}

export async function getMe() {
  return request('/auth/me');
}

export function logout() {
  clearToken();
  window.location.href = '/login';
}

export function isAuthenticated() {
  return !!getToken();
}

// ── Chat ──────────────────────────────────────────────────────
export async function sendMessage(message, conversationId = null) {
  return request('/chat/send', {
    method: 'POST',
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
}

export async function getConversations() {
  return request('/chat/conversations');
}

export async function getConversation(id) {
  return request(`/chat/conversations/${id}`);
}

export async function submitFeedback(messageId, feedback, comment = null) {
  return request('/chat/feedback', {
    method: 'POST',
    body: JSON.stringify({ message_id: messageId, feedback, comment }),
  });
}

export async function renameConversation(id, title) {
  return request(`/chat/conversations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ title }),
  });
}

export async function deleteConversation(id) {
  return request(`/chat/conversations/${id}`, {
    method: 'DELETE',
  });
}

// ── Tickets ───────────────────────────────────────────────────
export async function createTicket(data) {
  return request('/tickets', { method: 'POST', body: JSON.stringify(data) });
}

export async function getTickets(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/tickets${query ? `?${query}` : ''}`);
}

export async function getTicket(id) {
  return request(`/tickets/${id}`);
}

export async function updateTicket(id, data) {
  return request(`/tickets/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export async function getTicketAssignees() {
  return request('/tickets/assignees');
}

// ── Documents ─────────────────────────────────────────────────
export async function uploadDocument(file, docType = 'hr_policy', category = 'General') {
  const formData = new FormData();
  formData.append('file', file);

  const token = getToken();
  const res = await fetch(
    `${API_BASE}/documents/upload?doc_type=${docType}&category=${category}`,
    {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    }
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function getDocuments(docType = null) {
  const query = docType ? `?doc_type=${docType}` : '';
  return request(`/documents${query}`);
}

export async function deleteDocument(id) {
  return request(`/documents/${id}`, { method: 'DELETE' });
}

// ── Governance ────────────────────────────────────────────────
export async function requestAccess(requestedRole, justification) {
  return request('/governance/request', {
    method: 'POST',
    body: JSON.stringify({ requested_role: requestedRole, justification }),
  });
}

export async function getAccessRequests(statusFilter = null) {
  const query = statusFilter ? `?status_filter=${statusFilter}` : '';
  return request(`/governance/requests${query}`);
}

export async function processAccessRequest(requestId, status, adminComment = null) {
  return request(`/governance/requests/${requestId}/process`, {
    method: 'POST',
    body: JSON.stringify({ status, admin_comment: adminComment }),
  });
}

export async function getGovernanceStats() {
  return request('/governance/stats');
}

// ── Admin / User Management ────────────────────────────────────
export async function fetchUsers() {
  return request('/admin/users');
}

export async function updateUser(userId, data) {
  return request(`/admin/users/${userId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function createUser(data) {
  return request('/admin/users', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ── Analytics ──────────────────────────────────────────────────
export async function fetchAnalytics() {
  return request('/analytics/dashboard');
}

// ── Leave ──────────────────────────────────────────────────────
export async function getLeaveBalance() {
  return request('/leave/balance');
}

export async function getLeaveRequests() {
  return request('/leave');
}

export async function createLeaveRequest(data) {
  return request('/leave', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateLeaveRequest(id, data) {
  return request(`/leave/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

// ── Timesheet ──────────────────────────────────────────────────
export async function getTimesheets() {
  return request('/timesheet');
}

export async function getTimesheetProjects() {
  return request('/timesheet/projects');
}

export async function submitTimesheet(data) {
  return request('/timesheet', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateTimesheet(id, data) {
  return request(`/timesheet/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}
