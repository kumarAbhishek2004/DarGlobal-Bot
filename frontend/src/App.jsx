import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import {
  sendChatMessage,
  fetchThreads,
  fetchThreadDetail,
  deleteThread,
} from './services/api';

const ACTIVE_THREAD_KEY = 'darglobal_active_thread_id';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [threads, setThreads] = useState([]);
  const [currentThreadId, setCurrentThreadId] = useState(() => {
    return localStorage.getItem(ACTIVE_THREAD_KEY) || null;
  });
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  // Load threads from database on initial mount
  useEffect(() => {
    loadThreadsList();
  }, []);

  // When currentThreadId changes, fetch messages from database
  useEffect(() => {
    if (currentThreadId) {
      localStorage.setItem(ACTIVE_THREAD_KEY, currentThreadId);
      loadThreadMessages(currentThreadId);
    } else {
      localStorage.removeItem(ACTIVE_THREAD_KEY);
      setMessages([]);
    }
  }, [currentThreadId]);

  const loadThreadsList = async () => {
    const list = await fetchThreads();
    setThreads(list || []);
  };

  const loadThreadMessages = async (threadId) => {
    setIsLoading(true);
    try {
      const detail = await fetchThreadDetail(threadId);
      if (detail && detail.messages) {
        setMessages(detail.messages);
      }
    } catch (err) {
      console.error('Failed to load thread messages:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setCurrentThreadId(null);
    setMessages([]);
  };

  const handleSelectThread = (threadId) => {
    setCurrentThreadId(threadId);
  };

  const handleDeleteThread = async (threadId) => {
    const success = await deleteThread(threadId);
    if (success) {
      setThreads((prev) => prev.filter((t) => t.id !== threadId));
      if (currentThreadId === threadId) {
        handleNewChat();
      }
    }
  };

  const handleSendMessage = async (text) => {
    const userMessage = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Pass the last 6 turns as conversation context
      const historyPayload = messages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const data = await sendChatMessage(text, {
        top_k: 4,
        history: historyPayload,
        thread_id: currentThreadId,
      });

      // If this was a new thread, store the assigned thread_id
      if (data.thread_id && data.thread_id !== currentThreadId) {
        setCurrentThreadId(data.thread_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        model: data.model,
        latency_ms: data.latency_ms,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Refresh threads list in background so title appears in sidebar
      loadThreadsList();
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

  const activeThread = threads.find((t) => t.id === currentThreadId);

  return (
    <div className="h-screen w-screen overflow-hidden flex bg-[#212121] text-[#ECECEC]">
      {/* ChatGPT-Style History Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        threads={threads}
        activeThreadId={currentThreadId}
        onSelectThread={handleSelectThread}
        onNewChat={handleNewChat}
        onDeleteThread={handleDeleteThread}
      />

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <Header
          onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
          isSidebarOpen={isSidebarOpen}
          onNewChat={handleNewChat}
          activeThreadTitle={activeThread?.title}
        />
        <main className="flex-1 overflow-hidden flex flex-col relative">
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
          />
        </main>
      </div>
    </div>
  );
}
