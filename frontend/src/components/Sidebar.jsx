import React from 'react';
import { Plus, MessageSquare, Trash2, PanelLeftClose, Sparkles } from 'lucide-react';

export default function Sidebar({
  isOpen,
  onClose,
  threads = [],
  activeThreadId,
  onSelectThread,
  onNewChat,
  onDeleteThread,
}) {
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-30 md:hidden backdrop-blur-sm transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-64 bg-[#171717] border-r border-[#2a2a2a] flex flex-col transition-all duration-300 ease-in-out shrink-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:w-0 md:opacity-0 md:pointer-events-none'
        }`}
      >
        {/* Top Header */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-[#262626]">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#8C6D23] flex items-center justify-center font-bold text-black text-[11px] shadow-sm">
              D
            </div>
            <span className="font-semibold text-xs tracking-wider uppercase text-gray-300">
              Conversations
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#262626] transition"
            title="Close sidebar"
          >
            <PanelLeftClose className="w-4 h-4" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={() => {
              onNewChat();
              if (window.innerWidth < 768) onClose();
            }}
            className="w-full flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-semibold text-black bg-gradient-to-r from-[#D4AF37] to-[#C59B27] hover:from-[#E5BF45] hover:to-[#D4AF37] transition shadow-md shadow-[#D4AF37]/10"
          >
            <Plus className="w-4 h-4 stroke-[2.5]" />
            <span>New chat</span>
          </button>
        </div>

        {/* Recent Chats Section */}
        <div className="flex-1 overflow-y-auto px-2 py-1 space-y-1">
          <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-500">
            Recent Chats
          </div>

          {threads.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-gray-500">
              <Sparkles className="w-5 h-5 mx-auto mb-2 text-gray-600 opacity-60" />
              <span>No past conversations yet. Start a new chat!</span>
            </div>
          ) : (
            threads.map((thread) => {
              const isActive = thread.id === activeThreadId;
              return (
                <div
                  key={thread.id}
                  onClick={() => {
                    onSelectThread(thread.id);
                    if (window.innerWidth < 768) onClose();
                  }}
                  className={`group relative flex items-center gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer text-xs transition select-none ${
                    isActive
                      ? 'bg-[#262626] text-white font-medium shadow-sm border border-[#333333]'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-[#212121]'
                  }`}
                >
                  <MessageSquare
                    className={`w-3.5 h-3.5 shrink-0 transition ${
                      isActive ? 'text-[#D4AF37]' : 'text-gray-500 group-hover:text-gray-400'
                    }`}
                  />
                  <span className="truncate flex-1 pr-6" title={thread.title}>
                    {thread.title || 'Conversation'}
                  </span>

                  {/* Delete thread icon on hover */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm('Delete this conversation thread?')) {
                        onDeleteThread(thread.id);
                      }
                    }}
                    className="absolute right-2 opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400 hover:bg-[#333333] rounded transition"
                    title="Delete thread"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Bottom Info */}
        <div className="p-3 border-t border-[#262626] text-center">
          <div className="text-[10px] text-gray-500">
            DarGlobal & Wasalt Real Estate
          </div>
        </div>
      </aside>
    </>
  );
}
