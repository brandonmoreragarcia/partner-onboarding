import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import type { components } from "@/api/schema";
import { sessionQueryKey } from "./useSession";

type SessionOut = components["schemas"]["SessionOut"];

export function useValidate() {
  const queryClient = useQueryClient();

  const mutationFn = async () => {
    const session = queryClient.getQueryData<SessionOut>(sessionQueryKey);
    if (!session) throw new Error("No session loaded yet");

    const { data, error } = await apiClient.POST("/sessions/{session_id}/validate", {
      params: { path: { session_id: session.id } },
    });
    if (error) throw error;
    return data;
  };

  const handleSuccess = () => queryClient.invalidateQueries({ queryKey: sessionQueryKey });

  const mutation = useMutation({ mutationFn, onSuccess: handleSuccess });
  return mutation;
}
