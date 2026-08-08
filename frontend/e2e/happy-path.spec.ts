import { expect, test } from "@playwright/test";
import { resetDb } from "./reset-db";

// Requires the backend running separately on :8000 against the real Postgres dev DB
// (see README "Running it locally") -- Playwright's webServer only manages the
// frontend dev server, not the API.

test.beforeEach(() => {
  resetDb();
});

test("full happy path: details -> validate -> review -> go live", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Company details" })).toBeVisible();

  await page.getByLabel("Company name").fill("Acme Robotics");
  await page.getByLabel("Account ID").fill("acct_8841");
  await page.getByLabel("API key").fill("valid-key");
  await page.getByRole("button", { name: "Continue" }).click();

  await expect(page.getByRole("heading", { name: "Validate integration" })).toBeVisible();
  await expect(page.getByTestId("validation-status")).toHaveText("Ready");
  await page.getByRole("button", { name: "Validate integration" }).click();

  await expect(page.getByRole("heading", { name: "Review & go live" })).toBeVisible();
  await expect(page.getByText("Item One")).toBeVisible();
  await expect(page.getByText("Item Two")).toBeVisible();
  // valid (no warnings) -- the Warnings block must not render for this outcome.
  await expect(page.getByText("Warnings", { exact: true })).not.toBeVisible();

  await page.getByRole("button", { name: "Go live" }).click();

  await expect(page.getByText("You're live")).toBeVisible();
  await expect(page.getByText("Acme Robotics is now live with 2 item(s) synced.")).toBeVisible();
});
