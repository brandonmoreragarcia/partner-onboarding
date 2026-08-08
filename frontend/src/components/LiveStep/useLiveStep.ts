import type { components } from "@/api/schema";

type SessionOut = components["schemas"]["SessionOut"];

export function useLiveStep(session: SessionOut) {
  const result = {
    companyName: session.companyName,
    itemCount: session.items.length,
  };
  return result;
}
