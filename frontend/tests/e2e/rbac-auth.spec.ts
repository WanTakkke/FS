import { expect, test } from "@playwright/test";

async function mockLoginAndProfile(page: Parameters<typeof test>[0]["page"]) {
  await page.route("**/api/user/login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        code: 200,
        message: "success",
        data: {
          access_token: "access-token",
          refresh_token: "refresh-token",
          token_type: "bearer",
          expires_in: 1800,
        },
      }),
    });
  });

  await page.route("**/api/user/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        code: 200,
        message: "success",
        data: {
          id: 1,
          username: "admin",
          roles: ["管理员"],
          permissions: [
            "rbac:role:read",
            "rbac:permission:read",
          ],
        },
      }),
    });
  });
}

async function doLogin(page: Parameters<typeof test>[0]["page"]) {
  await page.goto("/login");
  await page.getByLabel("用户名").fill("admin");
  await page.getByLabel("密码").fill("123456");
  await Promise.all([
    page.waitForResponse((resp) => resp.url().includes("/api/user/login") && resp.request().method() === "POST"),
    page.getByRole("button", { name: /登\s*录/ }).click(),
  ]);
}

test("login and render rbac page", async ({ page }) => {
  await mockLoginAndProfile(page);
  await page.route("**/api/rbac/roles", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        code: 200,
        message: "success",
        data: [{ id: 1, name: "管理员", code: "admin", description: "system admin" }],
      }),
    });
  });

  await page.route("**/api/rbac/permissions", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        code: 200,
        message: "success",
        data: [{ id: 1, name: "角色读取", code: "rbac:role:read", type: "api", parent_id: null }],
      }),
    });
  });

  await doLogin(page);

  await expect(page).toHaveURL("http://127.0.0.1:5173/");
  await expect(page.getByText("当前用户：admin")).toBeVisible();

  await page.getByRole("link", { name: "RBAC 管理" }).click();
  await expect(page).toHaveURL("http://127.0.0.1:5173/rbac");
  await expect(page.getByText("角色列表")).toBeVisible();
  await expect(page.getByText("管理员")).toBeVisible();
});

test("auto refresh token on 401 then retry success", async ({ page }) => {
  await mockLoginAndProfile(page);
  let rolesHit = 0;
  let refreshHit = 0;

  await page.route("**/api/rbac/roles", async (route) => {
    rolesHit += 1;
    if (rolesHit === 1) {
      await route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "token expired" }),
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        code: 200,
        message: "success",
        data: [{ id: 2, name: "审计员", code: "auditor", description: "auditor role" }],
      }),
    });
  });

  await page.route("**/api/user/refresh", async (route) => {
    refreshHit += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        code: 200,
        message: "success",
        data: {
          access_token: "new-access-token",
          refresh_token: "new-refresh-token",
          token_type: "bearer",
          expires_in: 1800,
        },
      }),
    });
  });

  await page.route("**/api/rbac/permissions", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        code: 200,
        message: "success",
        data: [],
      }),
    });
  });

  await doLogin(page);
  await page.getByRole("link", { name: "RBAC 管理" }).click();

  await expect(page.getByText("审计员")).toBeVisible();
  await expect.poll(() => rolesHit).toBeGreaterThanOrEqual(2);
  await expect.poll(() => refreshHit).toBe(1);
});

test("text2sql business error should show message", async ({ page }) => {
  await mockLoginAndProfile(page);
  await page.route("**/api/ai/text2sql", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        code: 400,
        message: "仅支持SELECT语句",
        data: null,
      }),
    });
  });

  await doLogin(page);
  await page.getByRole("link", { name: "AI 助手" }).click();

  await page.getByRole("tab", { name: "Text2SQL" }).click();
  await page.getByLabel("自然语言问题").fill("删除成绩表全部数据");
  await page.getByRole("button", { name: "生成并执行" }).click();

  await expect(page.getByText("仅支持SELECT语句")).toBeVisible();
});
