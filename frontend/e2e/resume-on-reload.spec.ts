import { expect, test } from "@playwright/test";
import { resetDb } from "./reset-db";

// Requires the backend running separately on :8000 against the real Postgres dev DB
// (see README "Running it locally") -- Playwright's webServer only manages the
// frontend dev server, not the API.
//
// Nothing here is stored client-side (no localStorage, no step state) -- resume only
// works because GET/POST /sessions always reflects the backend's current status.

test.beforeEach(() => {
  resetDb();
});

test("reload mid-flow resumes at the correct step, twice", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Company name").fill("Acme Robotics");
  await page.getByLabel("Account ID").fill("acct_8841");
  await page.getByLabel("API key").fill("valid-key");
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(page.getByTestId("validation-status")).toHaveText("Ready");

  // Reload while DETAILS_OK -- must stay on Validate (Ready), not reset to Details.
  await page.reload();
  await expect(page.getByRole("heading", { name: "Validate integration" })).toBeVisible();
  await expect(page.getByTestId("validation-status")).toHaveText("Ready");
  // The read-only context fields prove the submitted details survived too.
  await expect(page.getByLabel("Company name")).toHaveValue("Acme Robotics");

  await page.getByRole("button", { name: "Validate integration" }).click();
  await expect(page.getByRole("heading", { name: "Review & go live" })).toBeVisible();

  // Reload while VALIDATED -- must stay on Review, items still shown.
  await page.reload();
  await expect(page.getByRole("heading", { name: "Review & go live" })).toBeVisible();
  await expect(page.getByText("Item One")).toBeVisible();
  await expect(page.getByText("Item Two")).toBeVisible();

  await page.getByRole("button", { name: "Go live" }).click();
  await expect(page.getByText("You're live")).toBeVisible();

  // Reload while LIVE -- terminal state, must still show Live, not regress.
  await page.reload();
  await expect(page.getByText("You're live")).toBeVisible();
});
