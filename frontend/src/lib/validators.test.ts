import { describe, expect, it } from "vitest";

import {
  assertNonEmptyString,
  assertNumberInRange,
  assertPositiveInt,
  assertPositiveIntArray,
} from "./validators";

describe("validators", () => {
  it("assertNonEmptyString throws on blank", () => {
    expect(() => assertNonEmptyString("   ", "字段")).toThrow("字段不能为空");
  });

  it("assertNumberInRange throws when out of range", () => {
    expect(() => assertNumberInRange(2.5, "temperature", 0, 2)).toThrow("temperature必须在0~2之间");
  });

  it("assertPositiveInt throws on invalid number", () => {
    expect(() => assertPositiveInt(0, "ID")).toThrow("ID必须是正整数");
  });

  it("assertPositiveIntArray throws when contains invalid value", () => {
    expect(() => assertPositiveIntArray([1, 2, -1], "列表")).toThrow("列表必须全部为正整数");
  });
});
