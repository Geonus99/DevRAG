"use client";

import { useState } from "react";
import type { SourceType } from "@/lib/types";

interface Props {
  onSubmit: (payload: { source_name: string; source_type: SourceType; source_url: string }) => Promise<void>;
}

export default function SourceForm({ onSubmit }: Props) {
  const [sourceName, setSourceName] = useState("");
  const [sourceType, setSourceType] = useState<SourceType>("URL");
  const [sourceUrl, setSourceUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!sourceName.trim() || !sourceUrl.trim()) {
      setError("이름과 URL을 모두 입력해주세요");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({ source_name: sourceName.trim(), source_type: sourceType, source_url: sourceUrl.trim() });
      setSourceName("");
      setSourceUrl("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "등록에 실패했습니다");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-zinc-200 bg-white p-4">
      <h2 className="mb-3 text-sm font-semibold text-zinc-900">새 문서 등록</h2>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label className="mb-1 block text-xs font-medium text-zinc-600">문서 이름</label>
          <input
            value={sourceName}
            onChange={(e) => setSourceName(e.target.value)}
            placeholder="예: FastAPI 공식 문서"
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-zinc-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-zinc-600">타입</label>
          <select
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value as SourceType)}
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-zinc-500 sm:w-28"
          >
            <option value="URL">URL</option>
            <option value="PDF">PDF</option>
          </select>
        </div>
        <div className="flex-[2]">
          <label className="mb-1 block text-xs font-medium text-zinc-600">
            {sourceType === "PDF" ? "PDF 링크" : "문서 URL"}
          </label>
          <input
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
            placeholder="https://..."
            className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-zinc-500"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
        >
          {submitting ? "등록 중..." : "등록"}
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </form>
  );
}
