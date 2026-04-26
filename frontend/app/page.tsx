"use client";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { sendChat, type Message } from "@/lib/api";

type AssistantTurn = { role: "assistant"; content: string; queries: string[] };
type UserTurn = { role: "user"; content: string };
type Turn = UserTurn | AssistantTurn;

function stripSqlFromContent(content: string): string {
  let out = content.replace(/\n#{1,6}\s*Queries\s*\n[\s\S]*$/i, "");
  out = out.replace(/```sql\b[\s\S]*?```/gi, "");
  return out.trimEnd();
}

function SqlFooter({ queries }: { queries: string[] }) {
  const [open, setOpen] = useState(false);
  if (queries.length === 0) return null;
  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen((o) => !o)}
        className="text-xs text-gray-400 hover:text-gray-600 underline-offset-2 hover:underline"
      >
        {open ? "Hide queries" : `Show ${queries.length} quer${queries.length === 1 ? "y" : "ies"}`}
      </button>
      {open && (
        <pre className="mt-2 text-xs bg-gray-50 border border-gray-200 rounded p-3 overflow-x-auto whitespace-pre-wrap">
          {queries.join("\n\n---\n\n")}
        </pre>
      )}
    </div>
  );
}

function LoadingDots() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}

export default function Page() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns, loading]);

  async function handleSubmit() {
    const text = input.trim();
    if (!text || loading) return;
    if (text.length > 4000) return;
    const newTurns: Turn[] = [...turns, { role: "user", content: text }];
    setTurns(newTurns);
    setInput("");
    setLoading(true);
    try {
      const apiMessages: Message[] = newTurns.map((t) => ({
        role: t.role,
        content: t.content,
      }));
      const res = await sendChat(apiMessages);
      setTurns([
        ...newTurns,
        { role: "assistant", content: res.text, queries: res.queries },
      ]);
    } catch {
      setTurns([
        ...newTurns,
        {
          role: "assistant",
          content: "Something went wrong. Please try again.",
          queries: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white px-4 py-3 shrink-0">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-base font-semibold text-gray-800">
            Navi Manufacturing Assistant
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Ask questions about machines, products, routes, and parameters
          </p>
        </div>
      </header>

      {/* Message list */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto flex flex-col gap-4">
          {turns.length === 0 && (
            <p className="text-center text-sm text-gray-400 mt-16">
              Ask a question to get started.
            </p>
          )}
          {turns.map((turn, i) =>
            turn.role === "user" ? (
              <div key={i} className="flex justify-end">
                <div className="max-w-[80%] bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm whitespace-pre-wrap">
                  {turn.content}
                </div>
              </div>
            ) : (
              <div key={i} className="flex justify-start">
                <div className="max-w-[90%] bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 text-sm shadow-sm">
                  <div className="prose prose-sm max-w-none prose-pre:bg-gray-50 prose-pre:text-xs prose-table:text-xs">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {stripSqlFromContent(turn.content)}
                    </ReactMarkdown>
                  </div>
                  <SqlFooter queries={turn.queries} />
                </div>
              </div>
            )
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm shadow-sm">
                <LoadingDots />
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>
      </main>

      {/* Input footer */}
      <footer className="border-t border-gray-200 bg-white px-4 py-3 shrink-0">
        <div className="max-w-3xl mx-auto flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            maxLength={4000}
            rows={1}
            placeholder="Ask about machines, products, or routes… (Enter to send, Shift+Enter for newline)"
            className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 leading-relaxed"
            style={{ maxHeight: "8rem", overflowY: "auto" }}
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !input.trim()}
            className="shrink-0 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
        {input.length > 3800 && (
          <p className="max-w-3xl mx-auto mt-1 text-xs text-amber-600">
            {4000 - input.length} characters remaining
          </p>
        )}
      </footer>
    </div>
  );
}
