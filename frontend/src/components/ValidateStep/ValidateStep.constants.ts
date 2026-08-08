export enum ValidateStepMode {
  Ready = "ready",
  Pending = "pending",
  Unavailable = "unavailable",
}

export const HEADING_TEXT = "Validate integration";
export const COMPANY_NAME_LABEL = "Company name";
export const ACCOUNT_ID_LABEL = "Account ID";
export const LABEL_VALIDATING = "Validating…";

export const EYEBROW_SUFFIX: Record<ValidateStepMode, string> = {
  [ValidateStepMode.Ready]: "",
  [ValidateStepMode.Pending]: " — pending",
  [ValidateStepMode.Unavailable]: " — unavailable",
};

interface ModeCopy {
  statusTag: string;
  panelTitle: string;
  panelBody: string;
  panelNote: string | null;
  buttonLabel: string;
}

export const MODE_COPY: Record<ValidateStepMode, ModeCopy> = {
  [ValidateStepMode.Ready]: {
    statusTag: "Ready",
    panelTitle: "Ready to validate",
    panelBody: "Trigger validation to check your credentials with the provider.",
    panelNote: null,
    buttonLabel: "Validate integration",
  },
  [ValidateStepMode.Pending]: {
    statusTag: "Checking",
    panelTitle: "Checking your credentials",
    panelBody: "Contacting the provider and pulling your available items. This usually takes a few seconds.",
    panelNote: null,
    buttonLabel: "Validating…",
  },
  [ValidateStepMode.Unavailable]: {
    statusTag: "Unavailable",
    panelTitle: "Provider unavailable",
    panelBody: "The provider didn't respond. Nothing was changed.",
    panelNote: "Not caused by your details — this is temporary and safe to retry.",
    buttonLabel: "Retry",
  },
};
