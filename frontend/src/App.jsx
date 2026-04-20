import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  MessageSquare, Ticket, FileText, Shield, LogOut, Plus,
  Send, ThumbsUp, ThumbsDown, Upload, Trash2, LayoutDashboard, Edit2,
  Bot, User, ChevronRight, AlertCircle, Calendar, Clock, CheckCircle, XCircle
} from 'lucide-react';
import * as api from './api';

/* ═══════════════════════════════════════════════════════════════
   Auth Context
   ═══════════════════════════════════════════════════════════════ */
const AuthContext = React.createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (api.isAuthenticated()) {
      api.getMe().then(setUser).catch(() => api.logout()).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) return <div className="loading"><div className="spinner" /></div>;
  return <AuthContext.Provider value={{ user, setUser }}>{children}</AuthContext.Provider>;
}

function useAuth() { return React.useContext(AuthContext); }

function ProtectedRoute({ children }) {
  return api.isAuthenticated() ? children : <Navigate to="/login" />;
}

function AdminRoute({ children }) {
  const { user } = useAuth();
  if (!user) return null;
  return (user.role === 'admin' || user.role === 'hr_admin') ? children : <Navigate to="/" />;
}

function StrictAdminRoute({ children }) {
  const { user } = useAuth();
  if (!user) return null;
  return user.role === 'admin' ? children : <Navigate to="/" />;
}

function AnalyticsRoute({ children }) {
  const { user } = useAuth();
  if (!user) return null;
  return ['admin', 'hr_admin', 'it_agent'].includes(user.role) ? children : <Navigate to="/" />;
}

/* ═══════════════════════════════════════════════════════════════
   Login Page
   ═══════════════════════════════════════════════════════════════ */
function LoginPage() {
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.login(email, password);
      const user = await api.getMe();
      setUser(user);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <div className="logo-icon">AI</div>
          <h1>Welcome Back</h1>
          <p>Sign in to ImpetusAI Workplace Platform</p>
        </div>
        {error && <div className="error-toast">{error}</div>}
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Email</label>
            <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@impetus.com" required />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
        <div className="auth-switch">
          Don't have an account? <a href="/signup">Sign Up</a>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Signup Page
   ═══════════════════════════════════════════════════════════════ */
function SignupPage() {
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '', full_name: '', department: 'Engineering' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.signup(form.email, form.password, form.full_name, form.department);
      await api.login(form.email, form.password);
      const user = await api.getMe();
      setUser(user);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const update = (k, v) => setForm({ ...form, [k]: v });

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <div className="logo-icon">AI</div>
          <h1>Create Account</h1>
          <p>Join the ImpetusAI platform</p>
        </div>
        {error && <div className="error-toast">{error}</div>}
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Full Name</label>
            <input className="input" value={form.full_name} onChange={e => update('full_name', e.target.value)} placeholder="John Doe" required />
          </div>
          <div className="input-group">
            <label>Email</label>
            <input className="input" type="email" value={form.email} onChange={e => update('email', e.target.value)} placeholder="you@impetus.com" required />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input className="input" type="password" value={form.password} onChange={e => update('password', e.target.value)} placeholder="Min 8 characters" required minLength={8} />
          </div>
          <div className="input-group">
            <label>Department</label>
            <select className="input" value={form.department} onChange={e => update('department', e.target.value)}>
              <option>Engineering</option>
              <option>HR</option>
              <option>IT</option>
              <option>Finance</option>
              <option>Marketing</option>
              <option>Operations</option>
              <option>General</option>
            </select>
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Creating Account…' : 'Sign Up'}
          </button>
        </form>
        <div className="auth-switch">
          Already have an account? <a href="/login">Sign In</a>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Chat Page
   ═══════════════════════════════════════════════════════════════ */
function ChatPage() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [editingConvId, setEditingConvId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(null); // conv id pending delete
  const messagesEnd = useRef(null);

  useEffect(() => { loadConversations(); }, []);

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConversations = async () => {
    try {
      const convs = await api.getConversations();
      setConversations(convs);
    } catch {}
  };

  const selectConversation = async (id) => {
    try {
      const conv = await api.getConversation(id);
      setActiveConv(id);
      setMessages(conv.messages || []);
    } catch {}
  };

  const handleSend = async () => {
    if (!input.trim() || sending) return;

    const userMsg = { id: Date.now().toString(), role: 'user', content: input, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setSending(true);

    try {
      const res = await api.sendMessage(input, activeConv);
      setActiveConv(res.conversation_id);
      setMessages(prev => [...prev, res.message]);
      loadConversations();
    } catch (err) {
      setMessages(prev => [...prev, { id: 'err', role: 'assistant', content: `⚠️ Error: ${err.message}`, created_at: new Date().toISOString() }]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const startNew = () => { setActiveConv(null); setMessages([]); };

  const handleDelete = (e, id) => {
    e.stopPropagation();
    setDeleteConfirm(id);
  };

  const confirmDelete = async () => {
    const id = deleteConfirm;
    setDeleteConfirm(null);
    try {
      await api.deleteConversation(id);
      if (activeConv === id) startNew();
      loadConversations();
    } catch {}
  };

  const startEdit = (e, c) => {
    e.stopPropagation();
    setEditingConvId(c.id);
    setEditTitle(c.title || '');
  };

  const saveEdit = async (id) => {
    if (editingConvId !== id) return;
    const newTitle = editTitle.trim();
    setEditingConvId(null);
    if (!newTitle) return;
    
    // Optimistic UI: Update locally first
    setConversations(prev => prev.map(c => c.id === id ? { ...c, title: newTitle } : c));
    
    try {
      await api.renameConversation(id, newTitle);
    } catch (err) {
      console.error('Failed to rename:', err);
      // Rollback on failure? For now just log.
      loadConversations();
    }
  };

  const handleEditKeyDown = (e, id) => {
    if (e.key === 'Enter') { e.preventDefault(); saveEdit(id); }
    else if (e.key === 'Escape') setEditingConvId(null);
  };

  const initials = user?.full_name?.split(' ').map(w => w[0]).join('').slice(0, 2) || 'U';

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 0px)' }}>
      {/* Delete confirmation modal */}
      {deleteConfirm && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          onClick={() => setDeleteConfirm(null)}>
          <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: 12, padding: '24px 28px', width: 340, boxShadow: '0 8px 32px rgba(0,0,0,0.6)' }}
            onClick={e => e.stopPropagation()}>
            <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 8, color: 'var(--text-primary)' }}>Delete conversation?</div>
            <div style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 24 }}>This will delete this conversation and cannot be undone.</div>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button className="btn btn-ghost btn-sm" onClick={() => setDeleteConfirm(null)}>Cancel</button>
              <button className="btn btn-sm" style={{ background: '#dc2626', color: '#fff', border: 'none' }} onClick={confirmDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}
      {/* Conversation sidebar */}
      <div style={{ width: 240, borderRight: '1px solid var(--border-color)', padding: '12px 8px', display: 'flex', flexDirection: 'column' }}>
        <button className="btn btn-primary btn-sm" onClick={startNew} style={{ marginBottom: 12, width: '100%' }}>
          <Plus size={14} /> New Chat
        </button>
        <div className="conv-list" style={{ flex: 1, overflowY: 'auto' }}>
          {conversations.map(c => (
            <div key={c.id} className={`conv-item-wrapper ${activeConv === c.id ? 'active' : ''}`} style={{ position: 'relative', display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
              {editingConvId === c.id ? (
                <div style={{ display: 'flex', width: '100%', alignItems: 'center' }}>
                  <input
                    autoFocus
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onKeyDown={(e) => handleEditKeyDown(e, c.id)}
                    onBlur={() => saveEdit(c.id)}
                    style={{ flex: 1, padding: '4px 8px', fontSize: '14px', borderRadius: '4px', border: '1px solid var(--border-color)', background: 'var(--surface-color)', color: 'var(--text-color)' }}
                  />
                </div>
              ) : (
                <>
                  <button className={`conv-item ${activeConv === c.id ? 'active' : ''}`} onClick={() => selectConversation(c.id)} style={{ flex: 1, textAlign: 'left', paddingRight: '48px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {c.title || 'New Conversation'}
                  </button>
                  <div className="conv-actions" style={{ position: 'absolute', right: '4px', display: 'flex', gap: '4px' }}>
                    <button className="icon-btn-sm" onClick={(e) => startEdit(e, c)} title="Rename"><Edit2 size={12} /></button>
                    <button className="icon-btn-sm text-danger" onClick={(e) => handleDelete(e, c.id)} title="Delete"><Trash2 size={12} /></button>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="chat-container" style={{ flex: 1 }}>
        {messages.length === 0 ? (
          <div className="empty-state" style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <Bot size={48} />
            <h3>Hello! I'm ImpetusAI</h3>
            <p>I can help with IT issues, HR policy questions, and more.</p>
            <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginTop: 20, flexWrap: 'wrap' }}>
              {['My VPN is not working', 'What is the leave policy?', 'How to request WFH?'].map(q => (
                <button key={q} className="btn btn-secondary btn-sm" onClick={() => { setInput(q); }}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map(m => (
              <div key={m.id} className={`chat-msg ${m.role}`}>
                <div className="chat-avatar">
                  {m.role === 'user' ? initials : <Bot size={16} />}
                </div>
                <div>
                  <div className="chat-bubble">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                  </div>
                  {m.agent_name && (
                    <div className="chat-agent-tag">
                      <Shield size={10} /> {m.agent_name.replace('_', ' ')}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {sending && (
              <div className="chat-typing">
                <span /><span /><span />
              </div>
            )}
            <div ref={messagesEnd} />
          </div>
        )}

        <div className="chat-input-area">
          <textarea
            className="chat-input"
            rows={1}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about IT issues, HR policies, or anything work-related…"
          />
          <button className="chat-send-btn" onClick={handleSend} disabled={sending || !input.trim()}>
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Tickets Page
   ═══════════════════════════════════════════════════════════════ */
const SLA_LABELS = { P1: '24h', P2: '2 days', P3: '7 days', P4: '14 days' };

function slaBadge(status) {
  const colors = { on_track: '#10b981', at_risk: '#f59e0b', breached: '#ef4444', met: '#6366f1' };
  const labels = { on_track: 'On Track', at_risk: 'At Risk', breached: 'Breached', met: 'Met' };
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, fontWeight: 600,
      color: colors[status] || '#64748b', background: (colors[status] || '#64748b') + '20',
      padding: '2px 8px', borderRadius: 12 }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: colors[status] || '#64748b' }} />
      {labels[status] || status}
    </span>
  );
}

function AssigneeSearch({ assignees, value, onChange }) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  const current = assignees.find(a => a.id === value);
  const filtered = query
    ? assignees.filter(a => a.full_name.toLowerCase().includes(query.toLowerCase()) || a.title.toLowerCase().includes(query.toLowerCase()))
    : assignees;

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', borderRadius: 8,
        border: `1px solid ${open ? 'var(--accent)' : 'var(--border-color)'}`, background: 'var(--bg-input)', cursor: 'text' }}
        onClick={() => setOpen(true)}>
        {current && !open ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 24, height: 24, borderRadius: '50%', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 700, color: '#fff', flexShrink: 0 }}>
              {current.full_name.split(' ').map(w=>w[0]).join('').slice(0,2)}
            </div>
            <div>
              <div style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>{current.full_name}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{current.title}</div>
            </div>
            <button style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 14 }}
              onClick={e => { e.stopPropagation(); onChange(null); setQuery(''); }}>✕</button>
          </div>
        ) : (
          <input autoFocus={open} value={query} onChange={e => { setQuery(e.target.value); setOpen(true); }}
            placeholder="Search by name or role…"
            style={{ flex: 1, background: 'none', border: 'none', outline: 'none', color: 'var(--text-primary)', fontSize: 13 }} />
        )}
      </div>
      {open && (
        <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, marginTop: 4, background: '#1e293b',
          border: '1px solid var(--border-color)', borderRadius: 8, zIndex: 100, maxHeight: 200, overflowY: 'auto',
          boxShadow: '0 8px 24px rgba(0,0,0,0.4)' }}>
          {filtered.length === 0 ? (
            <div style={{ padding: '10px 14px', fontSize: 13, color: 'var(--text-muted)' }}>No agents found</div>
          ) : filtered.map(a => (
            <div key={a.id} onClick={() => { onChange(a.id); setQuery(''); setOpen(false); }}
              style={{ padding: '10px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10,
                background: value === a.id ? 'var(--accent-glow)' : 'transparent' }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-glass-hover)'}
              onMouseLeave={e => e.currentTarget.style.background = value === a.id ? 'var(--accent-glow)' : 'transparent'}>
              <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, color: '#fff', flexShrink: 0 }}>
                {a.full_name.split(' ').map(w=>w[0]).join('').slice(0,2)}
              </div>
              <div>
                <div style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>{a.full_name}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{a.title}</div>
              </div>
              {value === a.id && <span style={{ marginLeft: 'auto', color: 'var(--accent)', fontSize: 14 }}>✓</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function TicketDetailDrawer({ ticketId, onClose, onUpdated, userRole }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [resolution, setResolution] = useState('');
  const [assignees, setAssignees] = useState([]);
  const [selectedAssignee, setSelectedAssignee] = useState(null); // id or null = keep current

  useEffect(() => {
    if (!ticketId) return;
    setLoading(true);
    setNewStatus(''); setResolution(''); setSelectedAssignee(null);
    Promise.all([
      api.getTicket(ticketId),
      api.getTicketAssignees(),
    ]).then(([d, a]) => { setDetail(d); setAssignees(a); setLoading(false); })
      .catch(() => setLoading(false));
  }, [ticketId]);

  const canUpdate = ['it_agent', 'admin', 'hr_admin'].includes(userRole);

  const handleUpdate = async () => {
    if (!newStatus && selectedAssignee === null) return;
    setUpdating(true);
    try {
      const payload = {};
      if (newStatus) { payload.status = newStatus; if (resolution) payload.resolution = resolution; }
      if (selectedAssignee !== null) payload.assigned_to = selectedAssignee;
      await api.updateTicket(ticketId, payload);
      const updated = await api.getTicket(ticketId);
      setDetail(updated);
      setNewStatus(''); setResolution(''); setSelectedAssignee(null);
      onUpdated && onUpdated();
    } catch {} finally { setUpdating(false); }
  };

  const fmt = (dt) => dt ? new Date(dt).toLocaleString() : '—';
  const fmtDeadline = (dt) => dt ? new Date(dt).toLocaleString() : '—';

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex' }} onClick={onClose}>
      {/* Backdrop */}
      <div style={{ flex: 1, background: 'rgba(0,0,0,0.5)' }} />
      {/* Drawer */}
      <div style={{ width: 520, background: 'var(--bg-secondary)', borderLeft: '1px solid var(--border-color)',
        overflowY: 'auto', display: 'flex', flexDirection: 'column' }}
        onClick={e => e.stopPropagation()}>
        {loading ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="spinner" />
          </div>
        ) : !detail ? (
          <div style={{ padding: 24, color: 'var(--text-muted)' }}>Ticket not found.</div>
        ) : (
          <>
            {/* Header */}
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4, fontFamily: 'monospace' }}>{detail.ticket_number}</div>
                <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3, maxWidth: 380 }}>{detail.title}</div>
              </div>
              <button className="btn btn-ghost btn-sm" onClick={onClose} style={{ marginLeft: 8, flexShrink: 0 }}>✕</button>
            </div>

            {/* Badges row */}
            <div style={{ padding: '12px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <span className={`badge badge-${detail.priority.toLowerCase()}`}>{detail.priority}</span>
              <span className={`badge badge-${detail.status.replace('_','-')}`}>{detail.status.replace('_',' ')}</span>
              <span className="badge badge-it">{detail.category}</span>
              {slaBadge(detail.sla_status)}
            </div>

            <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 24 }}>
              {/* Description */}
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>Description</div>
                <div style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6, background: 'var(--bg-glass)', padding: 12, borderRadius: 8 }}>{detail.description}</div>
              </div>

              {/* SLA */}
              <div style={{ background: 'var(--bg-glass)', borderRadius: 10, padding: 16 }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>SLA — Target: {SLA_LABELS[detail.priority]}</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>Deadline</div>
                    <div style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>{fmtDeadline(detail.sla_deadline)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>Status</div>
                    {slaBadge(detail.sla_status)}
                  </div>
                  {detail.sla_hours_remaining != null && (
                    <div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>Time Remaining</div>
                      <div style={{ fontSize: 13, color: detail.sla_hours_remaining < 0 ? '#ef4444' : 'var(--text-primary)', fontWeight: 500 }}>
                        {detail.sla_hours_remaining < 0 ? `${Math.abs(detail.sla_hours_remaining).toFixed(1)}h overdue` : `${detail.sla_hours_remaining.toFixed(1)}h`}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Assignee */}
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>Assignment</div>
                {detail.assignee_name ? (
                  <div style={{ background: 'var(--bg-glass)', borderRadius: 10, padding: 14 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: detail.assignee_manager_name ? 10 : 0 }}>
                      <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700, color: '#fff', flexShrink: 0 }}>
                        {detail.assignee_name.split(' ').map(w => w[0]).join('').slice(0,2)}
                      </div>
                      <div>
                        <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{detail.assignee_name}</div>
                        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{detail.assignee_title} · {detail.assignee_email}</div>
                      </div>
                    </div>
                    {detail.assignee_manager_name && (
                      <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{ width: 26, height: 26, borderRadius: '50%', background: '#4f46e5', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, color: '#fff', flexShrink: 0 }}>
                          {detail.assignee_manager_name.split(' ').map(w => w[0]).join('').slice(0,2)}
                        </div>
                        <div>
                          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Reports to: <strong>{detail.assignee_manager_name}</strong></div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{detail.assignee_manager_email}</div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div style={{ fontSize: 13, color: 'var(--text-muted)', fontStyle: 'italic' }}>Unassigned</div>
                )}
              </div>

              {/* Reporter */}
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>Reported By</div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{detail.creator_name} <span style={{ color: 'var(--text-muted)' }}>({detail.creator_email})</span></div>
              </div>

              {/* Timeline */}
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>Timeline</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Created: <span style={{ color: 'var(--text-primary)' }}>{fmt(detail.created_at)}</span></div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Updated: <span style={{ color: 'var(--text-primary)' }}>{fmt(detail.updated_at)}</span></div>
                  {detail.resolved_at && <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Resolved: <span style={{ color: '#10b981' }}>{fmt(detail.resolved_at)}</span></div>}
                </div>
              </div>

              {/* Resolution */}
              {detail.resolution && (
                <div>
                  <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>Resolution</div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)', background: 'var(--bg-glass)', padding: 12, borderRadius: 8 }}>{detail.resolution}</div>
                </div>
              )}

              {/* Update ticket (IT agents/admins only) */}
              {canUpdate && !['resolved','closed'].includes(detail.status) && (
                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: 20 }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>Update Ticket</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

                    {/* Reassign */}
                    <div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>Reassign to</div>
                      <AssigneeSearch
                        assignees={assignees}
                        value={selectedAssignee ?? detail.assignee_id}
                        onChange={setSelectedAssignee}
                      />
                    </div>

                    {/* Status */}
                    <div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>Change status</div>
                      <select value={newStatus} onChange={e => setNewStatus(e.target.value)}
                        style={{ width: '100%', padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border-color)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: 13 }}>
                        <option value="">— Keep current —</option>
                        <option value="in_progress">In Progress</option>
                        <option value="waiting">Waiting on User</option>
                        <option value="resolved">Resolved</option>
                        <option value="closed">Closed</option>
                      </select>
                    </div>

                    {['resolved','closed'].includes(newStatus) && (
                      <textarea value={resolution} onChange={e => setResolution(e.target.value)}
                        placeholder="Resolution notes (optional)"
                        rows={3}
                        style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border-color)', background: 'var(--bg-input)', color: 'var(--text-primary)', fontSize: 13, resize: 'vertical' }} />
                    )}

                    <button className="btn btn-primary btn-sm" onClick={handleUpdate}
                      disabled={(!newStatus && selectedAssignee === null) || updating}>
                      {updating ? 'Saving…' : 'Save Changes'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function TicketsPage() {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  useEffect(() => { loadTickets(); }, [filter]);

  const loadTickets = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter) params.status = filter;
      setTickets(await api.getTickets(params));
    } catch {} finally { setLoading(false); }
  };

  const priorityBadge = (p) => <span className={`badge badge-${p.toLowerCase()}`}>{p}</span>;
  const statusBadge = (s) => <span className={`badge badge-${s.replace('_', '-')}`}>{s.replace('_', ' ')}</span>;

  return (
    <div className="page-container">
      {selectedTicketId && (
        <TicketDetailDrawer
          ticketId={selectedTicketId}
          userRole={user?.role}
          onClose={() => setSelectedTicketId(null)}
          onUpdated={loadTickets}
        />
      )}

      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">IT Tickets</h1>
          <p className="page-subtitle">Track and manage IT support requests</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['', 'open', 'in_progress', 'resolved'].map(f => (
            <button key={f} className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setFilter(f)}>
              {f ? f.replace('_', ' ') : 'All'}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{tickets.length}</div>
          <div className="stat-label">Total Tickets</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{tickets.filter(t => t.status === 'open').length}</div>
          <div className="stat-label">Open</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{tickets.filter(t => t.status === 'in_progress').length}</div>
          <div className="stat-label">In Progress</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{tickets.filter(t => t.status === 'resolved').length}</div>
          <div className="stat-label">Resolved</div>
        </div>
      </div>

      {/* Ticket list */}
      {loading ? (
        <div className="loading"><div className="spinner" /></div>
      ) : tickets.length === 0 ? (
        <div className="empty-state">
          <Ticket size={48} />
          <h3>No tickets yet</h3>
          <p>Tickets will appear here when created via the AI chat.</p>
        </div>
      ) : (
        <div className="tickets-grid">
          {/* Header */}
          <div className="ticket-row" style={{ background: 'transparent', cursor: 'default', fontWeight: 600, fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', gridTemplateColumns: '110px 1fr 110px 80px 100px 90px 90px' }}>
            <div>Ticket #</div>
            <div>Title</div>
            <div>Category</div>
            <div>Priority</div>
            <div>Status</div>
            <div>SLA</div>
            <div>Created</div>
          </div>
          {tickets.map(t => (
            <div key={t.id} className="ticket-row" style={{ gridTemplateColumns: '110px 1fr 110px 80px 100px 90px 90px', cursor: 'pointer' }}
              onClick={() => setSelectedTicketId(t.id)}>
              <div style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--accent-light)', fontWeight: 600 }}>{t.ticket_number || `INC-${t.id.slice(0,8).toUpperCase()}`}</div>
              <div>
                <div className="ticket-title">{t.title}</div>
                {t.assigned_to_name && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>👤 {t.assigned_to_name}</div>}
              </div>
              <div><span className="badge badge-it">{t.category}</span></div>
              <div>{priorityBadge(t.priority)}</div>
              <div>{statusBadge(t.status)}</div>
              <div>{t.sla_status ? slaBadge(t.sla_status) : '—'}</div>
              <div className="ticket-date">{new Date(t.created_at).toLocaleDateString()}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Workplace Governance Page
   ═══════════════════════════════════════════════════════════════ */
const ALLOWED_DOC_TYPES = {
  admin: ['hr_policy', 'it_runbook', 'sop', 'general'],
  hr_admin: ['hr_policy'],
  it_agent: ['it_runbook', 'sop', 'general'],
};

function WorkplaceGovernancePage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('requests');
  const [documents, setDocuments] = useState([]);
  const [requests, setRequests] = useState([]);
  const [stats, setStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [docType, setDocType] = useState(() => {
    const allowed = ALLOWED_DOC_TYPES[user?.role] || ['hr_policy'];
    return allowed[0];
  });
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadDocs();
    loadRequests();
    loadStats();
  }, []);

  const loadDocs = async () => { try { setDocuments(await api.getDocuments()); } catch {} };
  const loadRequests = async () => { try { setRequests(await api.getAccessRequests()); } catch {} };
  const loadStats = async () => { try { setStats(await api.getGovernanceStats()); } catch {} };

  const handleProcessRequest = async (id, status) => {
    const comment = prompt(`Enter ${status} comment (optional):`);
    try {
      await api.processAccessRequest(id, status, comment);
      loadRequests();
      loadStats();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const handleUpload = async (file) => {
    if (!file) return;
    setUploading(true);
    try {
      await api.uploadDocument(file, docType);
      loadDocs();
    } catch (err) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this document?')) return;
    try { await api.deleteDocument(id); loadDocs(); } catch {}
  };

  const onDrop = (e) => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files[0]); };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Admin Panel</h1>
        <p className="page-subtitle">Manage HR policy documents and knowledge base</p>
      </div>

      {/* Doc type selector */}
      <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 10 }}>
        <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)' }}>Document Type:</label>
        <select
          className="input"
          style={{ width: 'auto', fontSize: 13, padding: '6px 12px' }}
          value={docType}
          onChange={e => setDocType(e.target.value)}
        >
          {(ALLOWED_DOC_TYPES[user?.role] || ['hr_policy']).map(t => (
            <option key={t} value={t}>{t.replace('_', ' ')}</option>
          ))}
        </select>
      </div>

      {/* Upload zone */}
      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <Upload size={32} />
        <p style={{ fontWeight: 600, marginTop: 8 }}>
          {uploading ? 'Uploading & Indexing…' : 'Drop files here or click to upload'}
        </p>
        <p style={{ fontSize: 13 }}>Supports PDF, DOCX, MD, TXT files (max 50MB)</p>
        <input ref={fileInputRef} type="file" hidden accept=".pdf,.docx,.md,.txt" onChange={e => handleUpload(e.target.files[0])} />
      </div>

      {/* Where to upload info */}
      <div className="card" style={{ marginBottom: 20, borderColor: 'rgba(99, 102, 241, 0.2)' }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
          <AlertCircle size={18} style={{ color: 'var(--accent-light)', flexShrink: 0, marginTop: 2 }} />
          <div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Where to upload real HR policies</div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Place your organization's PDF/DOCX files in <code style={{ background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: 4 }}>backend/uploads/hr_policies/</code> or use this upload panel.
              Documents are automatically parsed, chunked, and indexed into the AI knowledge base. If your organization has an API to fetch policy documents, it can be integrated in Phase 2.
            </div>
          </div>
        </div>
      </div>

      {/* Document list */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Uploaded Documents ({documents.length})</div>
        </div>
        {documents.length === 0 ? (
          <div className="empty-state" style={{ padding: 30 }}>
            <FileText size={32} />
            <h3>No documents uploaded</h3>
            <p>Demo policies are pre-loaded in the knowledge base.</p>
          </div>
        ) : (
          <div className="doc-grid">
            {documents.map(d => (
              <div key={d.id} className="doc-row">
                <div>
                  <div style={{ fontWeight: 500, fontSize: 14 }}>{d.original_name}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{d.chunk_count} chunks indexed</div>
                </div>
                <div><span className="badge badge-hr">{d.doc_type}</span></div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{formatSize(d.file_size)}</div>
                <div>
                  <button className="btn btn-ghost btn-sm" onClick={() => handleDelete(d.id)}>
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Dashboard Page
   ═══════════════════════════════════════════════════════════════ */
function DashboardPage() {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [convCount, setConvCount] = useState(0);
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  useEffect(() => {
    api.getTickets().then(setTickets).catch(() => {});
    api.getConversations().then(c => setConvCount(c.length)).catch(() => {});
  }, []);

  return (
    <div className="page-container">
      {selectedTicketId && (
        <TicketDetailDrawer
          ticketId={selectedTicketId}
          userRole={user?.role}
          onClose={() => setSelectedTicketId(null)}
          onUpdated={() => api.getTickets().then(setTickets).catch(() => {})}
        />
      )}

      <div className="page-header">
        <h1 className="page-title">Welcome, {user?.full_name?.split(' ')[0]} 👋</h1>
        <p className="page-subtitle">Here's your ImpetusAI dashboard overview</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{convCount}</div>
          <div className="stat-label">Conversations</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{tickets.length}</div>
          <div className="stat-label">Total Tickets</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{tickets.filter(t => t.status === 'open').length}</div>
          <div className="stat-label">Open Tickets</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{tickets.filter(t => t.priority === 'P1' || t.priority === 'P2').length}</div>
          <div className="stat-label">High Priority</div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Quick Actions</div>
        </div>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', padding: '0 20px 20px' }}>
          <NavLink to="/chat" className="btn btn-primary"><MessageSquare size={16} /> Start AI Chat</NavLink>
          <NavLink to="/tickets" className="btn btn-secondary"><Ticket size={16} /> View Tickets</NavLink>
          <NavLink to="/leave" className="btn btn-secondary"><Calendar size={16} /> Leave</NavLink>
          <NavLink to="/timesheet" className="btn btn-secondary"><Clock size={16} /> Timesheet</NavLink>
          {(user?.role === 'admin' || user?.role === 'hr_admin') && (
            <NavLink to="/admin" className="btn btn-secondary"><Shield size={16} /> Workplace Governance</NavLink>
          )}
        </div>
      </div>

      {/* Access Request section for regular employees */}
      {user?.role === 'employee' && (
        <div className="card" style={{ marginBottom: 20, background: 'linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%)', border: '1px solid #cce3ff' }}>
          <div className="card-header">
            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <Shield size={20} color="var(--primary-color)" /> Elevate Your Workplace Access
            </div>
          </div>
          <div style={{ padding: '0 20px 20px' }}>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 15 }}>
              Need to manage HR policies or access administrative tools? Submit an access request for the Workplace Governance board to review.
            </p>
            <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end' }}>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>Target Role</label>
                <select id="request-role" className="input" style={{ background: 'white' }}>
                  <option value="hr_admin">HR Administrator (Document & Policy Management)</option>
                  <option value="admin">System Administrator (Full Platform Access)</option>
                </select>
              </div>
              <div style={{ flex: 2 }}>
                <label style={{ fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>Business Justification</label>
                <input id="request-justification" className="input" placeholder="e.g. Required for upcoming policy audit..." style={{ background: 'white' }} />
              </div>
              <button className="btn btn-primary" onClick={async () => {
                const role = document.getElementById('request-role').value;
                const justification = document.getElementById('request-justification').value;
                if (!justification || justification.length < 10) return alert('Please provide a valid justification (min 10 chars).');
                try {
                  await api.requestAccess(role, justification);
                  alert('Access request submitted successfully! Your request is now pending governance review.');
                  document.getElementById('request-justification').value = '';
                } catch (err) {
                  alert(err.message);
                }
              }}>Submit Request</button>
            </div>
          </div>
        </div>
      )}

      {/* Recent tickets */}
      {tickets.length > 0 && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">Recent Tickets</div>
            <NavLink to="/tickets" className="btn btn-ghost btn-sm">View All <ChevronRight size={14} /></NavLink>
          </div>
          <div className="tickets-grid">
            {/* Header */}
            <div className="ticket-row" style={{ background: 'transparent', cursor: 'default', fontWeight: 600, fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', gridTemplateColumns: '110px 1fr 80px 100px 130px 80px' }}>
              <div>Ticket #</div>
              <div>Title</div>
              <div>Priority</div>
              <div>Status</div>
              <div>Assigned To</div>
              <div>Created</div>
            </div>
            {tickets.slice(0, 5).map(t => (
              <div key={t.id} className="ticket-row" style={{ gridTemplateColumns: '110px 1fr 80px 100px 130px 80px', cursor: 'pointer' }}
                onClick={() => setSelectedTicketId(t.id)}>
                <div style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--accent-light)', fontWeight: 600 }}>
                  {t.ticket_number || `INC-${t.id.slice(0,8).toUpperCase()}`}
                </div>
                <div>
                  <div className="ticket-title">{t.title}</div>
                </div>
                <div><span className={`badge badge-${t.priority.toLowerCase()}`}>{t.priority}</span></div>
                <div><span className={`badge badge-${t.status.replace('_', '-')}`}>{t.status.replace('_', ' ')}</span></div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{t.assigned_to_name || <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Unassigned</span>}</div>
                <div className="ticket-date">{new Date(t.created_at).toLocaleDateString()}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   User Management Page (admin only)
   ═══════════════════════════════════════════════════════════════ */
function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    email: '', password: '', full_name: '', department: 'General', role: 'employee',
  });
  const [createError, setCreateError] = useState('');

  useEffect(() => { loadUsers(); }, []);

  const loadUsers = async () => {
    setLoading(true);
    try { setUsers(await api.fetchUsers()); } catch {}
    finally { setLoading(false); }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.updateUser(userId, { role: newRole });
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err) { alert(`Failed to update role: ${err.message}`); }
  };

  const handleToggleActive = async (u) => {
    const newStatus = u.registration_status === 'active' ? 'suspended' : 'active';
    try {
      await api.updateUser(u.id, { registration_status: newStatus });
      setUsers(prev => prev.map(x => x.id === u.id
        ? { ...x, registration_status: newStatus, is_active: newStatus === 'active' } : x));
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setCreateError('');
    try {
      const newUser = await api.createUser(createForm);
      setUsers(prev => [newUser, ...prev]);
      setShowCreateModal(false);
      setCreateForm({ email: '', password: '', full_name: '', department: 'General', role: 'employee' });
    } catch (err) { setCreateError(err.message); }
  };

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">User Management</h1>
          <p className="page-subtitle">Manage platform users, roles, and access</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          <Plus size={16} /> Add User
        </button>
      </div>

      {loading ? (
        <div className="loading"><div className="spinner" /></div>
      ) : (
        <div className="card">
          <div className="card-header">
            <div className="card-title">All Users ({users.length})</div>
          </div>
          <div className="tickets-grid">
            <div className="ticket-row" style={{ background: 'transparent', cursor: 'default', fontWeight: 600, fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              <div>Name / Email</div>
              <div>Department</div>
              <div>Role</div>
              <div>Status</div>
              <div>Actions</div>
            </div>
            {users.map(u => (
              <div key={u.id} className="ticket-row">
                <div>
                  <div style={{ fontWeight: 500, fontSize: 14 }}>{u.full_name}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{u.email}</div>
                </div>
                <div style={{ fontSize: 13 }}>{u.department}</div>
                <div>
                  <select
                    className="input"
                    style={{ fontSize: 12, padding: '4px 8px', width: 'auto' }}
                    value={u.role}
                    onChange={e => handleRoleChange(u.id, e.target.value)}
                  >
                    {['employee', 'it_agent', 'hr_admin', 'admin'].map(r => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <span className={`badge badge-${u.registration_status === 'active' ? 'resolved' : 'p1'}`}>
                    {u.registration_status}
                  </span>
                </div>
                <div>
                  <button
                    className={`btn btn-sm ${u.registration_status === 'active' ? 'btn-secondary' : 'btn-primary'}`}
                    onClick={() => handleToggleActive(u)}
                  >
                    {u.registration_status === 'active' ? 'Suspend' : 'Activate'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: 480, maxWidth: '90vw' }}>
            <div className="card-header">
              <div className="card-title">Add New User</div>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowCreateModal(false)}>✕</button>
            </div>
            {createError && <div className="error-toast" style={{ margin: '0 20px 12px' }}>{createError}</div>}
            <form onSubmit={handleCreateUser} style={{ padding: '0 20px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div className="input-group">
                <label>Full Name</label>
                <input className="input" required value={createForm.full_name}
                  onChange={e => setCreateForm(p => ({ ...p, full_name: e.target.value }))} />
              </div>
              <div className="input-group">
                <label>Email</label>
                <input className="input" type="email" required value={createForm.email}
                  onChange={e => setCreateForm(p => ({ ...p, email: e.target.value }))} />
              </div>
              <div className="input-group">
                <label>Password</label>
                <input className="input" type="password" required minLength={8} value={createForm.password}
                  onChange={e => setCreateForm(p => ({ ...p, password: e.target.value }))} />
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Department</label>
                  <input className="input" value={createForm.department}
                    onChange={e => setCreateForm(p => ({ ...p, department: e.target.value }))} />
                </div>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Role</label>
                  <select className="input" value={createForm.role}
                    onChange={e => setCreateForm(p => ({ ...p, role: e.target.value }))}>
                    {['employee', 'it_agent', 'hr_admin', 'admin'].map(r => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 4 }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create User</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Analytics Dashboard Page (admin, hr_admin, it_agent)
   ═══════════════════════════════════════════════════════════════ */
function AnalyticsDashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.fetchAnalytics()
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading"><div className="spinner" /></div>;
  if (error) return <div className="page-container"><div className="error-toast">{error}</div></div>;
  if (!data) return null;

  const maxDailyCount = Math.max(...(data.daily_volume?.map(d => d.count) || [1]), 1);
  const openTickets = data.tickets_by_status?.find(t => t.status === 'open')?.count ?? null;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Analytics Dashboard</h1>
        <p className="page-subtitle">Platform usage metrics and agent performance insights</p>
      </div>

      {/* Stat cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{data.messages_all_time}</div>
          <div className="stat-label">Total Queries</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data.messages_last_7d}</div>
          <div className="stat-label">Queries (Last 7d)</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data.messages_last_30d}</div>
          <div className="stat-label">Queries (Last 30d)</div>
        </div>
        {openTickets !== null && (
          <div className="stat-card">
            <div className="stat-value">{openTickets}</div>
            <div className="stat-label">Open Tickets</div>
          </div>
        )}
      </div>

      {/* Agent Performance */}
      {data.by_agent?.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-header"><div className="card-title">Agent Performance</div></div>
          <div className="tickets-grid">
            <div className="ticket-row" style={{ background: 'transparent', cursor: 'default', fontWeight: 600, fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              <div>Agent</div><div>Messages</div><div style={{ color: '#22c55e' }}>Positive</div><div style={{ color: '#ef4444' }}>Negative</div><div>Avg Score</div>
            </div>
            {data.by_agent.map(a => (
              <div key={a.agent_name} className="ticket-row">
                <div style={{ fontWeight: 500 }}>{a.agent_name.replace(/_/g, ' ')}</div>
                <div>{a.message_count}</div>
                <div style={{ color: '#22c55e' }}>{a.positive_feedback}</div>
                <div style={{ color: '#ef4444' }}>{a.negative_feedback}</div>
                <div>{a.avg_feedback_score !== null ? a.avg_feedback_score.toFixed(2) : '—'}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Daily Volume — CSS bar chart */}
      {data.daily_volume?.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-header"><div className="card-title">Daily Message Volume (Last 30 Days)</div></div>
          <div style={{ padding: '12px 20px 20px', overflowX: 'auto' }}>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 3, height: 120, minWidth: data.daily_volume.length * 18 }}>
              {data.daily_volume.map(d => (
                <div
                  key={d.date}
                  title={`${d.date}: ${d.count} message${d.count !== 1 ? 's' : ''}`}
                  style={{
                    flex: 1, minWidth: 12,
                    height: `${Math.max(4, (d.count / maxDailyCount) * 100)}%`,
                    background: 'var(--gradient-primary)',
                    borderRadius: '3px 3px 0 0',
                    opacity: 0.8,
                    cursor: 'default',
                    transition: 'opacity 0.15s',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.opacity = 1; }}
                  onMouseLeave={e => { e.currentTarget.style.opacity = 0.8; }}
                />
              ))}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
              <span>{data.daily_volume[0]?.date}</span>
              <span>{data.daily_volume[data.daily_volume.length - 1]?.date}</span>
            </div>
          </div>
        </div>
      )}

      {/* Ticket breakdown */}
      {(data.tickets_by_status?.length > 0 || data.tickets_by_priority?.length > 0) && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
          {data.tickets_by_status?.length > 0 && (
            <div className="card">
              <div className="card-header"><div className="card-title">Tickets by Status</div></div>
              <div style={{ padding: '0 20px 16px' }}>
                {data.tickets_by_status.map(t => (
                  <div key={t.status} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: '1px solid var(--border-color)', fontSize: 14 }}>
                    <span>{t.status.replace(/_/g, ' ')}</span>
                    <span style={{ fontWeight: 600 }}>{t.count}</span>
                  </div>
                ))}
                {data.avg_resolution_hours !== null && data.avg_resolution_hours !== undefined && (
                  <div style={{ marginTop: 10, fontSize: 13, color: 'var(--text-muted)' }}>
                    Avg resolution: <strong>{data.avg_resolution_hours}h</strong>
                  </div>
                )}
              </div>
            </div>
          )}
          {data.tickets_by_priority?.length > 0 && (
            <div className="card">
              <div className="card-header"><div className="card-title">Tickets by Priority</div></div>
              <div style={{ padding: '0 20px 16px' }}>
                {data.tickets_by_priority.map(t => (
                  <div key={t.priority} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: '1px solid var(--border-color)', fontSize: 14, alignItems: 'center' }}>
                    <span><span className={`badge badge-${t.priority.toLowerCase()}`}>{t.priority}</span></span>
                    <span style={{ fontWeight: 600 }}>{t.count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Top Intents */}
      {data.top_intents?.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-header"><div className="card-title">Top Intent Categories</div></div>
          <div style={{ padding: '0 20px 16px' }}>
            {data.top_intents.map((item, i) => (
              <div key={item.intent} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 0', borderBottom: '1px solid var(--border-color)' }}>
                <span style={{ fontSize: 13, color: 'var(--text-muted)', width: 22 }}>#{i + 1}</span>
                <span style={{ flex: 1, fontSize: 14 }}>{item.intent.replace(/_/g, ' ')}</span>
                <span style={{ fontWeight: 600, fontSize: 14 }}>{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User breakdowns (admin only) */}
      {data.users_by_role && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
          <div className="card">
            <div className="card-header"><div className="card-title">Users by Role</div></div>
            <div style={{ padding: '0 20px 16px' }}>
              {data.users_by_role.map(r => (
                <div key={r.role} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: '1px solid var(--border-color)', fontSize: 14 }}>
                  <span>{r.role}</span>
                  <span style={{ fontWeight: 600 }}>{r.count}</span>
                </div>
              ))}
            </div>
          </div>
          {data.users_by_department && (
            <div className="card">
              <div className="card-header"><div className="card-title">Users by Department</div></div>
              <div style={{ padding: '0 20px 16px' }}>
                {data.users_by_department.map(d => (
                  <div key={d.department} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: '1px solid var(--border-color)', fontSize: 14 }}>
                    <span>{d.department}</span>
                    <span style={{ fontWeight: 600 }}>{d.count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Leave Page
   ═══════════════════════════════════════════════════════════════ */
function LeavePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [balance, setBalance] = useState(null);
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionError, setActionError] = useState('');

  const LEAVE_TYPE_NAMES = { CL: 'Casual Leave', EL: 'Earned Leave', SL: 'Sick Leave', CO: 'Comp-Off' };
  const LEAVE_COLORS = { CL: '#3b82f6', EL: '#10b981', SL: '#f59e0b', CO: '#8b5cf6' };

  const reload = () => {
    setLoading(true);
    Promise.all([api.getLeaveBalance(), api.getLeaveRequests()])
      .then(([bal, reqs]) => { setBalance(bal); setLeaves(reqs); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { reload(); }, []);

  const handleCancel = async (id) => {
    setActionError('');
    try {
      await api.updateLeaveRequest(id, { status: 'cancelled' });
      reload();
    } catch (e) {
      setActionError(e.message);
    }
  };

  const statusBadge = (s) => {
    const cfg = {
      pending: { color: '#f59e0b', bg: 'rgba(245,158,11,0.15)', label: 'Pending' },
      approved: { color: '#10b981', bg: 'rgba(16,185,129,0.15)', label: 'Approved' },
      rejected: { color: '#ef4444', bg: 'rgba(239,68,68,0.15)', label: 'Rejected' },
      cancelled: { color: '#6b7280', bg: 'rgba(107,114,128,0.15)', label: 'Cancelled' },
    }[s] || { color: '#6b7280', bg: 'rgba(107,114,128,0.12)', label: s };
    return (
      <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 12, background: cfg.bg, color: cfg.color }}>
        {cfg.label}
      </span>
    );
  };

  if (loading) return <div className="loading"><div className="spinner" /></div>;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Leave Management</h1>
        <p className="page-subtitle">View your leave balance and apply for leave via AI Chat</p>
      </div>

      {/* Balance Cards */}
      {balance && (
        <div className="stats-grid" style={{ marginBottom: 24 }}>
          {Object.entries(LEAVE_TYPE_NAMES).map(([code, name]) => {
            const total = { CL: 12, EL: 18, SL: 10, CO: 4 }[code] || 10;
            const avail = balance[code] ?? 0;
            const used = total - avail;
            const pct = Math.round((avail / total) * 100);
            return (
              <div key={code} className="stat-card" style={{ textAlign: 'left', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: LEAVE_COLORS[code] }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div>
                    <div className="stat-value" style={{ color: LEAVE_COLORS[code] }}>{avail}</div>
                    <div className="stat-label">{name}</div>
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>{used}/{total} used</div>
                </div>
                <div style={{ height: 4, background: 'var(--bg-secondary)', borderRadius: 2 }}>
                  <div style={{ height: '100%', width: `${pct}%`, background: LEAVE_COLORS[code], borderRadius: 2, transition: 'width 0.5s' }} />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Apply via chat CTA */}
      <div className="card" style={{ marginBottom: 20, border: '1px solid rgba(99,102,241,0.3)', background: 'rgba(99,102,241,0.05)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '16px 20px' }}>
          <Calendar size={28} color="var(--primary-color)" />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Apply for Leave via AI Chat</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Just type <em>"I need 2 days casual leave from Monday"</em> and the Leave Agent will handle the rest.
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => navigate('/chat')}>
            <MessageSquare size={15} /> Open Chat
          </button>
        </div>
      </div>

      {actionError && <div className="error-toast" style={{ marginBottom: 16 }}>{actionError}</div>}

      {/* Leave History */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Leave History</div>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{leaves.length} request{leaves.length !== 1 ? 's' : ''}</span>
        </div>
        {leaves.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
            No leave requests yet. Apply via AI Chat!
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                {['Reference', 'Type', 'From', 'To', 'Days', 'Reason', 'Status', ''].map(h => (
                  <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {leaves.map(lv => (
                <tr key={lv.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '12px 16px', fontSize: 12, fontWeight: 700, color: 'var(--primary-color)', fontFamily: 'monospace' }}>{lv.reference || '—'}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{ fontSize: 12, fontWeight: 600, color: LEAVE_COLORS[lv.leave_type] || 'var(--text-muted)' }}>
                      {LEAVE_TYPE_NAMES[lv.leave_type] || lv.leave_type}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: 12 }}>{new Date(lv.start_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</td>
                  <td style={{ padding: '12px 16px', fontSize: 12 }}>{new Date(lv.end_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</td>
                  <td style={{ padding: '12px 16px', fontSize: 13, fontWeight: 600, textAlign: 'center' }}>{lv.days}</td>
                  <td style={{ padding: '12px 16px', fontSize: 12, color: 'var(--text-muted)', maxWidth: 200 }}>{lv.reason || '—'}</td>
                  <td style={{ padding: '12px 16px' }}>{statusBadge(lv.status)}</td>
                  <td style={{ padding: '12px 16px' }}>
                    {lv.status === 'pending' && user?.role === 'employee' && (
                      <button className="btn btn-ghost" style={{ padding: '4px 8px', fontSize: 11, color: '#ef4444' }} onClick={() => handleCancel(lv.id)}>
                        Cancel
                      </button>
                    )}
                    {(user?.role === 'admin' || user?.role === 'hr_admin') && lv.status === 'pending' && (
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button className="btn btn-ghost" style={{ padding: '4px 8px', fontSize: 11, color: '#10b981' }}
                          onClick={() => api.updateLeaveRequest(lv.id, { status: 'approved' }).then(reload)}>
                          <CheckCircle size={13} /> Approve
                        </button>
                        <button className="btn btn-ghost" style={{ padding: '4px 8px', fontSize: 11, color: '#ef4444' }}
                          onClick={() => api.updateLeaveRequest(lv.id, { status: 'rejected' }).then(reload)}>
                          <XCircle size={13} /> Reject
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Timesheet Page
   ═══════════════════════════════════════════════════════════════ */
function TimesheetPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [timesheets, setTimesheets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  const reload = () => {
    setLoading(true);
    api.getTimesheets()
      .then(setTimesheets)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { reload(); }, []);

  const statusBadge = (s) => {
    const cfg = {
      submitted: { color: '#3b82f6', bg: 'rgba(59,130,246,0.15)', label: 'Submitted' },
      approved: { color: '#10b981', bg: 'rgba(16,185,129,0.15)', label: 'Approved' },
      rejected: { color: '#ef4444', bg: 'rgba(239,68,68,0.15)', label: 'Rejected' },
      draft: { color: '#6b7280', bg: 'rgba(107,114,128,0.12)', label: 'Draft' },
    }[s] || { color: '#6b7280', bg: 'rgba(107,114,128,0.12)', label: s };
    return (
      <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 12, background: cfg.bg, color: cfg.color }}>
        {cfg.label}
      </span>
    );
  };

  const weekLabel = (weekStart) => {
    const d = new Date(weekStart);
    const end = new Date(d); end.setDate(d.getDate() + 4);
    return `${d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })} – ${end.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}`;
  };

  if (loading) return <div className="loading"><div className="spinner" /></div>;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Timesheet</h1>
        <p className="page-subtitle">Log your weekly work hours via AI Chat</p>
      </div>

      {/* Submit via chat CTA */}
      <div className="card" style={{ marginBottom: 20, border: '1px solid rgba(16,185,129,0.3)', background: 'rgba(16,185,129,0.05)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '16px 20px' }}>
          <Clock size={28} color="#10b981" />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Log Hours via AI Chat</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Say <em>"I worked 8 hours on IMPETUS-AI project doing Development today"</em> and the Timesheet Agent will build your entry.
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => navigate('/chat')}>
            <MessageSquare size={15} /> Open Chat
          </button>
        </div>
      </div>

      {/* Timesheet list */}
      {timesheets.length === 0 ? (
        <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
          No timesheets submitted yet. Log your hours via AI Chat!
        </div>
      ) : (
        timesheets.map(ts => (
          <div key={ts.id} className="card" style={{ marginBottom: 16 }}>
            <div
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 20px', cursor: 'pointer' }}
              onClick={() => setExpanded(expanded === ts.id ? null : ts.id)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <Clock size={18} color="var(--text-muted)" />
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>Week of {weekLabel(ts.week_start)}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                    {ts.total_hours}h total · {ts.entries?.length || 0} entries
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                {statusBadge(ts.status)}
                {(user?.role === 'admin' || user?.role === 'hr_admin') && ts.status === 'submitted' && (
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button className="btn btn-ghost" style={{ padding: '4px 8px', fontSize: 11, color: '#10b981' }}
                      onClick={(e) => { e.stopPropagation(); api.updateTimesheet(ts.id, { status: 'approved' }).then(reload); }}>
                      <CheckCircle size={13} /> Approve
                    </button>
                    <button className="btn btn-ghost" style={{ padding: '4px 8px', fontSize: 11, color: '#ef4444' }}
                      onClick={(e) => { e.stopPropagation(); api.updateTimesheet(ts.id, { status: 'rejected' }).then(reload); }}>
                      <XCircle size={13} /> Reject
                    </button>
                  </div>
                )}
                <ChevronRight size={16} color="var(--text-muted)"
                  style={{ transform: expanded === ts.id ? 'rotate(90deg)' : 'none', transition: '0.2s' }} />
              </div>
            </div>

            {expanded === ts.id && ts.entries && ts.entries.length > 0 && (
              <div style={{ borderTop: '1px solid var(--border-color)', padding: '0 20px 16px' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12 }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                      {['Day', 'Project', 'Activity', 'Hours', 'Description'].map(h => (
                        <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {ts.entries.map((e, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '10px 12px', fontSize: 12, fontWeight: 600 }}>{e.day}</td>
                        <td style={{ padding: '10px 12px', fontSize: 12 }}>
                          <div style={{ fontWeight: 600 }}>{e.project_code}</div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{e.project_name}</div>
                        </td>
                        <td style={{ padding: '10px 12px', fontSize: 12 }}>{e.activity}</td>
                        <td style={{ padding: '10px 12px', fontSize: 13, fontWeight: 700, color: '#10b981' }}>{e.hours}h</td>
                        <td style={{ padding: '10px 12px', fontSize: 12, color: 'var(--text-muted)' }}>{e.description}</td>
                      </tr>
                    ))}
                    <tr style={{ background: 'var(--bg-secondary)' }}>
                      <td colSpan={3} style={{ padding: '10px 12px', fontSize: 12, fontWeight: 700 }}>Total</td>
                      <td style={{ padding: '10px 12px', fontSize: 14, fontWeight: 700, color: '#10b981' }}>{ts.total_hours}h</td>
                      <td />
                    </tr>
                  </tbody>
                </table>
                {ts.manager_comment && (
                  <div style={{ marginTop: 12, padding: '10px 14px', background: 'var(--bg-secondary)', borderRadius: 6, fontSize: 13 }}>
                    <strong>Manager Comment:</strong> {ts.manager_comment}
                  </div>
                )}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   App Shell with Sidebar
   ═══════════════════════════════════════════════════════════════ */
function AppShell({ children }) {
  const { user } = useAuth();

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="logo-icon">AI</div>
            <div>
              <div className="logo-text">ImpetusAI</div>
              <div className="logo-sub">Workplace Platform</div>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-title">Main</div>
          <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
            <LayoutDashboard size={18} /> Dashboard
          </NavLink>
          <NavLink to="/chat" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <MessageSquare size={18} /> AI Chat
          </NavLink>
          <NavLink to="/tickets" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Ticket size={18} /> IT Tickets
          </NavLink>

          <div className="nav-section-title">Self-Service</div>
          <NavLink to="/leave" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Calendar size={18} /> Leave
          </NavLink>
          <NavLink to="/timesheet" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Clock size={18} /> Timesheet
          </NavLink>

          {['admin', 'hr_admin', 'it_agent'].includes(user?.role) && (
            <>
              <div className="nav-section-title">Analytics</div>
              <NavLink to="/analytics" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <LayoutDashboard size={18} /> Analytics
              </NavLink>
            </>
          )}

          {(user?.role === 'admin' || user?.role === 'hr_admin') && (
            <>
              <div className="nav-section-title">Governance</div>
              <NavLink to="/admin" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <Shield size={18} /> Workplace Governance
              </NavLink>
            </>
          )}

          {user?.role === 'admin' && (
            <NavLink to="/admin/users" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <User size={18} /> User Management
            </NavLink>
          )}
        </nav>

        <div className="sidebar-footer">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px' }}>
            <div style={{ width: 32, height: 32, borderRadius: 'var(--radius-sm)', background: 'var(--gradient-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700, color: 'white' }}>
              {user?.full_name?.split(' ').map(w => w[0]).join('').slice(0, 2)}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user?.full_name}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{user?.department}</div>
            </div>
            <button className="btn btn-ghost" style={{ padding: 6 }} onClick={api.logout} title="Sign out">
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   App Router
   ═══════════════════════════════════════════════════════════════ */
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/*" element={
            <ProtectedRoute>
              <AppShell>
                <Routes>
                  <Route path="/" element={<DashboardPage />} />
                  <Route path="/chat" element={<ChatPage />} />
                  <Route path="/tickets" element={<TicketsPage />} />
                  <Route path="/leave" element={<LeavePage />} />
                  <Route path="/timesheet" element={<TimesheetPage />} />
                  <Route path="/admin" element={<AdminRoute><WorkplaceGovernancePage /></AdminRoute>} />
                  <Route path="/admin/users" element={<StrictAdminRoute><UserManagementPage /></StrictAdminRoute>} />
                  <Route path="/analytics" element={<AnalyticsRoute><AnalyticsDashboardPage /></AnalyticsRoute>} />
                </Routes>
              </AppShell>
            </ProtectedRoute>
          } />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
