import { Fragment } from "react";
import type { components } from "@/api/schema";
import { CheckIcon } from "@/components/icons";
import { STEP_LABELS, StepState } from "./StepIndicator.constants";
import { useStepIndicator } from "./useStepIndicator";

type SessionOut = components["schemas"]["SessionOut"];

interface Props {
  session: SessionOut;
}

interface StepCircleProps {
  number: number;
  state: StepState;
}

function StepCircle({ number, state }: StepCircleProps) {
  if (state === StepState.Done) {
    return (
      <span className="step-num step-done">
        <CheckIcon />
      </span>
    );
  }
  const circleClassName = state === StepState.Current ? "step-num step-now" : "step-num step-todo";
  return <span className={circleClassName}>{number}</span>;
}

export function StepIndicator({ session }: Props) {
  const { stepStates } = useStepIndicator(session.status);

  return (
    <div className="stepper">
      {STEP_LABELS.map((label, i) => {
        const state = stepStates[i];
        const labelClassName =
          state === StepState.Current ? "step-label step-label-current" : state === StepState.Todo ? "step-label step-label-todo" : "step-label";
        const isLast = i === STEP_LABELS.length - 1;

        return (
          <Fragment key={label}>
            <div className="step">
              <StepCircle number={i + 1} state={state} />
              <span className={labelClassName}>{label}</span>
            </div>
            {!isLast && <div className="stepper-line" />}
          </Fragment>
        );
      })}
    </div>
  );
}
