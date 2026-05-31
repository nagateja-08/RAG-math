import React, { useState } from 'react';
import { Brain, ChevronDown, ChevronRight } from 'lucide-react';

const ThoughtProcess = ({ thinkingText }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (!thinkingText || !thinkingText.trim()) return null;

  return (
    <div className="mb-4 rounded-xl border border-sky-500/10 bg-slate-900/30 backdrop-blur-md overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3.5 text-xs font-semibold text-sky-400/90 hover:bg-white/5 active:bg-white/10 transition-all text-left focus:outline-none"
      >
        <div className="flex items-center gap-2">
          <Brain size={15} className={`text-sky-400 animate-pulse`} />
          <span>Thought Process</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-slate-500 font-mono">
            {isOpen ? 'COLLAPSE' : 'EXPAND'}
          </span>
          {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </div>
      </button>

      {isOpen && (
        <div className="px-4 pb-4 pt-1 text-slate-400 text-xs leading-relaxed border-t border-sky-500/5 font-serif italic max-h-80 overflow-y-auto whitespace-pre-wrap">
          {thinkingText.replace(/<\/?think>/g, '').trim()}
        </div>
      )}
    </div>
  );
};

export default ThoughtProcess;
