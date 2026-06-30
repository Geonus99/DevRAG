"use client";

import { useState } from "react";
import { ApiError, getMessageReferences } from "@/lib/api";
import type { SourceReference } from "@/lib/types";

interface Props {
  messageId: string;
  initialReferences?: SourceReference[];
}

export default function ReferencesPanel({ messageId, initialReferences }: Props) {
  const [open, setOpen] = useState(false);
  const [references, setReferences] = useState<SourceReference[] | null>(initialReferences ?? null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function toggle() {
    const next = !open;
    setOpen(next);
    if (next && references === null) {
      setLoading(true);
      try {
        const data = await getMessageReferences(messageId);
        setReferences(data);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "출처를 불러오지 못했습니다");
      } finally {
        setLoading(false);
      }
    }
  }

  return (
    <div className="mt-2">
      <button
        onClick={toggle}
        className="text-xs font-medium text-zinc-500 underline-offset-2 hover:text-zinc-800 hover:underline"
      >
        {open ? "출처 숨기기" : `출처 보기 (Retrieval Debug View)`}
      </button>
      {open && (
        <div className="mt-2 space-y-2">
          {loading && <p className="text-xs text-zinc-400">불러오는 중...</p>}
          {error && <p className="text-xs text-red-600">{error}</p>}
          {references?.length === 0 && (
            <p className="text-xs text-zinc-400">참고한 청크가 없습니다.</p>
          )}
          {references?.map((reference) => (
            <div key={reference.id} className="rounded-md border border-zinc-200 bg-zinc-50 p-2.5 text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="font-medium text-zinc-800">
                  {reference.chunk?.title ?? "Untitled"}
                </span>
                <span className="shrink-0 rounded-full bg-zinc-200 px-2 py-0.5 font-mono text-[11px] text-zinc-700">
                  score {reference.relevance_score?.toFixed(3) ?? "-"}
                </span>
              </div>
              {reference.chunk?.page_url && (
                <a
                  href={reference.chunk.page_url}
                  target="_blank"
                  rel="noreferrer"
                  className="block truncate text-[11px] text-blue-600 hover:underline"
                >
                  {reference.chunk.page_url}
                </a>
              )}
              <p className="mt-1 line-clamp-3 text-zinc-600">{reference.chunk?.content}</p>
              <p className="mt-1 text-[11px] text-zinc-400">
                chunk_id: {reference.chunk_id}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
