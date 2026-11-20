import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import { sendChatMessage } from './services/api';

const STORAGE_KEY = 'darglobal_chat_messages_v1';

export default function App() {
  // Restore conversational context from localStorage if available
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch (e) {
      return [];
    }
  });
  const [isLoading, setIsLoading] = useState(false);

  // Persist conversation context on changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (e) {
      console.warn('Failed to persist conversation context:', e);
    }
  }, [messages]);

  const handleNewChat = () => {
    setMessages([]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {}
  };

  const handleSendMessage = async (text) => {
    const userMessage = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Pass the last 6 turns as conversation history for smooth context retention
      const historyPayload = messages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const data = await sendChatMessage(text, { top_k: 4, history: historyPayload });

      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        model: data.model,
        latency_ms: data.latency_ms,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = {
        role: 'assistant',
        content: `Unable to connect to server. ${err.message}`,
        sources: [],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col bg-[#212121] text-[#ECECEC]">
      <Header onNewChat={handleNewChat} />
      <main className="flex-1 overflow-hidden flex flex-col relative">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
      </main>
    </div>
  );
}
