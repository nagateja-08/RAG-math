import React, { useState, useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import FileUpload from "./FileUpload";
import useChat from "../hooks/useChat";

const ChatBox = () => {
  const [input, setInput] = useState("");
  const { messages, sendMessage, isLoading } = useChat();
  const messagesEndRef = useRef(null);

  const handleSend = async () => {
    if (!input.trim()) return;
    await sendMessage(input.trim());
    setInput("");
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
      {/* Header */}
      <header className="p-4 bg-white dark:bg-gray-800 shadow flex justify-between items-center">
        <h1 className="text-xl font-semibold text-gray-800 dark:text-gray-200">MathGPT</h1>
        {/* Theme toggle could be added here */}
      </header>

      {/* Message list */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} role={msg.role} content={msg.content} />
        ))}
        {isLoading && <MessageBubble role="assistant" content="..." />}
        <div ref={messagesEndRef} />
      </main>

      {/* Input area */}
      <footer className="p-4 bg-white dark:bg-gray-800 border-t flex items-center space-x-2">
        <FileUpload onUpload={sendMessage} disabled={isLoading} />
        <textarea
          className="flex-1 p-2 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-200"
          rows={1}
          placeholder="Ask a math question…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          disabled={isLoading}
        />
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          onClick={handleSend}
          disabled={isLoading}
        >
          Send
        </button>
      </footer>
    </div>
  );
};

export default ChatBox;
