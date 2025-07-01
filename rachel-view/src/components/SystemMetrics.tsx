// src/components/TopMetricsBar.tsx

import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { Paper } from "@mui/material";
import { MetricData } from "../types";
import { BE_HOST, BE_PORT, BE_PROTOCOL } from "../sharedConfig";

const BarContainer = styled('div')`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  min-height: 2rem;
  width: 100vw;
  z-index: 999;
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  background: rgb(26, 25, 24);
  font-family: "Roboto", sans-serif;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
`;

const MetricRow = styled.div`
  display: flex;
  width: 100%;
  justify-content: space-between;
`;

const MetricItem = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 0.875rem;
  padding: 1rem 2rem;
`;

const Label = styled.span`
  font-weight: 500;
  margin-right: 0.3rem;
  color: #666;
`;

const Value = styled.span`
  font-weight: 400;
  color: #999;
`;

export const TopMetricsBar: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricData | null>(null);

  useEffect(() => {
    const source = new EventSource(`${BE_PROTOCOL}://${BE_HOST}:${BE_PORT}/metrics/stream`);

    source.onmessage = (event) => {
      try {
        const parsed: MetricData = JSON.parse(event.data);
        setMetrics(parsed);
      } catch (err) {
        console.warn("Failed to parse metrics stream:", err);
      }
    };

    source.onerror = (err) => {
      console.error("Metrics stream error:", err);
      source.close();
    };

    return () => {
      source.close();
    };
  }, []);

  if (!metrics) return null;

  return (
    <BarContainer>
      <MetricRow>
        <MetricItem>
          <Label>CPU:</Label>
          <Value>{metrics.cpu.toFixed(1)}%</Value>
        </MetricItem>
        <MetricItem>
          <Label>RAM:</Label>
          <Value>{metrics.ram.toFixed(1)}%</Value>
        </MetricItem>
        {metrics.gpu !== null && metrics.gpu !== undefined && (
          <MetricItem>
            <Label>GPU:</Label>
            <Value>{metrics.gpu.toFixed(1)}%</Value>
          </MetricItem>
        )}
        <MetricItem>
          <Label>Segments:</Label>
          <Value>{metrics.segments_processed}</Value>
        </MetricItem>
        <MetricItem>
          <Label>Q:transcript:</Label>
          <Value>{metrics.queues.transcript}</Value>
        </MetricItem>
        <MetricItem>
          <Label>Q:shallow:</Label>
          <Value>{metrics.queues.shallow_results}</Value>
        </MetricItem>
        <MetricItem>
          <Label>Q:deep:</Label>
          <Value>{metrics.queues.deep_queue}</Value>
        </MetricItem>
        <MetricItem>
          <Label>Q:deep_results:</Label>
          <Value>{metrics.queues.deep_results}</Value>
        </MetricItem>
      </MetricRow>
    </BarContainer>
  );
};
