import React, { useState } from 'react';
import { Copy, Check, ExternalLink } from 'lucide-react';

function formatHumanContent(content) {
  if (!content) return '';
  // 1. Strip thinking process block if any
  let cleaned = content.replace(
    /(?is)^.*?(?:here(?:'s|\s+is)\s+(?:a\s+)?thinking\s+process|thinking\s+process|chain\s+of\s+thought):?[\s\S]*?(?=\n\n[A-Z0-9#•\*\-][^\n]*\n\n|\n\n(?=[A-Z][a-z]+ (?:by|is|in|offers|features|welcomes))|\Z)/i,
    ''
  );
  if (!cleaned || cleaned.trim().length < 20) {
    cleaned = content;
  }

  // 2. Remove AI asterisks and format clean human bullets
  cleaned = cleaned.replace(/\*\*(.*?)\*\*/g, '$1');
  cleaned = cleaned.replace(/\*([^\*\n]+)\*/g, '$1');
  cleaned = cleaned.replace(/^\s*[\*\-]\s+/gm, '• ');
  cleaned = cleaned.replace(/\*/g, '');

  return cleaned.trim();
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const displayContent = isUser ? message.content : formatHumanContent(message.content);

  const handleCopy = () => {
    navigator.clipboard.writeText(displayContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="bg-[#2f2f2f] text-[#ECECEC] px-4 py-2.5 rounded-3xl max-w-[85%] text-sm leading-relaxed whitespace-pre-wrap shadow-sm">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-4 items-start mb-6">
      {/* Avatar */}
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#8C6D23] flex items-center justify-center font-bold text-black text-xs shrink-0 mt-1 shadow-sm">
        D
      </div>

      <div className="flex-1 overflow-hidden">
        {/* Assistant Markdown Content */}
        <div className="chat-prose text-sm text-[#ECECEC] leading-relaxed whitespace-pre-wrap">
          {displayContent}
        </div>

        {/* Clean Source Pills */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-[#2a2a2a]">
            <div className="text-[11px] font-medium text-gray-400 mb-2">
              Verified Sources ({message.sources.length})
            </div>
            <div className="flex flex-wrap gap-1.5">
              {message.sources.map((src, idx) => {
                const isDG = src.source === 'DarGlobal';
                return (
                  <a
                    key={idx}
                    href={src.url || '#'}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#171717] hover:bg-[#282828] border border-[#2f2f2f] text-[11px] text-gray-300 transition shrink-0 group"
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        isDG ? 'bg-[#D4AF37]' : 'bg-emerald-400'
                      }`}
                    ></span>
                    <span className="font-medium text-white group-hover:text-[#D4AF37] truncate max-w-[150px]">
                      {src.title}
                    </span>
                    {src.price && (
                      <span className="text-gray-500 font-mono text-[10px]">
                        • {src.price}
                      </span>
                    )}
                    <ExternalLink className="w-3 h-3 text-gray-500 group-hover:text-gray-300 ml-0.5" />
                  </a>
                );
              })}
            </div>
          </div>
        )}

        {/* Latency & Actions */}
        <div className="mt-2 flex items-center gap-3 text-[11px] text-gray-500">
          {message.latency_ms && <span>{message.latency_ms} ms</span>}
          <button
            onClick={handleCopy}
            className="hover:text-gray-300 transition flex items-center gap-1"
            title="Copy text"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-emerald-400" />
                <span className="text-emerald-400">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
