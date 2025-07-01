// src/components/DeepSearchModal.tsx

import React from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { Box, Button, Typography } from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import { useUIContext } from '../context/UIContext';
import { useDeepContext } from '../context/DeepContext';
import { Segment, DeepSearchResponse } from '../types';
import { COLORS, DeepHeader, DeepList, DeepMeta, DeepSubHeader, DeepText, StyledButton } from '../styles';
import { BE_HOST, BE_PORT, BE_PROTOCOL, DEEP_NAME, DEEP_SEARCH_TEMP } from '../sharedConfig';

const TimelineContainer = styled.div``;



type Props = {
  segment: Segment;
};

const DeepSearchModal = ({ segment }: Props) => {
  const { setModalOpen, setModalContent, setModalLoading } = useUIContext();
  const { deepSearchResults, setDeepSearchResults } = useDeepContext();

  const segmentId = segment.id;
  const segmentTerms = (segment.flags?.[0]?.matches ?? []).join(', ');

  const renderContent = (result: DeepSearchResponse) => {
    return (
      <Box sx={{ p: 2 }}>
        <DeepHeader style={{ marginTop: 0 }}>Summary</DeepHeader>
        <DeepSubHeader>{result.summary}</DeepSubHeader>

        <DeepHeader>Key Figures</DeepHeader>
        <DeepList>
          {result.key_figures.map((f, i) => <li key={i}>{f}</li>)}
        </DeepList>

        <DeepHeader>Timeline</DeepHeader>
        <TimelineContainer>
          <Timeline sx={{
            [`& .MuiTimelineOppositeContent-root`]: { flex: .2, color: COLORS.deepSearch.text.content },
            '& .MuiTimelineDot-root': { backgroundColor: COLORS.primaryAccent, width: 10, height: 10 },
            '& .MuiTimelineConnector-root': { backgroundColor: 'rgba(255, 255, 255, 0.37)' },
            '& .MuiTimelineContent-root': {
              fontFamily: 'Montserrat, sans-serif',
              fontSize: '1.05rem',
              color: 'rgba(255, 255, 255, 0.9)'
            }
          }}>
            {result.timeline.map((entry, i) => {
              const [time, ...rest] = entry.split(':');
              const event = rest.join(':').trim();
              return (
                <TimelineItem key={i}>
                  <TimelineOppositeContent>{time}</TimelineOppositeContent>
                  <TimelineSeparator>
                    <TimelineDot />
                    {i < result.timeline.length - 1 && <TimelineConnector />}
                  </TimelineSeparator>
                  <TimelineContent>{event}</TimelineContent>
                </TimelineItem>
              );
            })}
          </Timeline>
        </TimelineContainer>

        <DeepHeader>Controversy</DeepHeader>
        <DeepText>{result.controversy}</DeepText>

        <DeepHeader>Evidence</DeepHeader>
        <DeepText>{result.evidence}</DeepText>

        <DeepMeta>
          <span>Context: <i>{segmentTerms}</i></span>
          <span>Model: {DEEP_NAME}</span>
          <span>Duration: {result.query_duration}s</span>
          <span>Temperature: {DEEP_SEARCH_TEMP}</span>
        </DeepMeta>
      </Box>
    );
  }

  const runDeepSearch = async () => {
    setModalOpen(true);
    setModalLoading(true);
    setModalContent(null);

    try {
      const endpoint = `${BE_PROTOCOL}://${BE_HOST}:${BE_PORT}/deepsearch`;
      const res = await axios.post(endpoint, { segment_id: segmentId });
      const data: DeepSearchResponse = res.data;

      setDeepSearchResults(prev => {
        const updated = new Map(prev);
        const existing = updated.get(segmentId) || [];
        updated.set(segmentId, [...existing, data]);
        return updated;
      });

      setModalContent(renderContent(data));
    } catch (err) {
      console.error("DeepSearchModal error:", err);
      setModalContent(<Typography sx={{ color: '#aaa' }}>Error loading deep search.</Typography>);
    } finally {
      setModalLoading(false);
    }
  };

  return (
    <StyledButton onClick={runDeepSearch}>Deep Search</StyledButton>
  );
};

export default DeepSearchModal;
