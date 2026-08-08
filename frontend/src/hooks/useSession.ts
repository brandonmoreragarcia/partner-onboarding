import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/api/client";

export const sessionQueryKey = ["session"] as const;

async function fetchOrCreateSession() {
  // POST /sessions is idempotent (get-or-create by the hardcoded PARTNER_ID), so reusing
  // it as this query's fetcher makes it double as both "create on first visit" and
  // "resume on reload/refetch" — no separate bootstrap step, no id held in React state.
  const { data, error } = await apiClient.POST("/sessions");
  if (error) throw error;
  return data;
}

export function useSession() {
  const query = useQuery({
    queryKey: sessionQueryKey,
    queryFn: fetchOrCreateSession,
  });
  return query;
}
