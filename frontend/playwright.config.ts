import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  // Single hardcoded partner -> exactly one session can exist at a time. fullyParallel:
  // false only stops parallelism within one file; workers: 1 is what actually forces
  // every spec file to run one after another instead of racing the same session.
  fullyParallel: false,
  workers: 1,
  webServer: {
    command: "npm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: "http://localhost:5173",
  },
});
