import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { COLORS } from '../styles';
import { Segment } from '../types';

const Container = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'isHovered',
}) <{ isHovered?: boolean }>`
  width:100%;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: start;
  justify-content: start;
  text-align: left;
  height: 100%;
  > div {
    opacity: ${({ isHovered }) => (isHovered ? '1.0' : '0.8')};
    transition: opacity 0.2s ease;
  }
`;

const Label = styled.div`
    margin:.2rem 0 0 0;
    font-size: .75em;
    color: ${COLORS.metrics.label};
`;

const Value = styled.div`
    color: ${COLORS.metrics.text};
    font-size: .95rem;
    margin-bottom: .4rem;
`;

export function formatSecondsToHHMMSS(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.floor(totalSeconds % 60);

  const pad = (n: number) => n.toString().padStart(2, '0');

  return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}

type MetricsProps = Pick<Segment, 'start' | 'duration' | 'latency' | 'created_at' | 'pipeline_started_at'> & {
  isHovered?: boolean;
};

const SegmentMetrics = ({ start, duration, latency, created_at, pipeline_started_at, isHovered }: MetricsProps) => {

  const [realLatency, setRealLatency] = useState(() => {
    const now = Date.now()
    const createdAtMs = pipeline_started_at * 1000;
    const output = ((now - createdAtMs) / 1000).toFixed(2)
    return output;
  });

  useEffect(() => {
    const now = Date.now()
    const createdAtMs = pipeline_started_at * 1000;
    const output = ((now - createdAtMs) / 1000).toFixed(2)
    setRealLatency(output);
  }, [created_at]);

  const dynamicLatency = latency ? Number(latency).toFixed(2) : "0.00";


  return (
    <Container isHovered={isHovered}>
      <Label>Time:</Label>
      <Value>{formatSecondsToHHMMSS(start)}</Value>
      <Label>Duration:</Label>
      <Value>{formatSecondsToHHMMSS(duration ?? 0)}</Value>
      <Label>Transcription:</Label>
      <Value>{dynamicLatency}s</Value>
      <Label>Latency:</Label>
      <Value>{realLatency}s</Value>
    </Container>
  );
};

export default SegmentMetrics;
