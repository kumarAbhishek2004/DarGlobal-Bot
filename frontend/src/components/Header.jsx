import React from 'react';
import { Plus, PanelLeft } from 'lucide-react';

export default function Header({ onToggleSidebar, isSidebarOpen, onNewChat, activeThreadTitle }) {
  return (
    <header className="h-14 flex items-center justify-between px-4 border-b border-[#2d2d2d] bg-[#212121]/95 shrink-0 z-20">
      <div className="flex items-center gap-3">
        {/* Sidebar Toggle Button */}
        <button
          onClick={onToggleSidebar}
          className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#2f2f2f] transition"
          title={isSidebarOpen ? "Hide conversations" : "Show conversations"}
        >
          <PanelLeft className="w-5 h-5" />
        </button>

        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#8C6D23] flex items-center justify-center font-bold text-black text-xs shadow-sm">
            D
          </div>
          <span className="font-semibold text-sm text-white tracking-wide hidden sm:inline">
            DarGlobal AI
          </span>
          {activeThreadTitle && (
            <>
              <span className="text-gray-600 hidden sm:inline">/</span>
              <span className="text-xs text-gray-400 truncate max-w-[200px] hidden sm:inline">
                {activeThreadTitle}
              </span>
            </>
          )}
        </div>
      </div>

      {/* New Chat Button */}
      <button
        onClick={onNewChat}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-gray-300 hover:text-white bg-[#2f2f2f] hover:bg-[#383838] border border-[#3d3d3d] transition shadow-sm"
        title="Start new conversation"
      >
        <Plus className="w-3.5 h-3.5" />
        <span>New chat</span>
      </button>
    </header>
  );
}
