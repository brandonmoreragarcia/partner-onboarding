import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/api/client";

export function useResetSession() {
  const mutationFn = async () => {
    const { error } = await apiClient.POST("/dev/reset");
    if (error) throw error;
  };

  // Full reload rather than invalidateQueries: components like DetailsStep seed
  // local form state from the session once on mount, so if the reset happens while
  // already on that same screen, a query refetch alone wouldn't clear the form --
  // only remounting the app does.
  const handleSuccess = () => window.location.reload();

  const mutation = useMutation({ mutationFn, onSuccess: handleSuccess });
  return mutation;
}
