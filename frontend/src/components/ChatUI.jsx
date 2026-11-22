import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import {
  Send, Layers, Upload, CheckCircle2, AlertTriangle,
  BarChart3, Calculator, BookOpen, ArrowRight, Database,
  Network, Cpu, Atom, Infinity, Sigma, Camera, X, Image as ImageIcon, User
} from 'lucide-react';

import { askQuestion, uploadFile, healthCheck } from '../services/api';
import GraphExplorer from './GraphExplorer';
import ProgressDashboard from './ProgressDashboard';
import AssessmentModal from './AssessmentModal';
import UserSignInModal from './UserSignInModal';

/* ─── Floating Math Symbols Component ───────────────────────── */
const FLOAT_SYMBOLS = ['∫', '∑', '∂', '√', '∞', 'π', 'θ', 'Δ', '∇', 'λ', 'α', 'β', 'φ', 'Ω', '∮', '∏', 'dx', 'dy', '→', '≈'];

function FloatingSymbols() {
  const [symbols, setSymbols] = useState([]);
  useEffect(() => {
    const created = Array.from({ length: 18 }, (_, i) => ({
      id: i,
      symbol: FLOAT_SYMBOLS[Math.floor(Math.random() * FLOAT_SYMBOLS.length)],
      left: `${Math.random() * 100}%`,
      delay: `${Math.random() * 20}s`,
      duration: `${18 + Math.random() * 20}s`,
      size: `${0.9 + Math.random() * 1.4}rem`,
      opacity: 0.04 + Math.random() * 0.06,
    }));
    setSymbols(created);
  }, []);
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0" aria-hidden>
      {symbols.map(s => (
        <span key={s.id} className="math-float absolute font-mono select-none"
          style={{ left: s.left, bottom: '-5%', animationDelay: s.delay, animationDuration: s.duration, fontSize: s.size, opacity: s.opacity }}>
          {s.symbol}
        </span>
      ))}
    </div>
  );
}

/* ─── Quick Symbols ─────────────────────────────────────────── */
const QUICK_MATH_SYMBOLS = [
  { label: '∫ dx',   insert: '\\int f(x) \\, dx' },
  { label: 'd/dx',   insert: '\\frac{d}{dx}[f(x)]' },
  { label: '√x',     insert: '\\sqrt{x}' },
  { label: 'lim',    insert: '\\lim_{x \\to 0}' },
  { label: 'x²',     insert: 'x^2' },
  { label: '∑',      insert: '\\sum_{i=1}^{n}' },
  { label: 'π',      insert: '\\pi' },
  { label: 'θ',      insert: '\\theta' },
  { label: 'P(A|B)', insert: 'P(A|B) = \\frac{P(A \\cap B)}{P(B)}' },
];

/* ─── Math Content Formatter for KaTeX ───────────────────────── */
function formatMathContent(content) {
  if (!content) return '';
  let text = content;
  // Convert \[ ... \] to $$ ... $$ with generous double newlines
  text = text.replace(/\\\[([\s\S]*?)\\\]/g, (_, math) => `\n\n$$\n${math.trim()}\n$$\n\n`);
  // Convert \( ... \) to $ ... $
  text = text.replace(/\\\(([\s\S]*?)\\\)/g, (_, math) => `$${math.trim()}$`);
  // Convert unescaped [ \frac{...} ] blocks to $$ \frac{...} $$
  text = text.replace(/(?:^|\n)\s*\[\s*([^\]\n]+?(?:\\(?:frac|text|sum|int|sqrt|lim|cdot|times|alpha|beta|theta|pi|le|ge|partial)|[\^_=])[^\]\n]*?)\s*\](?:\s*\.?)(?=\n|$)/g, '\n\n$$\n$1\n$$\n\n');
  // Ensure clear spacing before every Step header so each step is cleanly separated
  text = text.replace(/([^\n])\n+(Step\s*\d+:)/gi, '$1\n\n**$2**');
  text = text.replace(/([^\n])\n+(\*\*Step\s*\d+:)/gi, '$1\n\n$2');
  return text;
}

/* ─── Starter Suggestions ───────────────────────────────────── */
const SUGGESTIONS = [
  { title: 'Explain Integration', prompt: 'Explain Integration and show how to evaluate a definite integral step-by-step.', tag: 'Calculus', icon: '∫' },
  { title: 'Differentiate & Verify', prompt: 'Find the derivative of f(x) = x^3 - 4x + sin(x) step-by-step.', tag: 'Derivatives', icon: 'd/dx' },
  { title: 'Solve Quadratic', prompt: 'Solve the equation x^2 - 5x + 6 = 0 step-by-step and show the roots.', tag: 'Algebra', icon: 'x²' },
  { title: 'Bayes Theorem', prompt: 'Explain Bayes Theorem with a concise numerical example.', tag: 'Probability', icon: 'P(A|B)' },
];

/* ─── NAV TABS ───────────────────────────────────────────────── */
const TABS = [
  { id: 'chat',     label: 'Math Chat',       icon: Atom },
  { id: 'graph',    label: 'Graph Explorer',  icon: Network },
  { id: 'progress', label: 'Learning',        icon: BarChart3 },
];

/* ─── Main Component ─────────────────────────────────────────── */
export default function ChatUI() {
  const [activeTab, setActiveTab]   = useState('chat');
  const [messages,  setMessages]    = useState([]);
  const [input,        setInput]        = useState('');
  const [loading,      setLoading]      = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);
  const [uploading,    setUploading]    = useState(false);
  const [uploadMsg,    setUploadMsg]    = useState(null);
  const [quizConcept,  setQuizConcept]  = useState(null);
  const [isQuizOpen,   setIsQuizOpen]   = useState(false);
  const [selectedImage, setSelectedImage] = useState(null); // { dataUrl, name, size }
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const stored = localStorage.getItem('mathgpt_user');
      if (stored) return JSON.parse(stored);
    } catch (e) {}
    return { id: 'student_1', name: 'Student 1' };
  });
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const fileInputRef   = useRef(null);
  const imageInputRef  = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    checkHealth();
    const t = setInterval(checkHealth, 20000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const checkHealth = async () => {
    try { setSystemHealth(await healthCheck()); }
    catch { setSystemHealth({ status: 'offline', neo4j_mode: 'offline', total_graph_nodes: 0 }); }
  };

  const processImageFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      setSelectedImage({
        dataUrl: e.target.result,
        name: file.name || 'Math problem screenshot',
        size: (file.size / 1024).toFixed(1) + ' KB',
      });
    };
    reader.readAsDataURL(file);
  };

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) processImageFile(file);
    if (imageInputRef.current) imageInputRef.current.value = '';
  };

  const handlePaste = (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        processImageFile(file);
        break;
      }
    }
  };

  const handleSend = async (textToSend = input) => {
    const q = textToSend.trim();
    const imagePayload = selectedImage?.dataUrl || null;
    if ((!q && !imagePayload) || loading) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: q || (imagePayload ? 'Solve the mathematical problem in this image.' : ''),
      image_url: imagePayload,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(p => [...p, userMsg]);
    setInput('');
    setSelectedImage(null);
    setLoading(true);

    try {
      const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }));
      const res = await askQuestion(q, history, currentUser.id, imagePayload);
      setMessages(p => [...p, {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        identified_concept: res.identified_concept,
        prerequisites: res.prerequisites,
        document_references: res.document_references,
        graph_context: res.graph_context,
        sympy_verification: res.sympy_verification,
        recommended_study_topics: res.recommended_study_topics,
        extracted_question: res.extracted_question,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } catch (err) {
      setMessages(p => [...p, {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: '⚠️ Unable to complete request. Please verify backend connection.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true); setUploadMsg(null);
    try {
      const res = await uploadFile(file);
      setUploadMsg({ type: 'success', text: `✓ Indexed ${res.chunks_added} chunks → FAISS. Synced ${res.concepts_extracted?.length ?? 0} concepts → Neo4j.` });
      checkHealth();
    } catch {
      setUploadMsg({ type: 'error', text: '✗ Upload failed. Ensure file is a valid .pdf or .txt.' });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const insertSymbol = sym => setInput(p => p + (p && !p.endsWith(' ') ? ' ' : '') + sym);

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100%', overflow: 'hidden', background: 'var(--bg-primary)', position: 'relative', flexDirection: 'column' }}>
      <FloatingSymbols />
      <AssessmentModal concept={quizConcept} isOpen={isQuizOpen}
        onClose={() => setIsQuizOpen(false)} onComplete={checkHealth} />
      <UserSignInModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)}
        currentUser={currentUser} onUserChange={setCurrentUser} />

      {/* ── HEADER ─────────────────────────────────────────────── */}
      <header className="glass" style={{
        position: 'relative', zIndex: 10, flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 1.5rem', height: '64px', borderBottom: '1px solid var(--border)',
        borderTop: 'none', borderLeft: 'none', borderRight: 'none',
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: 42, height: 42, borderRadius: 12, flexShrink: 0,
            background: 'linear-gradient(135deg, #4f8ef7 0%, #7c3aed 50%, #22d3ee 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 20px #4f8ef755, 0 4px 12px #00000055',
            fontSize: '1.3rem',
          }}>Σ</div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <span className="gradient-text" style={{ fontWeight: 800, fontSize: '1.15rem', letterSpacing: '-0.3px' }}>MathGPT</span>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav style={{ display: 'flex', gap: '0.25rem', background: 'rgba(10,14,26,0.6)', borderRadius: 12, padding: '4px', border: '1px solid var(--border)' }}>
          {TABS.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={isActive ? 'tab-active' : 'btn-ghost'}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.4rem',
                  padding: '0.4rem 0.9rem', borderRadius: 9, fontSize: '0.78rem',
                  fontWeight: 600, cursor: 'pointer', border: 'none',
                  transition: 'all 0.2s ease',
                  background: isActive ? undefined : 'transparent',
                  color: isActive ? '#fff' : 'var(--text-muted)',
                }}>
                <Icon size={13} />
                {tab.label}
              </button>
            );
          })}
        </nav>

        {/* Right: Upload & User Sign In Account */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept=".pdf,.txt,.md" className="hidden" />
          <button onClick={() => fileInputRef.current?.click()} disabled={uploading}
            className="btn-ghost" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', padding: '0.4rem 0.85rem' }}>
            <Upload size={13} style={{ color: 'var(--accent)' }} />
            {uploading ? 'Indexing…' : 'Upload PDF/TXT'}
          </button>

          {/* User Sign In / Profile Button */}
          <button
            onClick={() => setIsAuthModalOpen(true)}
            className="btn-ghost"
            style={{
              display: 'flex', alignItems: 'center', gap: '0.45rem',
              padding: '0.35rem 0.75rem', borderRadius: 10,
              fontSize: '0.78rem',
              borderColor: 'rgba(59, 130, 246, 0.4)',
              background: 'rgba(59, 130, 246, 0.1)',
            }}
            title={`Account: ${currentUser?.name} (${currentUser?.id}). Click to switch user.`}
          >
            <div style={{
              width: 22, height: 22, borderRadius: '50%',
              background: 'linear-gradient(135deg, #2563eb, #7c3aed)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontWeight: 700, fontSize: '0.68rem', color: '#fff'
            }}>
              {(currentUser?.name || 'S').charAt(0).toUpperCase()}
            </div>
            <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{currentUser?.name || 'Sign In'}</span>
          </button>
        </div>
      </header>

      {/* Upload Banner */}
      {uploadMsg && (
        <div style={{
          flexShrink: 0, padding: '0.5rem 1.5rem', fontSize: '0.75rem',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: uploadMsg.type === 'success' ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)',
          borderBottom: `1px solid ${uploadMsg.type === 'success' ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,
          color: uploadMsg.type === 'success' ? '#4ade80' : '#f87171',
          position: 'relative', zIndex: 9,
        }}>
          <span>{uploadMsg.text}</span>
          <button onClick={() => setUploadMsg(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1rem' }}>✕</button>
        </div>
      )}

      {/* ── CONTENT AREA ───────────────────────────────────────── */}
      <div style={{ flex: 1, overflow: 'hidden', position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column' }}>
        {activeTab === 'graph' ? (
          <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem' }}>
            <GraphExplorer
              onSelectConceptForChat={concept => { setActiveTab('chat'); handleSend(`Explain ${concept}, its mathematical prerequisites, formal definitions, and a step-by-step example.`); }}
              onStartQuiz={concept => { setQuizConcept(concept); setIsQuizOpen(true); }}
            />
          </div>
        ) : activeTab === 'progress' ? (
          <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem', maxWidth: 1100, margin: '0 auto', width: '100%' }}>
            <ProgressDashboard
              currentUser={currentUser}
              onOpenSignIn={() => setIsAuthModalOpen(true)}
              onSelectTopic={topic => { setActiveTab('chat'); handleSend(`Explain ${topic} in detail with step-by-step mathematical examples.`); }}
              onStartQuiz={topic => { setQuizConcept(topic); setIsQuizOpen(true); }}
            />
          </div>
        ) : (
          /* ── CHAT PANEL ─────────────────────────────────────── */
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            {/* Messages */}
            <div style={{
              flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column',
              gap: '1.25rem', maxWidth: 860, margin: '0 auto', width: '100%',
              justifyContent: messages.length === 0 ? 'center' : 'flex-start',
            }}>
              {messages.length === 0 && (
                <div style={{ textAlign: 'center', padding: '1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{
                    width: 52, height: 52, borderRadius: 14,
                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2))',
                    border: '1px solid rgba(59, 130, 246, 0.35)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1.6rem', color: '#60a5fa',
                    boxShadow: '0 0 25px rgba(59, 130, 246, 0.2)'
                  }}>
                    ∫
                  </div>
                  <div>
                    <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                      How can I help you with Mathematics today?
                    </h2>
                  </div>
                </div>
              )}

              {messages.map(msg => (
                <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                  {/* Role Label */}
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: '0.3rem', fontWeight: 600, letterSpacing: '0.5px', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    {msg.role === 'user' ? (
                      <><Cpu size={10} /> You</>
                    ) : (
                      <><Sigma size={10} style={{ color: 'var(--accent)' }} /> MathGPT Mentor</>
                    )}
                    <span style={{ fontWeight: 400, opacity: 0.6 }}>{msg.timestamp}</span>
                  </div>

                  {/* Bubble */}
                  <div className={msg.role === 'user' ? 'bubble-user' : 'bubble-assistant'}
                    style={{ maxWidth: '88%', padding: '1rem 1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    
                    {/* User uploaded math image */}
                    {msg.role === 'user' && msg.image_url && (
                      <div style={{ borderRadius: 10, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.25)', background: 'rgba(0,0,0,0.3)', maxWidth: 360 }}>
                        <img src={msg.image_url} alt="Uploaded math problem" style={{ width: '100%', maxHeight: 220, objectFit: 'contain', display: 'block' }} />
                      </div>
                    )}

                    {/* Extracted Math Question Banner on Assistant */}
                    {msg.role === 'assistant' && msg.extracted_question && (
                      <div style={{
                        background: 'rgba(59, 130, 246, 0.12)', border: '1px solid rgba(59, 130, 246, 0.3)',
                        borderRadius: 10, padding: '0.65rem 0.85rem', display: 'flex', flexDirection: 'column', gap: '0.35rem'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#93c5fd', fontSize: '0.75rem', fontWeight: 700 }}>
                          <Camera size={13} />
                          <span>Transcribed Math Problem from Image:</span>
                        </div>
                        <div style={{ color: '#f1f5f9', fontSize: '0.82rem', fontFamily: 'JetBrains Mono, monospace', background: 'rgba(10,14,26,0.6)', padding: '0.4rem 0.6rem', borderRadius: 6 }}>
                          <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                            {formatMathContent(msg.extracted_question)}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}

                    {msg.content && (
                      <div className="prose-math" style={{ fontSize: '0.875rem' }}>
                        <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                          {formatMathContent(msg.content)}
                        </ReactMarkdown>
                      </div>
                    )}

                    {/* Prerequisites Panel */}
                    {msg.role === 'assistant' && msg.prerequisites?.length > 0 && (
                      <div style={{
                        background: 'rgba(79,142,247,0.07)', border: '1px solid rgba(79,142,247,0.2)',
                        borderRadius: 10, padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem',
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 700, color: '#7cb4ff' }}>
                          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                            <BookOpen size={13} /> Prerequisites for {msg.identified_concept || 'this topic'} · Knowledge Graph
                          </span>
                          {msg.identified_concept && (
                            <button onClick={() => { setQuizConcept(msg.identified_concept); setIsQuizOpen(true); }}
                              style={{ background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: 7, padding: '3px 10px', fontSize: '0.7rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}>
                              Test My Readiness <ArrowRight size={10} />
                            </button>
                          )}
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                          {msg.prerequisites.map((p, i) => (
                            <span key={i} className="symbol-chip" onClick={() => { setQuizConcept(p.name); setIsQuizOpen(true); }} style={{ cursor: 'pointer' }}>
                              {p.name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* SymPy Verification Badge */}
                    {msg.role === 'assistant' && msg.sympy_verification && msg.sympy_verification.status !== 'not_applicable' && (
                      <div style={{
                        display: 'flex', alignItems: 'flex-start', gap: '0.6rem', fontSize: '0.75rem',
                        padding: '0.6rem 0.75rem', borderRadius: 10,
                        background: msg.sympy_verification.is_verified ? 'rgba(34,197,94,0.07)' : 'rgba(245,158,11,0.07)',
                        border: `1px solid ${msg.sympy_verification.is_verified ? 'rgba(34,197,94,0.3)' : 'rgba(245,158,11,0.3)'}`,
                        color: msg.sympy_verification.is_verified ? '#4ade80' : '#fbbf24',
                      }}>
                        {msg.sympy_verification.is_verified
                          ? <CheckCircle2 size={14} style={{ marginTop: 1, flexShrink: 0 }} />
                          : <AlertTriangle size={14} style={{ marginTop: 1, flexShrink: 0 }} />}
                        <div>
                          <div style={{ fontWeight: 700 }}>
                            {msg.sympy_verification.is_verified ? '✓ SymPy Independently Verified — Mathematically Valid' : 'SymPy: Could not be automatically verified'}
                          </div>
                          {msg.sympy_verification.latex_output && (
                            <div style={{ color: 'var(--text-muted)', marginTop: 2, fontFamily: 'JetBrains Mono, monospace' }}>
                              {msg.sympy_verification.latex_output}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Document Source Citations */}
                    {msg.role === 'assistant' && msg.document_references?.length > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.7rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border)', paddingTop: '0.5rem' }}>
                        <Database size={11} style={{ color: 'var(--accent)' }} /> Sources: {msg.document_references.join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Thinking Indicator */}
              {loading && (
                <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                  <div className="bubble-assistant" style={{ padding: '0.9rem 1.1rem', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <div className="dot-pulse" style={{ display: 'flex', gap: 5 }}>
                      <span /><span /><span />
                    </div>
                    <span>Solving…</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Starter Suggestions */}
            {messages.length === 0 && (
              <div style={{ padding: '0 1.5rem 0.75rem', maxWidth: 860, margin: '0 auto', width: '100%', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.6rem' }}>
                {SUGGESTIONS.map((s, idx) => (
                  <button key={idx} onClick={() => handleSend(s.prompt)}
                    className="glass-bright"
                    style={{
                      padding: '0.75rem', borderRadius: 12, textAlign: 'left', cursor: 'pointer',
                      display: 'flex', flexDirection: 'column', gap: '0.3rem', border: '1px solid var(--border)',
                      transition: 'all 0.2s ease', background: 'rgba(19,29,53,0.6)',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.background = 'rgba(79,142,247,0.08)'; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'rgba(19,29,53,0.6)'; }}>
                    <span style={{ fontSize: '1.1rem', marginBottom: '0.1rem' }}>{s.icon}</span>
                    <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{s.tag}</span>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-primary)', fontWeight: 600, lineHeight: 1.3 }}>{s.title}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Symbol Insert Bar */}
            <div style={{
              padding: '0.5rem 1.5rem', maxWidth: 860, margin: '0 auto', width: '100%',
              display: 'flex', alignItems: 'center', gap: '0.4rem', overflowX: 'auto',
              borderTop: '1px solid rgba(30,45,80,0.5)',
            }}>
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', flexShrink: 0 }}>Insert:</span>
              {QUICK_MATH_SYMBOLS.map((s, i) => (
                <button key={i} className="symbol-chip" onClick={() => insertSymbol(s.insert)}>{s.label}</button>
              ))}
            </div>

            {/* Image Preview Box if image is selected */}
            {selectedImage && (
              <div style={{
                padding: '0.4rem 1.5rem 0', maxWidth: 860, margin: '0 auto', width: '100%',
              }}>
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '0.5rem 0.85rem', background: 'rgba(18, 27, 48, 0.95)',
                  border: '1px solid rgba(59, 130, 246, 0.4)', borderRadius: 12,
                  boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <img src={selectedImage.dataUrl} alt="Attached Preview" style={{ width: 42, height: 42, objectFit: 'cover', borderRadius: 8, border: '1px solid rgba(59,130,246,0.3)' }} />
                    <div>
                      <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span>{selectedImage.name}</span>
                        <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>({selectedImage.size})</span>
                      </div>
                      <div style={{ fontSize: '0.7rem', color: '#93c5fd' }}>Vision AI will transcribe and solve this math problem</div>
                    </div>
                  </div>
                  <button onClick={() => setSelectedImage(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 6, borderRadius: 6 }} title="Remove image">
                    <X size={16} />
                  </button>
                </div>
              </div>
            )}

            {/* Input Area */}
            <div style={{
              padding: '0.75rem 1.5rem 1.25rem', maxWidth: 860, margin: '0 auto', width: '100%',
              display: 'flex', gap: '0.6rem', alignItems: 'flex-end',
            }}>
              {/* Image Upload Button */}
              <input type="file" ref={imageInputRef} onChange={handleImageSelect} accept="image/*" className="hidden" />
              <button
                type="button"
                onClick={() => imageInputRef.current?.click()}
                className="btn-ghost"
                title="Upload Math Question Image (or paste with Ctrl+V)"
                style={{
                  height: 48, width: 48, padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  borderRadius: 12, flexShrink: 0,
                  borderColor: selectedImage ? '#3b82f6' : undefined,
                  background: selectedImage ? 'rgba(59,130,246,0.2)' : undefined,
                }}>
                <Camera size={19} style={{ color: selectedImage ? '#60a5fa' : 'var(--text-muted)' }} />
              </button>

              <div style={{ flex: 1, position: 'relative' }}>
                <textarea
                  className="chat-input"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onPaste={handlePaste}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                  placeholder={selectedImage ? "Add optional instructions or click Send to solve image..." : "Ask a math question or upload/paste an image of a math problem…"}
                  rows={1}
                  style={{
                    width: '100%', padding: '0.85rem 1rem', fontSize: '0.875rem',
                    minHeight: 48, maxHeight: 180,
                    boxSizing: 'border-box', display: 'block',
                  }}
                  onInput={e => { e.target.style.height = 'auto'; e.target.style.height = Math.min(e.target.scrollHeight, 180) + 'px'; }}
                />
              </div>
              <button
                onClick={() => handleSend()}
                disabled={(!input.trim() && !selectedImage) || loading}
                className="btn-primary"
                style={{
                  height: 48, width: 48, padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  borderRadius: 12, flexShrink: 0,
                  opacity: (!input.trim() && !selectedImage) || loading ? 0.5 : 1,
                  cursor: (!input.trim() && !selectedImage) || loading ? 'not-allowed' : 'pointer'
                }}>
                <Send size={18} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ── DECORATIVE GRID ─────────────────────────────────────── */}
      <div aria-hidden style={{
        position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none',
        backgroundImage: `linear-gradient(rgba(79,142,247,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(79,142,247,0.025) 1px, transparent 1px)`,
        backgroundSize: '50px 50px',
      }} />
    </div>
  );
}
