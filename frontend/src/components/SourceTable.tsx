"use client";

import type { KnowledgeSource } from "@/lib/types";
import StatusBadge from "./StatusBadge";

interface Props {
  sources: KnowledgeSource[];
  busyIds: Set<string>;
  onIngest: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function SourceTable({ sources, busyIds, onIngest, onDelete }: Props) {
  if (sources.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500">
        등록된 문서가 없습니다. 위에서 URL 또는 PDF를 등록해보세요.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-zinc-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-zinc-200 bg-zinc-50 text-xs uppercase text-zinc-500">
          <tr>
            <th className="px-4 py-2">이름</th>
            <th className="px-4 py-2">타입</th>
            <th className="px-4 py-2">상태</th>
            <th className="px-4 py-2">수집 페이지</th>
            <th className="px-4 py-2">청크 수</th>
            <th className="px-4 py-2">작업</th>
          </tr>
        </thead>
        <tbody>
          {sources.map((source) => {
            const isBusy = busyIds.has(source.id);
            return (
              <tr key={source.id} className="border-b border-zinc-100 last:border-0">
                <td className="max-w-xs px-4 py-3">
                  <div className="font-medium text-zinc-900">{source.source_name}</div>
                  <div className="truncate text-xs text-zinc-500">{source.source_url}</div>
                  {source.error_message && (
                    <div className="mt-1 text-xs text-red-600">{source.error_message}</div>
                  )}
                </td>
                <td className="px-4 py-3 text-zinc-600">{source.source_type}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={source.status} />
                </td>
                <td className="px-4 py-3 text-zinc-600">{source.crawled_pages}</td>
                <td className="px-4 py-3 text-zinc-600">{source.chunk_count}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button
                      onClick={() => onIngest(source.id)}
                      disabled={isBusy || source.status === "PROCESSING"}
                      className="rounded-md border border-zinc-300 px-2.5 py-1 text-xs font-medium text-zinc-700 hover:bg-zinc-50 disabled:opacity-50"
                    >
                      {source.status === "PROCESSING" ? "처리중" : source.status === "FAILED" ? "재시도" : "수집 시작"}
                    </button>
                    <button
                      onClick={() => onDelete(source.id)}
                      disabled={isBusy}
                      className="rounded-md border border-red-200 px-2.5 py-1 text-xs font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
                    >
                      삭제
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
