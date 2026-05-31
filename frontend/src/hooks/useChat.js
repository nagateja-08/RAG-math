import { useState, useCallback } from 'react';
import { sendMessage, uploadFile } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 0,
      role: 'assistant',
      content: "Hello! I'm **MathGPT** 🧮 — your AI-powered mathematical assistant.\n\nI can help you with:\n- Algebra, Calculus, Linear Algebra\n- Differential Equations & Laplace Transforms\n- Probability & Statistics\n- Engineering Mathematics\n- Step-by-step problem solving\n\nAsk me any math question!",
      timestamp: new Date(),
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const addMessage = useCallback((role, content, extra = {}) => {
    const msg = { id: Date.now(), role, content, timestamp: new Date(), ...extra };
    setMessages(prev => [...prev, msg]);
    return msg;
  }, []);

  const sendChat = useCallback(async (text, options = {}) => {
    if (!text.trim() || isLoading) return;
    setError(null);

    // Add user message
    addMessage('user', text);
    setIsLoading(true);

    try {
      // Build history for context (last 6 messages, exclude welcome message)
      const history = messages
        .filter(m => m.id !== 0)
        .slice(-6)
        .map(m => ({ role: m.role, content: m.content }));

      const response = await sendMessage(text, history, options);

      addMessage('assistant', response.answer, {
        contextUsed: response.context_used || [],
        sympyResult: response.sympy_result,
        model: response.model,
      });
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Something went wrong.';
      setError(errMsg);
      addMessage('assistant', `❌ Error: ${errMsg}`);
    } finally {
      setIsLoading(false);
    }
  }, [messages, isLoading, addMessage]);

  const uploadDocument = useCallback(async (file) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await uploadFile(file);
      addMessage('assistant', `📄 **Document uploaded successfully!**\n\n- File: \`${result.filename}\`\n- Added **${result.chunks_added} chunks** to the knowledge base.\n\nYou can now ask questions about this document!`);
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message;
      setError(errMsg);
      addMessage('assistant', `❌ Upload failed: ${errMsg}`);
    } finally {
      setIsLoading(false);
    }
  }, [addMessage]);

  const clearChat = useCallback(() => {
    setMessages([{
      id: 0,
      role: 'assistant',
      content: "Hello! I'm **MathGPT** 🧮 — your AI-powered mathematical assistant.\n\nAsk me any math question!",
      timestamp: new Date(),
    }]);
    setError(null);
  }, []);

  return { messages, isLoading, error, sendChat, uploadDocument, clearChat };
};
