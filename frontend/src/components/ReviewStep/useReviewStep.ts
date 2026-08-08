import { getErrorMessage } from "@/api/errors";
import type { components } from "@/api/schema";
import { useGoLive } from "@/hooks/useGoLive";

type SessionOut = components["schemas"]["SessionOut"];

export interface ReviewItem {
  id: string;
  name: string;
  externalId: string;
  flagged: boolean;
}

export function useReviewStep(session: SessionOut) {
  const { mutate, isPending, error } = useGoLive();

  // Best-effort: flag an item as the subject of a warning by matching its externalId
  // inside the warning text -- session.warnings is plain strings, no structured item
  // reference in the API shape.
  const items: ReviewItem[] = session.items.map((item) => {
    const flagged = session.warnings.some((warning) => warning.includes(item.externalId));
    const reviewItem: ReviewItem = { id: item.id, name: item.name, externalId: item.externalId, flagged };
    return reviewItem;
  });

  const hasWarnings = session.warnings.length > 0;
  const errorMessage = error ? getErrorMessage(error) : null;
  const handleGoLive = () => mutate();

  const result = { items, hasWarnings, warnings: session.warnings, isPending, errorMessage, handleGoLive };
  return result;
}
