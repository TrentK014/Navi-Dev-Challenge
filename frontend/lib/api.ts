const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL!;

export type Message = { role: "user" | "assistant"; content: string };
export type ChatResponse = { text: string; queries: string[] };

export async function sendChat(messages: Message[]): Promise<ChatResponse> {
  const res = await fetch(`${BACKEND}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`Request failed (${res.status}): ${detail}`);
  }
  return res.json();
}
