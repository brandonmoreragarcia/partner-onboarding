import type { components } from "./schema";

type ErrorResponse = components["schemas"]["ErrorResponse"];
type HTTPValidationError = components["schemas"]["HTTPValidationError"];

/** Narrows the union openapi-fetch infers for non-2xx bodies (ErrorResponse | HTTPValidationError)
 * into a single displayable string, without the frontend hand-defining either shape itself. */
export function getErrorMessage(error: unknown): string {
  if (error && typeof error === "object") {
    if ("message" in error && typeof (error as ErrorResponse).message === "string") {
      return (error as ErrorResponse).message;
    }
    if ("detail" in error) {
      const detail = (error as HTTPValidationError).detail;
      if (Array.isArray(detail) && detail.length > 0) {
        return detail.map((d) => d.msg).join(", ");
      }
    }
  }
  return "Something went wrong. Please try again.";
}
