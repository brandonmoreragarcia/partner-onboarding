import type { components } from "@/api/schema";
import { StepState } from "./StepIndicator.constants";

type SessionStatus = components["schemas"]["SessionStatus"];

const DETAILS_STATE: Record<SessionStatus, StepState> = {
  DRAFT: StepState.Current,
  INVALID: StepState.Current,
  DETAILS_OK: StepState.Done,
  VALIDATING: StepState.Done,
  VALIDATED: StepState.Done,
  UNAVAILABLE: StepState.Done,
  LIVE: StepState.Done,
};

const VALIDATE_STATE: Record<SessionStatus, StepState> = {
  DRAFT: StepState.Todo,
  INVALID: StepState.Todo,
  DETAILS_OK: StepState.Current,
  VALIDATING: StepState.Current,
  UNAVAILABLE: StepState.Current,
  VALIDATED: StepState.Done,
  LIVE: StepState.Done,
};

const REVIEW_STATE: Record<SessionStatus, StepState> = {
  DRAFT: StepState.Todo,
  INVALID: StepState.Todo,
  DETAILS_OK: StepState.Todo,
  VALIDATING: StepState.Todo,
  UNAVAILABLE: StepState.Todo,
  VALIDATED: StepState.Current,
  LIVE: StepState.Done,
};

/** Pure derivation of the 3-step indicator's state from session.status alone -- no
 * client-side step tracking, matching CLAUDE.md's "backend owns the step" rule. */
export function useStepIndicator(status: SessionStatus) {
  const stepStates: [StepState, StepState, StepState] = [
    DETAILS_STATE[status],
    VALIDATE_STATE[status],
    REVIEW_STATE[status],
  ];
  const result = { stepStates };
  return result;
}
