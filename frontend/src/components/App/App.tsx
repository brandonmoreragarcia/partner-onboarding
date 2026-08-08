import { DevResetButton } from "@/components/DevResetButton/DevResetButton";
import { Wizard } from "@/components/Wizard/Wizard";
import { useApp } from "./useApp";

const LOADING_TEXT = "Loading…";

export function App() {
  const { session, isLoading, errorMessage } = useApp();

  if (isLoading) {
    return (
      <section className="screen st-wait">
        <div className="screen-inner">
          <p className="text-muted">{LOADING_TEXT}</p>
        </div>
      </section>
    );
  }

  if (errorMessage || !session) {
    return (
      <>
        <DevResetButton />
        <section className="screen st-err">
          <div className="screen-inner">
            <p role="alert">{errorMessage}</p>
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <DevResetButton />
      <Wizard session={session} />
    </>
  );
}
