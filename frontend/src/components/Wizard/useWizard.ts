import type { components } from "@/api/schema";
import { WizardScreen } from "./Wizard.constants";

type SessionStatus = components["schemas"]["SessionStatus"];

const STATUS_TO_SCREEN: Record<SessionStatus, WizardScreen> = {
  DRAFT: WizardScreen.Details,
  INVALID: WizardScreen.Details,
  DETAILS_OK: WizardScreen.Validate,
  VALIDATING: WizardScreen.Validate,
  UNAVAILABLE: WizardScreen.Validate,
  VALIDATED: WizardScreen.Review,
  LIVE: WizardScreen.Live,
};

// The backend owns which step the partner is on -- this maps `status` alone to a
// screen, never client-side step state (CLAUDE.md).
export function useWizard(status: SessionStatus) {
  const screen = STATUS_TO_SCREEN[status];
  const result = { screen };
  return result;
}
