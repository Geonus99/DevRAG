import type { SourceStatus } from "@/lib/types";

const STYLES: Record<SourceStatus, string> = {
  PENDING: "bg-zinc-100 text-zinc-600",
  PROCESSING: "bg-amber-100 text-amber-700",
  COMPLETED: "bg-emerald-100 text-emerald-700",
  FAILED: "bg-red-100 text-red-700",
};

const LABELS: Record<SourceStatus, string> = {
  PENDING: "대기중",
  PROCESSING: "처리중",
  COMPLETED: "완료",
  FAILED: "실패",
};

export default function StatusBadge({ status }: { status: SourceStatus }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[status]}`}
    >
      {LABELS[status]}
    </span>
  );
}
