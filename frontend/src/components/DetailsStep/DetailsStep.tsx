import type { components } from "@/api/schema";
import { ArrowRightIcon, BlueprintCorners } from "@/components/icons";
import { StepIndicator } from "@/components/StepIndicator/StepIndicator";
import {
  ACCOUNT_ID_LABEL,
  ACCOUNT_ID_PLACEHOLDER,
  API_KEY_LABEL,
  API_KEY_PLACEHOLDER,
  COMPANY_NAME_LABEL,
  COMPANY_NAME_PLACEHOLDER,
  HEADING_TEXT,
  INSTRUCTION_TEXT,
  INVALID_BANNER_TITLE,
  LABEL_CONTINUE,
  LABEL_SAVING,
} from "./DetailsStep.constants";
import { useDetailsStep } from "./useDetailsStep";

type SessionOut = components["schemas"]["SessionOut"];

interface Props {
  session: SessionOut;
}

export function DetailsStep({ session }: Props) {
  const {
    companyName,
    accountId,
    apiKey,
    isPending,
    errorMessage,
    showInvalidBanner,
    lastError,
    handleCompanyNameChange,
    handleAccountIdChange,
    handleApiKeyChange,
    handleSubmit,
  } = useDetailsStep(session);
  const buttonLabel = isPending ? LABEL_SAVING : LABEL_CONTINUE;

  return (
    <section className="screen st-wait">
      <div className="screen-inner">
        <div className="eyebrow">Step 1 of 3</div>
        <StepIndicator session={session} />

        <h3>{HEADING_TEXT}</h3>
        <p className="text-muted instruction-text">{INSTRUCTION_TEXT}</p>

        {showInvalidBanner && (
          <div className="warnings-block st-err" role="alert">
            <div className="warnings-title">{INVALID_BANNER_TITLE}</div>
            <p>{lastError}. Please correct your details below.</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="details-form">
          <div className="field">
            <label htmlFor="details-company">{COMPANY_NAME_LABEL}</label>
            <input
              id="details-company"
              className="input"
              placeholder={COMPANY_NAME_PLACEHOLDER}
              value={companyName}
              onChange={handleCompanyNameChange}
              required
              disabled={isPending}
            />
          </div>
          <div className="field">
            <label htmlFor="details-account">{ACCOUNT_ID_LABEL}</label>
            <input
              id="details-account"
              className="input"
              placeholder={ACCOUNT_ID_PLACEHOLDER}
              value={accountId}
              onChange={handleAccountIdChange}
              required
              disabled={isPending}
            />
          </div>
          <div className="field">
            <label htmlFor="details-key">{API_KEY_LABEL}</label>
            <input
              id="details-key"
              className="input"
              placeholder={API_KEY_PLACEHOLDER}
              type="password"
              autoComplete="off"
              value={apiKey}
              onChange={handleApiKeyChange}
              required
              disabled={isPending}
            />
          </div>

          {errorMessage && (
            <p role="alert" className="text-muted">
              {errorMessage}
            </p>
          )}

          <button type="submit" className="btn btn-primary blueprint form-submit-btn" disabled={isPending}>
            <BlueprintCorners />
            {buttonLabel}
            {!isPending && <ArrowRightIcon />}
          </button>
        </form>
      </div>
    </section>
  );
}
