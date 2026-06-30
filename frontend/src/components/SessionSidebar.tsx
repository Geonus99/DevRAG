"use client";

import type { ChatSession } from "@/lib/types";

interface Props {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
}

export default function SessionSidebar({ sessions, activeSessionId, onSelect, onNewChat }: Props) {
  return (
    <aside className="flex w-64 flex-col border-r border-zinc-200 bg-zinc-50">
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full rounded-md bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-700"
        >
          + 새 대화
        </button>
      </div>
      <div className="flex-1 overflow-y-auto px-2 pb-3">
        {sessions.length === 0 && (
          <p className="px-2 py-4 text-xs text-zinc-400">대화 이력이 없습니다</p>
        )}
        {sessions.map((session) => (
          <button
            key={session.id}
            onClick={() => onSelect(session.id)}
            className={`mb-1 w-full truncate rounded-md px-3 py-2 text-left text-sm ${
              session.id === activeSessionId
                ? "bg-zinc-200 text-zinc-900"
                : "text-zinc-600 hover:bg-zinc-100"
            }`}
            title={session.title}
          >
            {session.title}
          </button>
        ))}
      </div>
    </aside>
  );
}
