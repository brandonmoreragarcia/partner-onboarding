import { useState, type ChangeEvent, type SubmitEvent } from "react";
import { getErrorMessage } from "@/api/errors";
import type { components } from "@/api/schema";
import { useSubmitDetails } from "@/hooks/useSubmitDetails";

type SessionOut = components["schemas"]["SessionOut"];

export function useDetailsStep(session: SessionOut) {
  const [companyName, setCompanyName] = useState(session.companyName ?? "");
  const [accountId, setAccountId] = useState(session.accountId ?? "");
  const [apiKey, setApiKey] = useState("");
  const { mutate, isPending, error } = useSubmitDetails();

  const handleCompanyNameChange = (event: ChangeEvent<HTMLInputElement>) => setCompanyName(event.target.value);
  const handleAccountIdChange = (event: ChangeEvent<HTMLInputElement>) => setAccountId(event.target.value);
  const handleApiKeyChange = (event: ChangeEvent<HTMLInputElement>) => setApiKey(event.target.value);

  const handleSubmit = (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    mutate({ companyName, accountId, apiKey });
  };

  const errorMessage = error ? getErrorMessage(error) : null;
  const showInvalidBanner = session.status === "INVALID" && Boolean(session.lastError);

  const result = {
    companyName,
    accountId,
    apiKey,
    isPending,
    errorMessage,
    showInvalidBanner,
    lastError: session.lastError,
    handleCompanyNameChange,
    handleAccountIdChange,
    handleApiKeyChange,
    handleSubmit,
  };
  return result;
}
