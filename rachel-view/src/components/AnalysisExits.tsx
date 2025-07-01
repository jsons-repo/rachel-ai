// src/components/AnalysisExits.tsx
import styled from "styled-components";
import { Flag, ExitReason, ExitReasonLabels } from "../types"
import { COLORS, GLOBAL_STYLES } from "../styles";

export const Reasons: Record<ExitReason, string[]> = {
    [ExitReason.NONE]: ["No issue detected"],
    [ExitReason.DUPLICATE]: ["Duplicate"],
    [ExitReason.CONFUSING]: ["Too confusing"],
    [ExitReason.RULE_VIOLATION]: ["this wasn't interesting"],
  };
  
  const pickRandom = <T,>(arr: T[]): T =>
            arr[Math.floor(Math.random() * arr.length)];
  

  const Container = styled.div.withConfig({
    shouldForwardProp: (prop) => prop !== 'minHeight' && prop !== 'margin',
  })<{ minHeight?: string, margin?: string }>`
    padding: 1rem;
  `;

  const Fun = styled.div.withConfig({
    shouldForwardProp: (prop) => prop !== 'minHeight' && prop !== 'margin',
  })<{ minHeight?: string, margin?: string }>`
    color:${COLORS.primaryText};
    font-size: 1rem;
    font-style: italic;
    text-align: center;
  `;

  const Formal = styled.div.withConfig({
    shouldForwardProp: (prop) => prop !== 'minHeight' && prop !== 'margin',
  })<{ minHeight?: string, margin?: string }>`
    color:rgba(255,255,255, .4);
    font-size: .9rem;
    text-align: center;
    font-style: italic;
  `;

  export const AnalysisExits = ({ flag }: { flag: Flag }) => {

    const safeExitReason =
        flag.exit_reason && ExitReasonLabels[flag.exit_reason]
          ? ExitReasonLabels[flag.exit_reason]
          : ExitReasonLabels[ExitReason.NONE];

    const safeReason =
        flag.exit_reason && Reasons[flag.exit_reason]
            ? flag.exit_reason
            : ExitReason.NONE;
  
    const labelArray = Reasons[safeReason];
    const randomLabel = pickRandom(labelArray);
  
    return (
      <Container>
        <Formal>(From deep model: {safeExitReason})</Formal>
      </Container>
    );
  };