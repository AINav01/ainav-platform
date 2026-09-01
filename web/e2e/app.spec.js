const { test, expect } = require("@playwright/test");
const AxeBuilder = require("@axe-core/playwright").default;

test("application workspaces stay catalog-honest", async ({ page }) => {
  await page.goto("/app.html?v=2600#floor");
  await expect(page.locator("#app-write-rail")).toBeVisible();
  await expect(page.locator("ainav-honest h2").filter({ hasText: "Not a priced round" })).toBeVisible();
  await page.locator('.app-rail a[data-workspace="capital"]').click();
  await expect(page.locator("#workspace-capital")).toBeVisible();
  await expect(page.locator("#workspace-capital .price").filter({ hasText: "refused" })).toBeVisible();
  await expect(page.locator("#app-capital-scenarios")).toBeVisible();
  await page.locator('.app-rail a[data-workspace="business"]').click();
  await expect(page.locator("#workspace-business")).toBeVisible();
  await expect(page.locator("#workspace-business h1")).toHaveText("Operating company. Close is open.");
  await expect(page.locator("#app-business-close .price").filter({ hasText: "open" }).first()).toBeVisible();
  await page.locator('.app-rail a[data-workspace="programs"]').click();
  await expect(page.locator("#workspace-programs")).toBeVisible();
  await expect(page.locator("#workspace-programs h1")).toHaveText("Qualify. Do not claim.");
  const body = (await page.content()).toLowerCase();
  expect(body).not.toContain("nvidia inception member");
});

test("kit and identify refuse admit and CMS", async ({ page }) => {
  await page.goto("/kit.html?v=2600");
  await expect(page.locator("h1")).toHaveText("Licensed tools. Same law.");
  await page.goto("/identify.html?v=2600");
  await expect(page.locator("h1")).toHaveText("Identify is not admit.");
});

test("axe on the application floor", async ({ page }) => {
  await page.goto("/app.html?v=2600#floor");
  const results = await new AxeBuilder({ page }).analyze();
  const serious = results.violations.filter((item) =>
    ["serious", "critical"].includes(item.impact)
  );
  expect(serious, JSON.stringify(serious, null, 2)).toEqual([]);
});
