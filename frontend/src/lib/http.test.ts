import { describe, expect, it, vi } from "vitest";

vi.mock("antd", () => ({
  message: {
    error: vi.fn(),
  },
}));

import { unwrapResponse } from "./http";

describe("unwrapResponse", () => {
  it("returns data when business code is 200", async () => {
    const result = await unwrapResponse(
      Promise.resolve({
        data: {
          code: 200,
          message: "success",
          data: { value: 1 },
        },
      }),
    );

    expect(result).toEqual({ value: 1 });
  });

  it("throws when business code is not 200", async () => {
    await expect(
      unwrapResponse(
        Promise.resolve({
          data: {
            code: 400,
            message: "bad request",
            data: null,
          },
        }),
      ),
    ).rejects.toThrow("bad request");
  });
});
