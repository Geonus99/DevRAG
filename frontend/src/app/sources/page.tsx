"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, createSource, deleteSource, ingestSource, listSources } from "@/lib/api";
import type { KnowledgeSource, SourceType } from "@/lib/types";
import SourceForm from "@/components/SourceForm";
import SourceTable from "@/components/SourceTable";

const POLL_INTERVAL_MS = 3000;

export default function SourcesPage() {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyIds, setBusyIds] = useState<Set<string>>(new Set());
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listSources();
      setSources(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "목록을 불러오지 못했습니다");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    listSources()
      .then((data) => {
        setSources(data);
        setError(null);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "목록을 불러오지 못했습니다"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const hasProcessing = sources.some((source) => source.status === "PROCESSING");
    if (hasProcessing && !pollRef.current) {
      pollRef.current = setInterval(refresh, POLL_INTERVAL_MS);
    }
    if (!hasProcessing && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [sources, refresh]);

  async function handleCreate(payload: { source_name: string; source_type: SourceType; source_url: string }) {
    await createSource(payload);
    await refresh();
  }

  async function handleIngest(id: string) {
    setBusyIds((prev) => new Set(prev).add(id));
    try {
      await ingestSource(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "수집 실행에 실패했습니다");
    } finally {
      setBusyIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("이 문서와 관련 청크를 모두 삭제할까요?")) return;
    setBusyIds((prev) => new Set(prev).add(id));
    try {
      await deleteSource(id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "삭제에 실패했습니다");
    } finally {
      setBusyIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-8">
      <div>
        <h1 className="text-xl font-semibold text-zinc-900">지식베이스</h1>
        <p className="text-sm text-zinc-500">
          URL 또는 PDF를 등록하면 크롤링 → 청킹 → 임베딩까지 자동으로 처리됩니다.
        </p>
      </div>

      <SourceForm onSubmit={handleCreate} />

      {error && <p className="text-sm text-red-600">{error}</p>}

      {loading ? (
        <p className="text-sm text-zinc-500">불러오는 중...</p>
      ) : (
        <SourceTable sources={sources} busyIds={busyIds} onIngest={handleIngest} onDelete={handleDelete} />
      )}
    </div>
  );
}
