import { getErrorMessage } from "@/api/errors";
import { useSession } from "@/hooks/useSession";

export function useApp() {
  const { data: session, isLoading, isError, error } = useSession();

  const errorMessage = isError ? getErrorMessage(error) : null;

  const result = { session, isLoading, errorMessage };
  return result;
}
