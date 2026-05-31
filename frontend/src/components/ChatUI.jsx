import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import ScrollToBottom from 'react-scroll-to-bottom';
import { 
  Send, 
  Plus, 
  Trash2, 
  Database, 
  Settings, 
  FileText, 
  HelpCircle, 
  Activity, 
  Sparkles,
  ArrowRight,
  Upload,
  Volume2,
  Bookmark,
  ChevronRight,
  Maximize2
} from 'lucide-react';
import ThoughtProcess from './ThoughtProcess';
import { sendMessage, uploadFile, healthCheck } from '../services/api';
import 'katex/dist/katex.min.css';

const SUGGESTIONS = [
  {
    icon: '📐',
    title: 'Differentiate',
    prompt: 'Differentiate x * sin(x) + cos(x) with respect to x',
    desc: 'Calculus derivatives'
  },
  {
    icon: '📈',
    title: 'Solve Equation',
    prompt: 'Solve equation x^2 - 5*x + 6 = 0 for x',
    desc: 'Algebraic roots'
  },
  {
    icon: '🧮',
    title: 'Matrix Inverse',
    prompt: 'Compute the inverse of matrix [[1, 2], [3, 4]]',
    desc: 'Linear algebra'
  },
  {
    icon: '📜',
    title: 'ODE Solver',
    prompt: 'Solve the Ordinary Differential Equation: y(x).diff(x) - y(x)',
    desc: 'Differential equations'
  }
];

const ChatUI = () => {
  // Chat States
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hello! I'm **MathGPT** 🧮 — your professional AI mathematical assistant with deep reasoning and symbolic evaluation.\n\nI am equipped with a RAG knowledge base and a SymPy symbolic math engine. Ask me any math question, upload textbooks/papers, or try one of the suggestion templates below!",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Settings States
  const [useRag, setUseRag] = useState(true);
  const [useSympy, setUseSympy] = useState(true);
  const [model, setModel] = useState('llama-3.3-70b-versatile');
  const [isOnline, setIsOnline] = useState(false);
  const [vectorStoreStatus, setVectorStoreStatus] = useState('Checking...');

  // Ingestion States
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);
  
  const fileInputRef = useRef(null);

  // Connection Health Check
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const data = await healthCheck();
        if (data.status === 'ok') {
          setIsOnline(true);
          setVectorStoreStatus('Loaded & Ready');
        } else {
          setIsOnline(false);
          setVectorStoreStatus('Unavailable');
        }
      } catch (err) {
        setIsOnline(false);
        setVectorStoreStatus('Unavailable');
      }
    };
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Split content into thought and markdown response
  const parseMessageContent = (content) => {
    if (!content) return { thought: '', response: '' };
    
    // Support DeepSeek R1 tags
    if (content.includes('<think>')) {
      const parts = content.split('</think>');
      if (parts.length > 1) {
        return {
          thought: parts[0].replace('<think>', '').trim(),
          response: parts.slice(1).join('</think>').trim()
        };
      }
      return { thought: content.replace('<think>', '').trim(), response: '' };
    }
    
    return { thought: '', response: content };
  };

  const handleSend = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    setError(null);
    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Build conversation history (excluding welcome message, last 6 rounds)
      const history = messages
        .filter(m => m.id !== 'welcome')
        .slice(-6)
        .map(m => ({ role: m.role, content: m.content }));

      // We use axios API from services/api, which parses data automatically
      const result = await sendMessage(text, history, {
        useRag,
        useSympy,
        model
      });

      const assistantMsg = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.answer,
        contextUsed: result.context_used || [],
        sympyResult: result.sympy_result,
        model: result.model || model,
        timestamp: new Date()
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      const errMsg = err.response?.data?.detail || err.message || 'Error communicating with server.';
      setError(errMsg);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `❌ **Failed to generate answer.** \n\n*Details: ${errMsg}*`,
          timestamp: new Date()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadMessage({ type: 'info', text: `Ingesting ${file.name}...` });

    try {
      const res = await uploadFile(file);
      setUploadMessage({ 
        type: 'success', 
        text: `📄 Ingested! Added ${res.chunks_added} math blocks.` 
      });
      // Add notification to conversation
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: `📄 **Document Uploaded Successfully**\n\n- **File Name**: \`${res.filename}\`\n- **Mathematical Blocks Indexed**: \`${res.chunks_added}\` \n\nYou can now ask specific algebraic, geometric, or textual questions about the contents of this document!`,
          timestamp: new Date()
        }
      ]);
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Upload failed.';
      setUploadMessage({ type: 'error', text: errMsg });
    } finally {
      setUploading(false);
      setTimeout(() => setUploadMessage(null), 5000);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: "Conversation history cleared. How can I help you with mathematics today? 📐",
        timestamp: new Date()
      }
    ]);
    setError(null);
  };

  return (
    <div className="flex h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden font-sans antialiased">
      
      {/* Hidden file input (still needed for the + button in the input bar) */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt"
        className="hidden"
        onChange={handleFileUpload}
        disabled={uploading}
      />

      {/* 2. CHAT CANVAS */}
      <main className="flex-1 flex flex-col justify-between bg-slate-950 relative overflow-hidden">
        
        {/* Glowing Decorative Orbs */}
        <div className="absolute top-[-20%] left-[20%] w-[500px] h-[500px] rounded-full bg-sky-600/5 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[10%] w-[450px] h-[450px] rounded-full bg-indigo-600/5 blur-[120px] pointer-events-none" />

        {/* Diagnostic Top Header */}
        <header className="h-14 border-b border-slate-800/40 bg-slate-950/80 backdrop-blur-md flex items-center justify-between px-6 z-10 select-none">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-300">Mathematical RAG Assistant</span>
            <span className="px-2 py-0.5 bg-sky-950 border border-sky-900 text-sky-400 rounded-full text-[10px] font-mono tracking-wider font-semibold">
              v1.0.0
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-semibold">
            <Sparkles size={12} className="text-indigo-400 animate-pulse" />
            <span>LLM: {model}</span>
          </div>
        </header>

        {/* Message Scrolling Body */}
        <div className="flex-1 overflow-y-auto z-10">
          <ScrollToBottom 
            className="h-full flex flex-col" 
            scrollViewClassName="px-4 py-8 max-w-3xl w-full mx-auto space-y-6 flex flex-col"
          >
            {messages.map((msg, idx) => {
              const isUser = msg.role === 'user';
              const { thought, response } = parseMessageContent(msg.content);

              return (
                <div key={msg.id || idx} className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
                  
                  {/* Assistant Avatar */}
                  {!isUser && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shrink-0 shadow-md">
                      <span className="font-extrabold text-sm">∑</span>
                    </div>
                  )}

                  {/* Bubble Body */}
                  <div className={`max-w-[85%] rounded-2xl p-4 shadow-sm flex flex-col space-y-2 ${
                    isUser 
                      ? 'bg-gradient-to-br from-sky-500 to-indigo-600 text-white rounded-tr-none px-4.5 py-3 shadow-indigo-500/10' 
                      : 'bg-slate-900 border border-slate-800/80 rounded-tl-none text-slate-100'
                  }`}>
                    
                    {/* User Text */}
                    {isUser ? (
                      <p className="text-sm font-medium whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    ) : (
                      // Assistant Structured Content
                      <div className="text-sm leading-relaxed space-y-3">
                        
                        {/* Collapsible thought process (DeepSeek R1) */}
                        {thought && <ThoughtProcess thinkingText={thought} />}

                        {/* Main Response Markdown */}
                        {response && (
                          <div className="prose prose-invert prose-slate prose-xs max-w-none text-slate-200">
                            <ReactMarkdown
                              remarkPlugins={[remarkMath]}
                              rehypePlugins={[rehypeKatex]}
                              components={{
                                p({ children }) {
                                  return <p className="mb-2.5 last:mb-0 leading-relaxed text-slate-200">{children}</p>;
                                },
                                pre({ node, children, ...props }) {
                                  return (
                                    <pre className="my-3 bg-slate-950 border border-slate-800 rounded-xl p-3.5 overflow-x-auto text-xs font-mono select-text" {...props}>
                                      {children}
                                    </pre>
                                  );
                                },
                                code({ node, inline, className, children, ...props }) {
                                  return inline ? (
                                    <code className="bg-slate-800/50 border border-slate-700/30 rounded px-1.5 py-0.5 text-xs text-sky-400 font-mono" {...props}>
                                      {children}
                                    </code>
                                  ) : (
                                    <code className={className} {...props}>
                                      {children}
                                    </code>
                                  );
                                },
                                table({ children }) {
                                  return (
                                    <div className="overflow-x-auto my-3 border border-slate-800 rounded-xl">
                                      <table className="min-w-full divide-y divide-slate-800 text-xs text-left">{children}</table>
                                    </div>
                                  );
                                },
                                th({ children }) {
                                  return <th className="px-4 py-2 bg-slate-950/50 font-semibold text-slate-350">{children}</th>;
                                },
                                td({ children }) {
                                  return <td className="px-4 py-2 border-t border-slate-800/40 text-slate-400">{children}</td>;
                                }
                              }}
                            >
                              {response}
                            </ReactMarkdown>
                          </div>
                        )}

                        {/* SymPy Evaluated Result Card */}
                        {msg.sympyResult && msg.sympyResult.success && (
                          <div className="mt-4 p-3 bg-sky-950/20 border border-sky-500/10 rounded-xl space-y-2">
                            <div className="flex items-center gap-1.5 text-xs text-sky-400 font-semibold">
                              <Sparkles size={13} />
                              <span>Symbolic Math Engine evaluated:</span>
                            </div>
                            <div className="bg-slate-950/80 p-2.5 rounded-lg border border-slate-850 overflow-x-auto flex justify-center text-slate-200">
                              {/* Ifsolutions LaTeX exist, render it, else print LaTeX value */}
                              <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                                {msg.sympyResult.solutions_latex
                                  ? `$$x \\in \\left\\{ ${msg.sympyResult.solutions_latex.join(', ')} \\right\\}$$`
                                  : msg.sympyResult.result_latex
                                    ? `$$${msg.sympyResult.result_latex}$$`
                                    : msg.sympyResult.derivative_latex
                                      ? `$$\\frac{d}{dx} = ${msg.sympyResult.derivative_latex}$$`
                                      : msg.sympyResult.simplified_latex
                                        ? `$$= ${msg.sympyResult.simplified_latex}$$`
                                        : `$$${msg.sympyResult.solution_latex || ''}$$`}
                              </ReactMarkdown>
                            </div>
                          </div>
                        )}

                        {/* RAG Context reference count */}
                        {msg.contextUsed && msg.contextUsed.length > 0 && (
                          <div className="flex items-center gap-1.5 text-[10px] text-slate-500 font-semibold select-none pt-2.5 border-t border-slate-800/30">
                            <Bookmark size={10} className="text-slate-600" />
                            <span>Injected {msg.contextUsed.length} Q&A knowledge source{msg.contextUsed.length > 1 ? 's' : ''} from database</span>
                          </div>
                        )}

                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </ScrollToBottom>
        </div>

        {/* Suggestion Cards Container (Visible on empty chat) */}
        {messages.length <= 1 && (
          <div className="max-w-3xl w-full mx-auto px-6 mb-2 z-10 grid grid-cols-2 gap-3 select-none">
            {SUGGESTIONS.map((sug, idx) => (
              <div 
                key={idx}
                onClick={() => handleSend(sug.prompt)}
                className="bg-slate-900 hover:bg-slate-850 hover:border-slate-700/60 border border-slate-800/50 p-3 rounded-xl cursor-pointer transition-all flex flex-col text-left group"
              >
                <div className="flex justify-between items-start">
                  <span className="text-lg mb-1">{sug.icon}</span>
                  <ChevronRight size={14} className="text-slate-600 group-hover:text-sky-400 group-hover:translate-x-0.5 transition-all" />
                </div>
                <h4 className="text-xs font-semibold text-slate-200 mb-0.5">{sug.title}</h4>
                <p className="text-[10px] text-slate-500 font-mono tracking-tight font-medium truncate">{sug.prompt}</p>
              </div>
            ))}
          </div>
        )}

        {/* Diagnostic Errors */}
        {error && (
          <div className="max-w-3xl w-full mx-auto px-6 py-2 z-10">
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs p-3 rounded-xl flex items-center justify-between">
              <span>⚠️ Error: {error}</span>
              <button onClick={() => setError(null)} className="font-semibold text-[10px] hover:text-white">DISMISS</button>
            </div>
          </div>
        )}

        {/* elevated Input box resembling ChatGPT */}
        <footer className="p-6 bg-gradient-to-t from-slate-950 via-slate-950 to-transparent z-10 shrink-0 select-none">
          <div className="max-w-3xl w-full mx-auto space-y-3">
            
            <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl flex items-end p-2.5 focus-within:ring-2 focus-within:ring-sky-500/10 focus-within:border-sky-500/50 transition-all">
              
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                title="Attach PDF or Text context"
                className="p-2 text-slate-500 hover:text-sky-400 active:bg-slate-850 rounded-xl transition-all cursor-pointer select-none"
              >
                <Plus size={18} />
              </button>
              
              <textarea
                value={input}
                rows={1}
                disabled={loading}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKey}
                placeholder="Ask a math problem, compute matrices, differential equations..."
                className="flex-1 bg-transparent border-0 px-3 py-2 text-sm text-slate-200 focus:outline-none resize-none placeholder-slate-500 min-h-[38px] max-h-[120px] scrollbar-none font-medium leading-relaxed font-sans"
              />

              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || loading}
                className="p-2.5 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-450 hover:to-indigo-500 text-white rounded-xl shadow-lg shadow-sky-500/15 active:scale-95 disabled:opacity-30 disabled:scale-100 disabled:shadow-none disabled:bg-slate-800 transition-all shrink-0 cursor-pointer"
              >
                {loading ? (
                  <span className="block w-4.5 h-4.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Send size={15} />
                )}
              </button>

            </div>

            <p className="text-[10px] text-slate-500 text-center font-medium select-none">
              MathGPT parses SymPy expressions safely and integrates dynamic contexts. Always verify steps.
            </p>

          </div>
        </footer>

      </main>
    </div>
  );
};

export default ChatUI;
