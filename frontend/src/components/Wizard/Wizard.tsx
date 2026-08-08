import type { components } from "@/api/schema";
import { DetailsStep } from "@/components/DetailsStep/DetailsStep";
import { LiveStep } from "@/components/LiveStep/LiveStep";
import { ReviewStep } from "@/components/ReviewStep/ReviewStep";
import { ValidateStep } from "@/components/ValidateStep/ValidateStep";
import { WizardScreen } from "./Wizard.constants";
import { useWizard } from "./useWizard";

type SessionOut = components["schemas"]["SessionOut"];

interface Props {
  session: SessionOut;
}

export function Wizard({ session }: Props) {
  const { screen } = useWizard(session.status);

  switch (screen) {
    case WizardScreen.Details:
      return <DetailsStep session={session} />;
    case WizardScreen.Validate:
      return <ValidateStep session={session} />;
    case WizardScreen.Review:
      return <ReviewStep session={session} />;
    case WizardScreen.Live:
      return <LiveStep session={session} />;
  }
}
