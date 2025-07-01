// src/components/TranscriptStream.tsx

import React, { useEffect, useState, useRef } from 'react';
import TranscriptItem from './TranscriptItem';
import AnalysisItem from './AnalysisItem';
import { Button } from '@mui/material';
import styled from 'styled-components';
import { COLORS, GLOBAL_STYLES } from '../styles';
import SegmentMetrics from './SegmentMetrics';
import { PipelineState, useUIContext } from '../context/UIContext';
import { useSegmentContext } from '../context/SegmentContext';
import { FEED_STATUS, FeedStatus } from './FeedStatus';
import { useVirtualizer } from '@tanstack/react-virtual';
import { SegmentSkeleton } from './Shimmer';
import { DeepProvider } from '../context/DeepContext';

const ScrollAnchor = styled.div`
  height: 1px;
  margin-bottom: 40px;
`;

export const Row = styled.div`
  width: 100%;
  display: flex;
  align-items: center;
  background: ${COLORS.table.cellBackground};
  transition: ${GLOBAL_STYLES.transition.background};
  margin: 0 0 4px 0;
  &:hover {
    cursor: pointer;
    background: ${COLORS.table.cellBackgroundHover};
  }
`;

export const RowItem = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 1rem 3rem;
  margin: 1rem 0;
`;

const VirtualWrapper = styled.div`
  width: 100%;
  height: 100%;
  position: relative;
`;

const StreamContainer = styled.div`
  height: calc(100vh - 4.5rem);
  width: 100vw;
  margin-top: 4rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
`;

const TranscriptStream = () => {


  const bottomRef = useRef<HTMLDivElement | null>(null);
  const parentRef = useRef<HTMLDivElement | null>(null);
  const SCROLL_RESUME_DELAY = 8000;
  const scrollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const {
    setExpandedIndex,
    shouldAutoScroll,
    setShouldAutoScroll,
    modalOpen,
    pipelineState
  } = useUIContext();
  const { streamState, segments } = useSegmentContext();

  useEffect(() => {
    const handleMouseMove = () => {
      setShouldAutoScroll(false);
      if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current);
      scrollTimeoutRef.current = setTimeout(() => {
        setShouldAutoScroll(true);
      }, SCROLL_RESUME_DELAY);

      return () => {
        if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current);
      };
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current);
    };
  }, []);

  useEffect(() => {
    if (shouldAutoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [segments, shouldAutoScroll]);


  const DebugButton = ({ count = 10 }: { count?: number }) => {
    const handleDebugClick = () => {
      const recentSegments = segments.slice(-count);
      const debugOutput: Record<string, any> = {};

      recentSegments.forEach((seg) => {
        debugOutput[seg.id] = {
          key: seg.transcript,
          flags: seg.flags?.flatMap((f) => f.matches) ?? [],
          segment: seg,
        };
      });
      console.log("DEBUG SEGMENTS:", debugOutput);
    };

    return (
      <div style={{ padding: '1rem', alignSelf: 'flex-end' }}>
        <Button variant="outlined" color="secondary" onClick={handleDebugClick}>
          Debug Segments
        </Button>
      </div>
    );
  };

  const rowVirtualizer = useVirtualizer({
    count: segments.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 250,
    overscan: 5,
    measureElement: (el) => el.getBoundingClientRect().height
  });

  useEffect(() => {
    rowVirtualizer.measure(); // Forces fresh height for all rows
  }, []);


  return (
    <DeepProvider>
      <StreamContainer ref={parentRef}>
        {/* <DebugButton count={10} /> */}
        <VirtualWrapper>
          <div style={{ position: 'relative', height: rowVirtualizer.getTotalSize() }}>
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const segment = segments[virtualRow.index];
              const isHovered = hoveredIndex === virtualRow.index;

              return (
                <div
                  key={segment.id}
                  ref={rowVirtualizer.measureElement}
                  data-index={virtualRow.index}
                  style={{
                    transform: `translateY(${virtualRow.start}px)`,
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                  }}
                  onMouseEnter={() => setHoveredIndex(virtualRow.index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                  onClick={() =>
                    setExpandedIndex((prev) =>
                      prev === virtualRow.index ? null : virtualRow.index
                    )
                  }
                >
                  <Row>
                    <RowItem style={{ flex: '0 0 10%', paddingLeft: '2rem', minWidth: '12rem' }}>
                      <SegmentMetrics {...segment} isHovered={isHovered} />
                    </RowItem>
                    <RowItem
                      style={{
                        flex: '0 0 20%',
                        minWidth: '20rem',
                        padding: '2rem 5rem',
                        borderRight: `1px solid ${COLORS.table.cellDividerBorder}`,
                        borderLeft: `1px solid ${COLORS.table.cellDividerBorder}`,
                      }}
                    >
                      <TranscriptItem segment={segment} isHovered={isHovered} />
                    </RowItem>
                    <RowItem style={{ flex: '1 0 0' }}>
                      <AnalysisItem
                        segment={segment}
                        index={virtualRow.index}
                        isHovered={isHovered}
                      />
                    </RowItem>
                  </Row>
                </div>
              );
            })}
            <div
              style={{
                position: 'absolute',
                top: rowVirtualizer.getTotalSize(),
                left: 0,
                width: '100%',
              }}
            >
              {
                streamState === FEED_STATUS.LISTENING &&
                pipelineState == PipelineState.ACTIVE &&
                modalOpen == false && (
                  <SegmentSkeleton />
                )}
              <div style={{ height: '20rem' }} />
              <ScrollAnchor ref={bottomRef} />
            </div>
          </div>
        </VirtualWrapper>

      </StreamContainer >
    </DeepProvider>
  );
};

export default TranscriptStream;