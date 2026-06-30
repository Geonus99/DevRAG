"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError, getSession, listSessions, sendChatMessage } from "@/lib/api";
import type { ChatSession } from "@/lib/types";
import SessionSidebar from "@/components/SessionSidebar";
import MessageBubble, { type DisplayMessage } from "@/components/MessageBubble";

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingSession, setLoadingSession] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listSessions()
      .then(setSessions)
      .catch((err) => setError(err instanceof ApiError ? err.message : "세션 목록을 불러오지 못했습니다"));
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function handleSelectSession(id: string) {
    setActiveSessionId(id);
    setLoadingSession(true);
    setError(null);
    try {
      const detail = await getSession(id);
      setMessages(
        detail.messages.map((m) => ({ id: m.id, role: m.role, content: m.message }))
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "대화를 불러오지 못했습니다");
    } finally {
      setLoadingSession(false);
    }
  }

  function handleNewChat() {
    setActiveSessionId(null);
    setMessages([]);
    setError(null);
  }

  async function handleSend() {
    const message = input.trim();
    if (!message || sending) return;

    setSending(true);
    setError(null);
    setInput("");
    setMessages((prev) => [...prev, { id: `local-${Date.now()}`, role: "user", content: message }]);

    try {
      const response = await sendChatMessage({ message, session_id: activeSessionId });
      setMessages((prev) => [
        ...prev,
        {
          id: response.assistant_message_id,
          role: "assistant",
          content: response.answer,
          hasCode: response.has_code,
          references: response.references,
        },
      ]);

      if (!activeSessionId) {
        setActiveSessionId(response.session_id);
        const updated = await listSessions();
        setSessions(updated);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "답변을 받지 못했습니다");
    } finally {
      setSending(false);
    }
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-1">
      <SessionSidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelect={handleSelectSession}
        onNewChat={handleNewChat}
      />

      <div className="flex flex-1 flex-col">
        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
          {loadingSession ? (
            <p className="text-sm text-zinc-400">대화를 불러오는 중...</p>
          ) : messages.length === 0 ? (
            <p className="text-sm text-zinc-400">
              등록된 문서 범위 내에서 질문해보세요. 코드를 ```로 감싸서 보내면 코드 질문으로 인식합니다.
            </p>
          ) : (
            messages.map((message) => <MessageBubble key={message.id} message={message} />)
          )}
        </div>

        {error && <p className="px-6 text-sm text-red-600">{error}</p>}

        <div className="border-t border-zinc-200 p-4">
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="질문을 입력하세요 (Shift+Enter로 줄바꿈)"
              rows={2}
              className="flex-1 resize-none rounded-md border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-zinc-500"
            />
            <button
              onClick={handleSend}
              disabled={sending || !input.trim()}
              className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
            >
              {sending ? "전송 중..." : "전송"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
