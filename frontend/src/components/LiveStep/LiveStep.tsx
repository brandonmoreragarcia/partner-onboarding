import type { components } from "@/api/schema";
import { BlueprintCorners, CheckCircleIcon } from "@/components/icons";
import { StepIndicator } from "@/components/StepIndicator/StepIndicator";
import { useLiveStep } from "./useLiveStep";

type SessionOut = components["schemas"]["SessionOut"];

const EYEBROW_TEXT = "Complete";
const PANEL_TITLE = "You're live";

interface Props {
  session: SessionOut;
}

export function LiveStep({ session }: Props) {
  const { companyName, itemCount } = useLiveStep(session);

  return (
    <section className="screen st-ok">
      <div className="screen-inner">
        <div className="eyebrow">{EYEBROW_TEXT}</div>
        <StepIndicator session={session} />

        <div className="panel blueprint panel-centered">
          <BlueprintCorners />
          <CheckCircleIcon width={28} height={28} />
          <div>
            <div className="panel-title panel-title-lg">{PANEL_TITLE}</div>
            <p className="panel-body">
              {companyName} is now live with {itemCount} item(s) synced.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
