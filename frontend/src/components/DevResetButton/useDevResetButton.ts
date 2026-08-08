import { useResetSession } from "@/hooks/useResetSession";

export function useDevResetButton() {
  const { mutate, isPending } = useResetSession();

  const handleReset = () => mutate();

  const result = {
    isDevBuild: import.meta.env.DEV,
    isPending,
    handleReset,
  };
  return result;
}
