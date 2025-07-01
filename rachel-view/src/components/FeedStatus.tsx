// src/components/FeedStatus.tsx
import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import { COLORS } from '../styles';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import SettingsEthernetOutlined from '@mui/icons-material/SettingsEthernetOutlined';
import { Typography, Box, Icon } from '@mui/material';
import { Ellipsis } from './Shimmer';
import { useUIContext, PipelineState } from '../context/UIContext';
import { useSegmentContext } from '../context/SegmentContext';
import { BE_HOST, BE_PORT, BE_PROTOCOL } from '../sharedConfig';
import { PlayCircleOutline } from '@mui/icons-material';

const Container = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'background' && prop !== 'borderColor',
}) <{ background?: string; borderColor?: string }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 999;
  height: 3rem;
  padding: 2rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(
    6deg,
    rgb(35, 34, 31) 50%, 
    rgb(41, 37, 33) 100%
  );
  border-bottom: 6px solid ${({ borderColor }) => borderColor};
`;


// Left: Start/Stop icon
const StartStopContainer = styled.div`
  display: flex;
  align-items: center;
`;

const Spacer = styled.div`
  flex: 1;
`;

// Center: Mic status content
const MicStatusContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
`;

export enum FEED_STATUS {
  CONNECTION = 'CONNECTION',
  LISTENING = 'LISTENING',
  ERROR = 'ERROR',
}

const STATUS_CONTENT = (status: FEED_STATUS, isSpeaking: boolean, pipelineState: PipelineState): JSX.Element => {


  if (status === FEED_STATUS.LISTENING && (pipelineState === PipelineState.PENDING || pipelineState === PipelineState.IDLE)) {
    return (
      <Box display="flex" alignItems="center" gap={1}>
        <MicOffIcon sx={{ color: COLORS.status.inactive }} />
        <Typography color="gray">Paused</Typography>
      </Box>
    );
  }

  switch (status) {
    case FEED_STATUS.LISTENING:
      return (
        <Box display="flex" alignItems="center" gap={1}>
          <MicIcon sx={{
            color: isSpeaking ? COLORS.status.activeText : COLORS.status.activeText,
            backgroundColor: isSpeaking ? COLORS.status.activeAccent : COLORS.status.inactive,
            borderRadius: '50%',
            width: 36,
            height: 36,
            padding: 0.5,
            transition: 'all 0.25s ease-in-out'
          }} />
          <Typography color={COLORS.status.activeText}>Listening<Ellipsis /></Typography>
        </Box>
      );
    case FEED_STATUS.CONNECTION:
      return (
        <Box display="flex" alignItems="center" gap={1}>
          <SettingsEthernetOutlined sx={{ color: COLORS.secondaryText }} />
          <Typography color={COLORS.status.inactive}>Waiting to connect<Ellipsis /></Typography>
        </Box>
      );
    case FEED_STATUS.ERROR:
      return (
        <Box display="flex" alignItems="center" gap={1}>
          <ErrorOutlineIcon color="error" />
          <Typography color={COLORS.status.inactive} >Connection failed</Typography>
        </Box>
      );
    default:
      return <></>;
  }
};

const PlayButton = styled(PlayCircleOutline) <{ state: PipelineState }>`
  cursor: pointer;
  font-size: 2.5rem;
  transition: color 0.5s ease;

  color: ${({ state }) =>
    state == PipelineState.IDLE
      ? COLORS.status.inactive
      : state == PipelineState.ACTIVE
        ? COLORS.status.activeAccent
        : COLORS.status.inactive};

  animation: ${({ state }) =>
    state === PipelineState.PENDING ? 'pulse 5s infinite ease-in-out' : 'none'};

  @keyframes pulse {
    0% { color: ${COLORS.status.inactive}; }
    50% { color: ${COLORS.status.activeAccent}; }
    100% { color:${COLORS.status.inactive}; }
  }
`;


export const FeedStatus = () => {

  const [isSpeaking, setIsSpeaking] = useState(false);
  const [volume, setVolume] = useState<number | null>(null);
  const { streamState } = useSegmentContext();
  const { pipelineState, setPipelineState } = useUIContext();

  const sourceRef = useRef<EventSource | null>(null);
  const retryTimeoutRef = useRef<number | null>(null);

  const handleTogglePipeline = async () => {
    if (pipelineState === PipelineState.PENDING) return;

    const targetState =
      pipelineState === PipelineState.ACTIVE
        ? PipelineState.IDLE
        : PipelineState.ACTIVE;

    setPipelineState(PipelineState.PENDING);

    try {
      const endpoint = `${BE_PROTOCOL}://${BE_HOST}:${BE_PORT}/stream/${targetState === PipelineState.ACTIVE ? 'start' : 'pause'}`;
      const res = await fetch(endpoint, { method: 'POST' });

      if (!res.ok) throw new Error(`Failed to toggle pipeline (${res.status})`);

      setPipelineState(targetState);
    } catch (err) {
      console.error('Error toggling pipeline:', err);
      setPipelineState(PipelineState.IDLE); // fail safe
    }
  };

  useEffect(() => {
    const statusUrl = `${BE_PROTOCOL}://${BE_HOST}:${BE_PORT}/stream/status`;
    const statusSource = new EventSource(statusUrl);

    statusSource.addEventListener("pipeline_state", (e) => {
      try {
        const { paused } = JSON.parse(e.data);
        setPipelineState(paused ? PipelineState.IDLE : PipelineState.ACTIVE);
      } catch (err) {
        console.warn("[StatusStream] Invalid payload:", e.data);
      }
    });

    statusSource.addEventListener("heartbeat", (e) => {
      console.debug("[StatusStream] eartbeat", e.data);
    });

    statusSource.onerror = (err) => {
      console.error("[StatusStream] SSE error", err);
      statusSource.close();
    };

    return () => {
      statusSource.close();
    };
  }, []);


  useEffect(() => {
    const connect = () => {
      if (sourceRef.current) {
        return;
      }

      const url = `${BE_PROTOCOL}://${BE_HOST}:${BE_PORT}/voice-stream`;
      const source = new EventSource(url);
      sourceRef.current = source;

      source.onopen = () => {
        console.log('[VoiceStream] Connection opened');
      };

      source.onmessage = (event) => {
        try {
          const { isSpeaking, volume } = JSON.parse(event.data);
          if (typeof isSpeaking === 'boolean') setIsSpeaking(isSpeaking);
          if (typeof volume === 'number') setVolume(volume);
        } catch (err) {
          console.warn('[VoiceStream] Invalid payload:', event.data);
        }
      };

      source.onerror = (err) => {
        console.error('[VoiceStream] SSE error — retrying in 2s', err);
        source.close();
        sourceRef.current = null;

        if (retryTimeoutRef.current) clearTimeout(retryTimeoutRef.current);
        retryTimeoutRef.current = window.setTimeout(connect, 2000);
      };
    };

    connect();

    return () => {
      if (sourceRef.current) {
        sourceRef.current.close();
        sourceRef.current = null;
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
        retryTimeoutRef.current = null;
      }
    };
  }, []);

  const borderColor = (): string => {
    switch (streamState) {
      case FEED_STATUS.CONNECTION:
        return COLORS.status.inactive
      case FEED_STATUS.LISTENING:
        if (pipelineState === PipelineState.PENDING || pipelineState === PipelineState.IDLE) {
          return COLORS.status.inactive
        }
        return COLORS.status.activeAccent;
      case FEED_STATUS.ERROR:
        return COLORS.status.inactive
      default:
        return COLORS.status.inactive;
    }
  };



  return (
    <Container borderColor={borderColor()}>
      <StartStopContainer>
        <PlayButton
          fontSize='large'
          state={pipelineState}
          onClick={handleTogglePipeline}
        />
      </StartStopContainer>

      <Spacer /> {/* Push mic content to center */}

      <MicStatusContainer>
        {STATUS_CONTENT(streamState, isSpeaking, pipelineState)}
      </MicStatusContainer>

      <Spacer /> {/* Maintain centering even with asymmetrical icons */}
    </Container>
  );
};
