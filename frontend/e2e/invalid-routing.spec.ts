import { execSync } from "node:child_process";
import { expect, test } from "@playwright/test";

// Requires the backend running separately on :8000 against the real Postgres dev DB
// (see README "Running it locally") -- Playwright's webServer only manages the
// frontend dev server, not the API.

function resetDb() {
  execSync(
    `PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH" psql -d partner_onboarding -c "DELETE FROM sessions;"`,
    { stdio: "ignore" }
  );
}

test.beforeEach(() => {
  resetDb(); // only one session exists (hardcoded partner) -- must reset between tests
});

test("INVALID routes back to the Details screen with an error banner, not a separate Validate screen", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Company name").fill("Acme Robotics");
  await page.getByLabel("Account ID").fill("acct_8841");
  await page.getByLabel("API key").fill("invalid-key");
  await page.getByRole("button", { name: "Continue" }).click();

  await expect(page.getByTestId("validation-status")).toBeVisible();
  await page.getByRole("button", { name: "Validate integration" }).click();

  // Product decision (confirmed, not assumed): stay on the Details screen with a
  // role="alert" banner -- the design's alternate "screen 2d" intermediate Validate
  // view is deliberately NOT wired in.
  const banner = page.getByRole("alert");
  await expect(banner).toBeVisible();
  await expect(banner).toContainText("The provided API key was rejected");
  await expect(page.getByRole("heading", { name: "Company details" })).toBeVisible();

  // Confirms we did NOT land on a Validate-step screen for this status.
  await expect(page.getByRole("heading", { name: "Validate integration" })).not.toBeVisible();

  // Credentials survive the round trip except the secret one, per D6 (api_key never
  // returned by the API) -- the form should show them prefilled, ready to correct.
  await expect(page.getByLabel("Company name")).toHaveValue("Acme Robotics");
  await expect(page.getByLabel("Account ID")).toHaveValue("acct_8841");
  await expect(page.getByLabel("API key")).toHaveValue("");
});
