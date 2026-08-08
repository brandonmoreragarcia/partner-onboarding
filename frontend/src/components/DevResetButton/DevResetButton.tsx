import { useDevResetButton } from "./useDevResetButton";

const LABEL_IDLE = "Reset session";
const LABEL_PENDING = "Resetting…";

// Dev-only: tree-shaken out of production builds by Vite (import.meta.env.DEV is
// statically false there). Deliberately NOT styled with the design system's .btn
// classes -- it's tooling, not one of the 8 product screens.
export function DevResetButton() {
  const { isDevBuild, isPending, handleReset } = useDevResetButton();

  if (!isDevBuild) return null;

  return (
    <button type="button" className="dev-reset-btn" onClick={handleReset} disabled={isPending}>
      {isPending ? LABEL_PENDING : LABEL_IDLE}
    </button>
  );
}
