import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import type { components } from "@/api/schema";
import { sessionQueryKey } from "./useSession";

type DetailsIn = components["schemas"]["DetailsIn"];
type SessionOut = components["schemas"]["SessionOut"];

export function useSubmitDetails() {
  const queryClient = useQueryClient();

  const mutationFn = async (payload: DetailsIn) => {
    const session = queryClient.getQueryData<SessionOut>(sessionQueryKey);
    if (!session) throw new Error("No session loaded yet");

    const { data, error } = await apiClient.POST("/sessions/{session_id}/details", {
      params: { path: { session_id: session.id } },
      body: payload,
    });
    if (error) throw error;
    return data;
  };

  // Refetch from the server rather than assume the mutation's response is the new
  // truth — do not optimistically advance the step (CLAUDE.md).
  const handleSuccess = () => queryClient.invalidateQueries({ queryKey: sessionQueryKey });

  const mutation = useMutation({ mutationFn, onSuccess: handleSuccess });
  return mutation;
}
