const { test, expect } = require("@playwright/test");
const AxeBuilder = require("@axe-core/playwright").default;

test("application workspaces stay catalog-honest", async ({ page }) => {
  await page.goto("/app.html?v=2590#floor");
  await expect(page.locator("#app-write-rail")).toBeVisible();
  await expect(page.getByText("Not a priced round")).toBeVisible();
  await page.locator('.app-rail a[data-workspace="capital"]').click();
  await expect(page.locator("#workspace-capital")).toBeVisible();
  await expect(page.getByText("refused")).toBeVisible();
  await page.locator('.app-rail a[data-workspace="programs"]').click();
  await expect(page.locator("#workspace-programs")).toBeVisible();
  await expect(page.getByText("Qualify. Do not claim.")).toBeVisible();
  const body = (await page.content()).toLowerCase();
  expect(body).not.toContain("nvidia inception member");
});

test("kit and identify refuse admit and CMS", async ({ page }) => {
  await page.goto("/kit.html?v=2590");
  await expect(page.getByText("Licensed tools. Same law.")).toBeVisible();
  await page.goto("/identify.html?v=2590");
  await expect(page.getByText("Identify is not admit.")).toBeVisible();
});

test("axe on the application floor", async ({ page }) => {
  await page.goto("/app.html?v=2590#floor");
  const results = await new AxeBuilder({ page }).analyze();
  const serious = results.violations.filter((item) =>
    ["serious", "critical"].includes(item.impact)
  );
  expect(serious, JSON.stringify(serious, null, 2)).toEqual([]);
});
