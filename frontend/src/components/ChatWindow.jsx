import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';
import MessageBubble from './MessageBubble';

const SUGGESTIONS = [
  {
    title: "Pagani Tower in Dubai",
    query: "Tell me about DaVinci Tower by Pagani in Dubai. What are the amenities and price?"
  },
  {
    title: "Lamborghini Villas Spain",
    query: "What luxury villas does DarGlobal have in Spain? Describe Tierra Viva."
  },
  {
    title: "AIDA Oman Resort",
    query: "What is the AIDA project in Oman? Tell me about the Trump International resort."
  },
  {
    title: "Riyadh Listings on Wasalt",
    query: "What 3-bedroom residential properties are available for sale in Riyadh on Wasalt?"
  }
];

export default function ChatWindow({ messages, isLoading, onSendMessage }) {
  const [input, setInput] = useState('');
  const [loadingTime, setLoadingTime] = useState(0);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Loading duration timer to give dynamic concierge status feedback
  useEffect(() => {
    let timer;
    if (isLoading) {
      setLoadingTime(0);
      timer = setInterval(() => {
        setLoadingTime((prev) => prev + 1);
      }, 1000);
    } else {
      setLoadingTime(0);
    }
    return () => clearInterval(timer);
  }, [isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden relative">
      {/* Scrollable messages container */}
      <div className="flex-1 overflow-y-auto px-4">
        <div className="max-w-3xl mx-auto w-full py-6">
          {messages.length === 0 ? (
            <div className="min-h-[55vh] flex flex-col items-center justify-center text-center">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#8C6D23] flex items-center justify-center font-bold text-black text-lg mb-6 shadow-md">
                D
              </div>
              <h2 className="text-2xl font-semibold text-white mb-8 tracking-tight">
                What real estate property are you looking for?
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl text-left">
                {SUGGESTIONS.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSendMessage(item.query)}
                    className="p-3.5 rounded-2xl bg-[#212121] hover:bg-[#2f2f2f] border border-[#2f2f2f] hover:border-[#424242] transition group"
                  >
                    <span className="text-xs font-medium text-gray-300 group-hover:text-white block mb-0.5">
                      {item.title}
                    </span>
                    <p className="text-xs text-gray-500 line-clamp-1">{item.query}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div>
              {messages.map((msg, index) => (
                <MessageBubble key={index} message={msg} />
              ))}
              {isLoading && (
                <div className="flex gap-4 items-start py-4">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#8C6D23] flex items-center justify-center font-bold text-black text-xs shrink-0 mt-0.5 shadow-sm animate-pulse">
                    D
                  </div>
                  <div className="flex-1 bg-[#262626] border border-[#333333] rounded-2xl px-4 py-3 max-w-md shadow-sm">
                    <div className="flex items-center gap-2 mb-1.5">
                      <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-[#D4AF37] animate-bounce"></span>
                        <span className="w-2 h-2 rounded-full bg-[#D4AF37] animate-bounce [animation-delay:0.2s]"></span>
                        <span className="w-2 h-2 rounded-full bg-[#D4AF37] animate-bounce [animation-delay:0.4s]"></span>
                      </div>
                      <span className="text-xs font-medium text-gray-200">
                        {loadingTime < 3
                          ? "Searching portfolio & retrieving property details..."
                          : "Consulting AI Real Estate Advisor..."}
                      </span>
                    </div>
                    <div className="text-[11px] text-amber-400/90 flex items-center gap-1.5 mt-1">
                      <span className="inline-block w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
                      <span>First response may take a moment while the cloud server wakes up.</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Floating Capsule Input Footer */}
      <div className="w-full max-w-3xl mx-auto px-4 pb-4 pt-1">
        <form
          onSubmit={handleSubmit}
          className="relative flex items-center bg-[#2f2f2f] rounded-3xl border border-[#383838] focus-within:border-gray-500 shadow-lg transition"
        >
          <textarea
            rows="1"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message DarGlobal AI Advisor..."
            disabled={isLoading}
            className="w-full bg-transparent text-white placeholder-gray-400 text-sm py-3.5 pl-5 pr-14 focus:outline-none resize-none max-h-36"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2.5 w-8 h-8 rounded-full bg-white text-black hover:bg-gray-200 disabled:opacity-30 disabled:hover:bg-white flex items-center justify-center transition disabled:cursor-not-allowed shadow"
          >
            <ArrowUp className="w-4 h-4 stroke-[2.5]" />
          </button>
        </form>
      </div>
    </div>
  );
}
