import { getErrorMessage } from "@/api/errors";
import type { components } from "@/api/schema";
import { useValidate } from "@/hooks/useValidate";
import { ValidateStepMode } from "./ValidateStep.constants";

type SessionOut = components["schemas"]["SessionOut"];
type SessionStatus = components["schemas"]["SessionStatus"];

const STATUS_TO_MODE: Partial<Record<SessionStatus, ValidateStepMode>> = {
  DETAILS_OK: ValidateStepMode.Ready,
  VALIDATING: ValidateStepMode.Pending,
  UNAVAILABLE: ValidateStepMode.Unavailable,
};

export function useValidateStep(session: SessionOut) {
  const { mutate, isPending, error } = useValidate();

  const mode = STATUS_TO_MODE[session.status] ?? ValidateStepMode.Ready;
  const busy = isPending || mode === ValidateStepMode.Pending;
  const showCompanyFields = mode !== ValidateStepMode.Unavailable;
  const showRefreshIcon = mode === ValidateStepMode.Unavailable && !isPending;
  const errorMessage = error ? getErrorMessage(error) : null;
  const handleValidate = () => mutate();

  const result = { mode, busy, showCompanyFields, showRefreshIcon, errorMessage, handleValidate };
  return result;
}
