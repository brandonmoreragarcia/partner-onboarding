import type { components } from "@/api/schema";
import { BlueprintCorners, CloudOffIcon, RefreshIcon, SpinnerIcon } from "@/components/icons";
import { StepIndicator } from "@/components/StepIndicator/StepIndicator";
import {
  ACCOUNT_ID_LABEL,
  COMPANY_NAME_LABEL,
  EYEBROW_SUFFIX,
  HEADING_TEXT,
  LABEL_VALIDATING,
  MODE_COPY,
  ValidateStepMode,
} from "./ValidateStep.constants";
import { useValidateStep } from "./useValidateStep";

type SessionOut = components["schemas"]["SessionOut"];

interface Props {
  session: SessionOut;
}

// Handles DETAILS_OK (ready to trigger), VALIDATING (pending) and UNAVAILABLE.
// VALIDATED lives entirely in ReviewStep -- see D13/D14 in ai-log/03-frontend.md.
export function ValidateStep({ session }: Props) {
  const { mode, busy, showCompanyFields, showRefreshIcon, errorMessage, handleValidate } = useValidateStep(session);
  const copy = MODE_COPY[mode];
  const buttonLabel = busy ? LABEL_VALIDATING : copy.buttonLabel;
  const screenClassName = mode === ValidateStepMode.Unavailable ? "screen st-none" : "screen st-wait";

  return (
    <section className={screenClassName}>
      <div className="screen-inner">
        <div className="eyebrow">Step 2 of 3{EYEBROW_SUFFIX[mode]}</div>
        <StepIndicator session={session} />

        <div className="head-row">
          <h3>{HEADING_TEXT}</h3>
          <span className="status-tag" data-testid="validation-status">
            {copy.statusTag}
          </span>
        </div>

        <div className="panel blueprint">
          <BlueprintCorners />
          {mode === ValidateStepMode.Unavailable ? <CloudOffIcon /> : <SpinnerIcon />}
          <div>
            <div className="panel-title">{copy.panelTitle}</div>
            <p className="panel-body">{copy.panelBody}</p>
            {copy.panelNote && <p className="panel-note">{copy.panelNote}</p>}
          </div>
        </div>

        {showCompanyFields && (
          <div className="field-row">
            <div className="field">
              <label>{COMPANY_NAME_LABEL}</label>
              <input className="input" value={session.companyName ?? ""} disabled />
            </div>
            <div className="field">
              <label>{ACCOUNT_ID_LABEL}</label>
              <input className="input" value={session.accountId ?? ""} disabled />
            </div>
          </div>
        )}

        {errorMessage && (
          <p role="alert" className="text-muted">
            {errorMessage}
          </p>
        )}

        <button type="button" className="btn btn-primary blueprint" disabled={busy} onClick={handleValidate}>
          <BlueprintCorners />
          {showRefreshIcon && <RefreshIcon />}
          {buttonLabel}
        </button>
      </div>
    </section>
  );
}
