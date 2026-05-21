import { describe, expect, it } from "vitest";

import { parseSse } from "@/lib/sse";

describe("parseSse", () => {
  it("parses an event name and JSON data", () => {
    const events = parseSse('event: score_corrected\ndata: {"to":7.6}\n\n');
    expect(events).toHaveLength(1);
    expect(events[0].stage).toBe("score_corrected");
    expect(events[0].data.to).toBe(7.6);
  });

  it("parses multiple frames in order", () => {
    const events = parseSse('event: a\ndata: {}\n\nevent: complete\ndata: {"final_score":80}\n\n');
    expect(events.map((e) => e.stage)).toEqual(["a", "complete"]);
    expect(events[1].data.final_score).toBe(80);
  });

  it("ignores blank buffers", () => {
    expect(parseSse("\n\n")).toEqual([]);
  });
});
