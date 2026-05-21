/** Minimal SSE frame parser + a fetch-based event-stream reader. */

export interface SseEvent {
  stage: string;
  data: Record<string, unknown>;
}

/** Parse one or more `event:`/`data:` frames out of an SSE text buffer. */
export function parseSse(buffer: string): SseEvent[] {
  const events: SseEvent[] = [];
  for (const frame of buffer.split("\n\n")) {
    const trimmed = frame.trim();
    if (!trimmed) continue;
    let stage = "message";
    let data: Record<string, unknown> = {};
    for (const line of trimmed.split("\n")) {
      if (line.startsWith("event:")) {
        stage = line.slice("event:".length).trim();
      } else if (line.startsWith("data:")) {
        const raw = line.slice("data:".length).trim();
        try {
          data = JSON.parse(raw) as Record<string, unknown>;
        } catch {
          data = { raw };
        }
      }
    }
    events.push({ stage, data });
  }
  return events;
}

/** Stream POST an evaluation and invoke `onEvent` per SSE frame. */
export async function streamPost(
  url: string,
  body: unknown,
  onEvent: (e: SseEvent) => void,
): Promise<void> {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.body) return;
  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lastBreak = buffer.lastIndexOf("\n\n");
    if (lastBreak !== -1) {
      const ready = buffer.slice(0, lastBreak);
      buffer = buffer.slice(lastBreak + 2);
      for (const e of parseSse(ready)) onEvent(e);
    }
  }
  for (const e of parseSse(buffer)) onEvent(e);
}
