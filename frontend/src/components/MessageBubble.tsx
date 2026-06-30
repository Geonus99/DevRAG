import type { SourceReference } from "@/lib/types";
import ReferencesPanel from "./ReferencesPanel";

export interface DisplayMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  hasCode?: boolean;
  references?: SourceReference[];
}

export default function MessageBubble({ message }: { message: DisplayMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-lg px-4 py-2.5 text-sm whitespace-pre-wrap ${
          isUser ? "bg-zinc-900 text-white" : "bg-zinc-100 text-zinc-900"
        }`}
      >
        {!isUser && message.hasCode && (
          <span className="mb-1 inline-block rounded-full bg-blue-100 px-2 py-0.5 text-[11px] font-medium text-blue-700">
            코드 질문으로 감지됨
          </span>
        )}
        <div>{message.content}</div>
        {!isUser && <ReferencesPanel messageId={message.id} initialReferences={message.references} />}
      </div>
    </div>
  );
}
