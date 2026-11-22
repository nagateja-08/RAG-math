import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { 
  Send, Plus, Trash2, Database, Layers, Sparkles, 
  Upload, HelpCircle, CheckCircle2, AlertTriangle, 
  BarChart3, Calculator, BookOpen, ArrowRight, ExternalLink 
} from 'lucide-react';

import { askQuestion, uploadFile, healthCheck } from '../services/api';
import GraphExplorer from './GraphExplorer';
import ProgressDashboard from './ProgressDashboard';
import FormulaVerifier from './FormulaVerifier';
import AssessmentModal from './AssessmentModal';

const QUICK_MATH_SYMBOLS = [
  { label: '∫ dx', insert: '\\int f(x) \\, dx' },
  { label: 'd/dx', insert: '\\frac{d}{dx}[f(x)]' },
  { label: '√x', insert: '\\sqrt{x}' },
  { label: 'lim', insert: '\\lim_{x \\to 0}' },
  { label: 'x²', insert: 'x^2' },
  { label: '∑', insert: '\\sum_{i=1}^{n}' },
  { label: 'π', insert: '\\pi' },
  { label: 'θ', insert: '\\theta' },
  { label: 'P(A|B)', insert: 'P(A|B) = \\frac{P(A \\cap B)}{P(B)}' },
];

const SUGGESTIONS = [
  {
    title: 'Explain Integration',
    prompt: 'Explain Integration, its prerequisites, fundamental formulas, and a worked example with verification.',
    tag: 'Calculus'
  },
  {
    title: 'Differentiate & Verify',
    prompt: 'Find the derivative of f(x) = x^3 - 4x + sin(x) and verify it mathematically with SymPy.',
    tag: 'Derivatives'
  },
  {
    title: 'Solve Quadratic Equation',
    prompt: 'Solve the equation x^2 - 5x + 6 = 0 step-by-step and show roots.',
    tag: 'Algebra'
  },
  {
    title: 'Bayes Theorem Application',
    prompt: 'Explain Bayes Theorem and its prerequisites in probability with a concrete example.',
    tag: 'Probability'
  }
];

export default function ChatUI() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'graph', 'progress', 'verifier'
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: 
        `# Welcome to MathGPT! 🧮\n\n` +
        `I am your **Graph-Enhanced RAG Intelligent Mathematical Learning Platform**.\n\n` +
        `### How I work:\n` +
        `- **Knowledge Graph (Neo4j)**: Understands prerequisites, formulas, and conceptual dependencies.\n` +
        `- **Vector Retrieval (FAISS)**: Retrieves grounded mathematical explanations from documents.\n` +
        `- **Symbolic Math Engine (SymPy)**: Independently verifies formulas, derivatives, and calculations.\n\n` +
        `Ask any math question below, upload your textbooks, or explore the interactive Knowledge Graph!`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);

  // File Upload State
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);
  const fileInputRef = useRef(null);

  // Assessment Modal State
  const [quizConcept, setQuizConcept] = useState(null);
  const [isQuizOpen, setIsQuizOpen] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const checkHealth = async () => {
    try {
      const data = await healthCheck();
      setSystemHealth(data);
    } catch (err) {
      setSystemHealth({ status: 'offline', neo4j_mode: 'offline', total_graph_nodes: 0 });
    }
  };

  const handleSend = async (textToSend = input) => {
    const questionText = textToSend.trim();
    if (!questionText || loading) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: questionText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Build conversation history format
      const history = messages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await askQuestion(questionText, history);

      const botMsg = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        identified_concept: response.identified_concept,
        prerequisites: response.prerequisites,
        document_references: response.document_references,
        graph_context: response.graph_context,
        sympy_verification: response.sympy_verification,
        recommended_study_topics: response.recommended_study_topics,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error('Ask error:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: '⚠️ Unable to complete request. Please verify backend connection.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadMessage(null);
    try {
      const res = await uploadFile(file);
      setUploadMessage({
        type: 'success',
        text: `Indexed ${res.chunks_added} chunks into FAISS and synced ${res.concepts_extracted.length} concepts to Neo4j.`,
      });
      checkHealth();
    } catch (err) {
      setUploadMessage({
        type: 'error',
        text: 'Document upload failed. Ensure file is a valid .pdf or .txt file.',
      });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const insertSymbol = (symbol) => {
    setInput((prev) => prev + (prev.length > 0 && !prev.endsWith(' ') ? ' ' : '') + symbol);
  };

  const startQuiz = (conceptName) => {
    setQuizConcept(conceptName);
    setIsQuizOpen(true);
  };

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-100 font-sans overflow-hidden">
      {/* Assessment Modal */}
      <AssessmentModal
        concept={quizConcept}
        isOpen={isQuizOpen}
        onClose={() => setIsQuizOpen(false)}
        onComplete={() => checkHealth()}
      />

      {/* Main Container */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-slate-900/90 border-b border-slate-800 px-6 flex items-center justify-between backdrop-blur-md z-20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-600/30">
              <span className="text-xl">🧮</span>
            </div>
            <div>
              <h1 className="text-base font-bold text-white flex items-center gap-2">
                MathGPT
                <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full font-semibold">
                  Graph-Enhanced RAG v2.0
                </span>
              </h1>
              <p className="text-[11px] text-slate-400">
                FAISS Vector Search &bull; Neo4j Knowledge Graph &bull; SymPy Symbolic Engine
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'chat'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              💬 Math Chat
            </button>
            <button
              onClick={() => setActiveTab('graph')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                activeTab === 'graph'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" /> Graph Explorer
            </button>
            <button
              onClick={() => setActiveTab('progress')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                activeTab === 'progress'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" /> Learning Progress
            </button>
            <button
              onClick={() => setActiveTab('verifier')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5 ${
                activeTab === 'verifier'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Calculator className="w-3.5 h-3.5" /> SymPy Verifier
            </button>
          </div>

          {/* Health & Upload Pill */}
          <div className="flex items-center gap-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf,.txt,.md"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-medium border border-slate-700 transition"
            >
              <Upload className="w-3.5 h-3.5 text-indigo-400" />
              <span>{uploading ? 'Indexing...' : 'Upload PDF/TXT'}</span>
            </button>

            {systemHealth && (
              <div className="flex items-center gap-2 text-[11px] text-slate-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                <span
                  className={`w-2 h-2 rounded-full ${
                    systemHealth.status === 'healthy' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'
                  }`}
                />
                <span>Graph: {systemHealth.neo4j_mode === 'live_neo4j' ? 'Live Neo4j' : 'Active (60 nodes)'}</span>
              </div>
            )}
          </div>
        </header>

        {/* Upload Status Banner */}
        {uploadMessage && (
          <div
            className={`px-6 py-2 text-xs flex items-center justify-between border-b ${
              uploadMessage.type === 'success'
                ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-200'
                : 'bg-rose-950/40 border-rose-500/30 text-rose-200'
            }`}
          >
            <span>{uploadMessage.text}</span>
            <button onClick={() => setUploadMessage(null)} className="text-slate-400 hover:text-white">
              ✕
            </button>
          </div>
        )}

        {/* Tab View Switcher */}
        {activeTab === 'graph' ? (
          <div className="flex-1 p-6 overflow-y-auto">
            <GraphExplorer
              onSelectConceptForChat={(concept) => {
                setActiveTab('chat');
                handleSend(`Explain ${concept}, its mathematical prerequisites, formal definitions, and a step-by-step example.`);
              }}
              onStartQuiz={(concept) => startQuiz(concept)}
            />
          </div>
        ) : activeTab === 'progress' ? (
          <div className="flex-1 p-6 overflow-y-auto max-w-5xl mx-auto w-full">
            <ProgressDashboard
              onSelectTopic={(topic) => {
                setActiveTab('chat');
                handleSend(`Explain ${topic} in detail with step-by-step mathematical examples.`);
              }}
              onStartQuiz={(topic) => startQuiz(topic)}
            />
          </div>
        ) : activeTab === 'verifier' ? (
          <div className="flex-1 p-6 overflow-y-auto max-w-4xl mx-auto w-full">
            <FormulaVerifier />
          </div>
        ) : (
          /* Main Math Chat View */
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            {/* Messages Scroll Area */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 max-w-4xl mx-auto w-full">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[88%] md:max-w-[80%] rounded-2xl p-5 shadow-md ${
                      msg.role === 'user'
                        ? 'bg-indigo-600 text-white rounded-br-none'
                        : 'bg-slate-900 border border-slate-800 text-slate-100 rounded-bl-none space-y-4'
                    }`}
                  >
                    {/* Message Header */}
                    <div className="flex items-center justify-between text-[11px] opacity-75 mb-1 pb-1 border-b border-white/10">
                      <span className="font-semibold uppercase tracking-wider">
                        {msg.role === 'user' ? 'You' : 'MathGPT Mentor'}
                      </span>
                      <span>{msg.timestamp}</span>
                    </div>

                    {/* Markdown Answer Body with KaTeX */}
                    <div className="prose prose-invert max-w-none text-sm leading-relaxed overflow-x-auto">
                      <ReactMarkdown
                        remarkPlugins={[remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>

                    {/* Graph Prerequisite Alert Banner */}
                    {msg.role === 'assistant' && msg.prerequisites && msg.prerequisites.length > 0 && (
                      <div className="mt-3 p-3 bg-blue-950/40 border border-blue-500/30 rounded-xl text-xs space-y-2">
                        <div className="font-semibold text-blue-300 flex items-center justify-between">
                          <span className="flex items-center gap-1.5">
                            <BookOpen className="w-4 h-4 text-blue-400" />
                            Prerequisites for {msg.identified_concept || 'this topic'} (from Knowledge Graph):
                          </span>
                          {msg.identified_concept && (
                            <button
                              onClick={() => startQuiz(msg.identified_concept)}
                              className="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-[11px] font-bold transition flex items-center gap-1"
                            >
                              <span>Test My Readiness</span>
                              <ArrowRight className="w-3 h-3" />
                            </button>
                          )}
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.prerequisites.map((p, i) => (
                            <span
                              key={i}
                              onClick={() => startQuiz(p.name)}
                              className="bg-blue-500/10 text-blue-300 border border-blue-500/20 px-2 py-0.5 rounded-md cursor-pointer hover:bg-blue-500/20"
                            >
                              {p.name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* SymPy Verification Status Badge */}
                    {msg.role === 'assistant' && msg.sympy_verification && msg.sympy_verification.status !== 'not_applicable' && (
                      <div
                        className={`p-3 rounded-xl border text-xs flex items-start gap-2.5 ${
                          msg.sympy_verification.is_verified
                            ? 'bg-emerald-950/30 border-emerald-500/30 text-emerald-300'
                            : 'bg-amber-950/30 border-amber-500/30 text-amber-300'
                        }`}
                      >
                        {msg.sympy_verification.is_verified ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                        ) : (
                          <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
                        )}
                        <div>
                          <div className="font-bold">
                            {msg.sympy_verification.is_verified
                              ? 'SymPy Independently Verified: Mathematically Valid'
                              : 'SymPy Verification Notice: Could not be automatically verified'}
                          </div>
                          {msg.sympy_verification.latex_output && (
                            <div className="text-slate-200 mt-1 font-mono">
                              Verified Step: {msg.sympy_verification.latex_output}
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Document Reference Citations */}
                    {msg.role === 'assistant' && msg.document_references && msg.document_references.length > 0 && (
                      <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
                        <Database className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Sources: {msg.document_references.join(', ')}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex items-start gap-3">
                  <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl rounded-bl-none text-xs text-slate-400 flex items-center gap-3">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-500" />
                    <span>Traversing Knowledge Graph & calculating symbolic verification...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Suggestions (if conversation is short) */}
            {messages.length <= 2 && (
              <div className="px-6 py-2 max-w-4xl mx-auto w-full grid grid-cols-2 md:grid-cols-4 gap-2">
                {SUGGESTIONS.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(s.prompt)}
                    className="p-2.5 bg-slate-900/90 hover:bg-slate-800 border border-slate-800 rounded-xl text-left transition group"
                  >
                    <span className="text-[10px] uppercase font-bold text-indigo-400 block mb-1">
                      {s.tag}
                    </span>
                    <span className="text-xs text-slate-200 group-hover:text-white font-medium line-clamp-1">
                      {s.title}
                    </span>
                  </button>
                ))}
              </div>
            )}

            {/* Quick Math Symbols Bar */}
            <div className="px-6 py-1.5 max-w-4xl mx-auto w-full flex items-center gap-1.5 overflow-x-auto">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mr-1">Insert:</span>
              {QUICK_MATH_SYMBOLS.map((s, i) => (
                <button
                  key={i}
                  onClick={() => insertSymbol(s.insert)}
                  className="px-2 py-0.5 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white rounded-md text-xs font-mono border border-slate-800 transition shrink-0"
                >
                  {s.label}
                </button>
              ))}
            </div>

            {/* Input Form Bar */}
            <div className="p-4 bg-slate-900/80 border-t border-slate-800 backdrop-blur-md">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="max-w-4xl mx-auto flex items-center gap-2"
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a mathematical question (e.g. 'Explain Integration and its prerequisites', or 'differentiate x^3 - 4x')..."
                  className="flex-1 p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="p-3.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl transition shadow-lg shadow-indigo-600/30"
                >
                  <Send className="w-5 h-5" />
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
