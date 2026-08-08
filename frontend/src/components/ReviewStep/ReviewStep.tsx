import type { components } from "@/api/schema";
import { ArrowRightIcon, BlueprintCorners } from "@/components/icons";
import { StepIndicator } from "@/components/StepIndicator/StepIndicator";
import {
  ACCOUNT_ID_LABEL,
  API_KEY_LABEL,
  API_KEY_MASK,
  COMPANY_NAME_LABEL,
  COMPANY_SECTION_TITLE,
  HEADING_TEXT,
  INSTRUCTION_TEXT,
  ITEMS_SECTION_TITLE,
  LABEL_GOING_LIVE,
  LABEL_GO_LIVE,
  WARNINGS_TITLE,
} from "./ReviewStep.constants";
import { useReviewStep } from "./useReviewStep";

type SessionOut = components["schemas"]["SessionOut"];

interface Props {
  session: SessionOut;
}

export function ReviewStep({ session }: Props) {
  const { items, hasWarnings, warnings, isPending, errorMessage, handleGoLive } = useReviewStep(session);
  const buttonLabel = isPending ? LABEL_GOING_LIVE : LABEL_GO_LIVE;

  return (
    <section className="screen st-wait">
      <div className="screen-inner">
        <div className="eyebrow">Step 3 of 3</div>
        <StepIndicator session={session} />

        <h3>{HEADING_TEXT}</h3>
        <p className="text-muted instruction-text">{INSTRUCTION_TEXT}</p>

        <h6 className="section-label">{COMPANY_SECTION_TITLE}</h6>
        <div className="frame blueprint frame-padded">
          <BlueprintCorners />
          <dl className="kv">
            <dt>{COMPANY_NAME_LABEL}</dt>
            <dd>{session.companyName}</dd>
          </dl>
          <dl className="kv kv-divider">
            <dt>{ACCOUNT_ID_LABEL}</dt>
            <dd>{session.accountId}</dd>
          </dl>
          <dl className="kv kv-divider">
            <dt>{API_KEY_LABEL}</dt>
            <dd>{API_KEY_MASK}</dd>
          </dl>
        </div>

        <h6 className="section-label">{ITEMS_SECTION_TITLE}</h6>
        <div className="frame blueprint">
          <BlueprintCorners />
          {items.map((item) => (
            <div className="row" key={item.id}>
              <span>{item.name}</span>
              <span className={`tag ${item.flagged ? "tag-outline" : "tag-neutral"}`}>{item.externalId}</span>
            </div>
          ))}
        </div>

        {hasWarnings && (
          <div className="warnings-block st-warn">
            <div className="warnings-title">{WARNINGS_TITLE}</div>
            {warnings.map((warning) => (
              <p key={warning}>{warning}</p>
            ))}
          </div>
        )}

        {errorMessage && (
          <p role="alert" className="text-muted">
            {errorMessage}
          </p>
        )}

        <button type="button" className="btn btn-primary blueprint" disabled={isPending} onClick={handleGoLive}>
          <BlueprintCorners />
          {buttonLabel}
          {!isPending && <ArrowRightIcon />}
        </button>
      </div>
    </section>
  );
}
