import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-row ${isUser ? 'user-row' : 'assistant-row'}`}>
      {!isUser && (
        <div className="avatar assistant-avatar">
          <span>∑</span>
        </div>
      )}

      <div className={`bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
        <ReactMarkdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline ? (
                <pre className="code-block">
                  <code className={className} {...props}>
                    {children}
                  </code>
                </pre>
              ) : (
                <code className="inline-code" {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {message.content}
        </ReactMarkdown>

        {/* SymPy result badge */}
        {message.sympyResult?.success && (
          <div className="sympy-badge">
            <span className="sympy-label">Computed Result</span>
            <span className="sympy-value">
              {message.sympyResult.solutions_latex
                ? `x = ${message.sympyResult.solutions_latex.join(', ')}`
                : message.sympyResult.result_latex ||
                  message.sympyResult.derivative_latex ||
                  message.sympyResult.simplified_latex || ''}
            </span>
          </div>
        )}

        {/* Context sources */}
        {message.contextUsed?.length > 0 && (
          <div className="context-info">
            <span className="context-label">
              {message.contextUsed.length} reference{message.contextUsed.length > 1 ? 's' : ''} used
            </span>
          </div>
        )}

        <div className="message-time">
          {message.timestamp?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>

      {isUser && (
        <div className="avatar user-avatar">
          <span>U</span>
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
