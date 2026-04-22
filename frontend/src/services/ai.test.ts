import { describe, expect, it } from "vitest";

import { chatWithAi, text2sql } from "./ai";

describe("ai service payload validation", () => {
  it("chatWithAi validates message", async () => {
    await expect(chatWithAi({ message: "   " })).rejects.toThrow("对话内容不能为空");
  });

  it("chatWithAi validates temperature", async () => {
    await expect(chatWithAi({ message: "test", temperature: 3 })).rejects.toThrow("temperature必须在0~2之间");
  });

  it("text2sql validates question", async () => {
    await expect(text2sql({ question: "" })).rejects.toThrow("查询问题不能为空");
  });

  it("text2sql validates max_rows", async () => {
    await expect(text2sql({ question: "q", max_rows: 500 })).rejects.toThrow("max_rows必须在1~200之间");
  });
});
