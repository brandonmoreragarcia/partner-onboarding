import { execSync } from "node:child_process";

// Only one session exists (hardcoded partner, no auth) -- every e2e test must reset
// before it runs, or it inherits whatever state the previous test left behind.
export function resetDb() {
  execSync(
    `PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH" psql -d partner_onboarding -c "DELETE FROM sessions;"`,
    { stdio: "ignore" }
  );
}
