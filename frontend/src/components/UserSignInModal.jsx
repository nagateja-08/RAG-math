import React, { useState, useEffect } from 'react';
import { User, LogIn, UserPlus, Check, X, Shield, History, ArrowRight } from 'lucide-react';

export default function UserSignInModal({ isOpen, onClose, currentUser, onUserChange }) {
  const [username, setUsername] = useState('');
  const [studentId, setStudentId] = useState('');
  const [knownUsers, setKnownUsers] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    try {
      const stored = localStorage.getItem('mathgpt_known_users');
      if (stored) {
        setKnownUsers(JSON.parse(stored));
      } else {
        const defaults = [
          { id: 'student_1', name: 'Student 1' },
          { id: 'teja', name: 'Teja' }
        ];
        setKnownUsers(defaults);
        localStorage.setItem('mathgpt_known_users', JSON.stringify(defaults));
      }
    } catch (e) {
      console.error(e);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSignIn = (e) => {
    e?.preventDefault();
    const cleanName = username.trim();
    if (!cleanName) {
      setError('Please enter a username or student name');
      return;
    }

    const cleanId = studentId.trim()
      ? studentId.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '_')
      : cleanName.toLowerCase().replace(/[^a-z0-9_-]/g, '_');

    const newUser = { id: cleanId, name: cleanName };

    // Update known users list
    const updated = [newUser, ...knownUsers.filter(u => u.id !== cleanId)].slice(0, 8);
    setKnownUsers(updated);
    localStorage.setItem('mathgpt_known_users', JSON.stringify(updated));
    localStorage.setItem('mathgpt_user', JSON.stringify(newUser));

    onUserChange(newUser);
    setUsername('');
    setStudentId('');
    setError('');
    onClose();
  };

  const handleSelectUser = (user) => {
    localStorage.setItem('mathgpt_user', JSON.stringify(user));
    onUserChange(user);
    onClose();
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 100,
      background: 'rgba(5, 8, 16, 0.85)', backdropFilter: 'blur(8px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem'
    }}>
      <div className="glass-bright" style={{
        width: '100%', maxWidth: '440px', borderRadius: '18px',
        border: '1px solid rgba(59, 130, 246, 0.3)', padding: '1.75rem',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(59, 130, 246, 0.2)',
        display: 'flex', flexDirection: 'column', gap: '1.25rem'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff'
            }}>
              <User size={18} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f1f5f9', margin: 0 }}>
                Student Sign In
              </h2>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                Track your personal learning progress &amp; inquiries
              </span>
            </div>
          </div>
          <button onClick={onClose} className="btn-ghost" style={{ padding: '0.35rem', borderRadius: 8 }}>
            <X size={16} />
          </button>
        </div>

        {/* Current Signed-In Badge */}
        {currentUser && (
          <div style={{
            background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.25)',
            borderRadius: 12, padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <div style={{
                width: 28, height: 28, borderRadius: '50%',
                background: 'linear-gradient(135deg, #2563eb, #6366f1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700, fontSize: '0.78rem', color: '#fff'
              }}>
                {currentUser.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>{currentUser.name}</div>
                <div style={{ fontSize: '0.7rem', color: '#93c5fd', fontFamily: 'JetBrains Mono, monospace' }}>ID: {currentUser.id}</div>
              </div>
            </div>
            <span style={{
              fontSize: '0.65rem', background: 'rgba(16, 185, 129, 0.15)',
              color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: 20, padding: '2px 8px', fontWeight: 700
            }}>Active</span>
          </div>
        )}

        {/* Sign In / Switch Form */}
        <form onSubmit={handleSignIn} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
              Student / Account Name
            </label>
            <input
              type="text"
              placeholder="e.g. Teja, Alex, Sarah"
              value={username}
              onChange={(e) => { setUsername(e.target.value); setError(''); }}
              className="chat-input"
              style={{ width: '100%', padding: '0.65rem 0.85rem', fontSize: '0.85rem' }}
              autoFocus
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.35rem' }}>
              User ID <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional)</span>
            </label>
            <input
              type="text"
              placeholder="Auto-generated if left empty"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              className="chat-input"
              style={{ width: '100%', padding: '0.65rem 0.85rem', fontSize: '0.85rem' }}
            />
          </div>

          {error && (
            <div style={{ fontSize: '0.75rem', color: '#f87171' }}>{error}</div>
          )}

          <button type="submit" className="btn-primary" style={{
            padding: '0.65rem', fontSize: '0.82rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.45rem', marginTop: '0.25rem'
          }}>
            <LogIn size={15} /> Sign In / Switch to Account
          </button>
        </form>

        {/* Recent Accounts Switcher */}
        {knownUsers.length > 0 && (
          <div style={{ borderTop: '1px solid var(--border)', paddingTop: '0.85rem' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <History size={12} /> Switch to Saved Account on this Device:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {knownUsers.map((u) => {
                const isSelected = currentUser?.id === u.id;
                return (
                  <button
                    key={u.id}
                    onClick={() => handleSelectUser(u)}
                    className="btn-ghost"
                    style={{
                      display: 'flex', alignItems: 'center', gap: '0.35rem',
                      padding: '0.3rem 0.65rem', fontSize: '0.75rem',
                      borderRadius: 8,
                      borderColor: isSelected ? 'rgba(59, 130, 246, 0.6)' : undefined,
                      background: isSelected ? 'rgba(59, 130, 246, 0.15)' : undefined,
                      color: isSelected ? '#fff' : 'var(--text-muted)'
                    }}
                  >
                    <span>{u.name}</span>
                    {isSelected && <Check size={12} style={{ color: '#60a5fa' }} />}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
