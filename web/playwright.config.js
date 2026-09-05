const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./e2e",
  timeout: 30000,
  use: {
    baseURL: process.env.AINAV_BASE || "http://127.0.0.1:8765",
    browserName: "chromium",
  },
  webServer: {
    command: "python3 -m http.server 8765 --directory ../institute",
    port: 8765,
    reuseExistingServer: true,
  },
});
