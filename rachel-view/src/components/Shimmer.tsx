import { useMemo } from 'react';
import styled, { keyframes, css } from 'styled-components';
import { Box, Skeleton } from "@mui/material"
import { Row, RowItem } from "./TranscriptStream"

const dots = keyframes`
  0%   { content: ""; }
  25%   { content: "."; }
  50%  { content: ".."; }
  75%  { content: "..."; }
  100%  { content: ""; }
`;

const DotsSpan = styled.span`
  display: inline-block;
  width: 1.5em;
  color: inherit;
  margin-left: .1rem;
  &::after {
    display: inline-block;
    content: ".";
    animation: ${dots} 1.5s steps(3, end) infinite;
  }
`;

export const Ellipsis = () => <DotsSpan />;

export const randomBetween = (a: number, b: number, decimals: number = 0): number => {
  const factor = Math.pow(10, decimals);
  return Math.round((Math.random() * (b - a) + a) * factor) / factor;
}

const background = '#555';
const opacity = 0.3;

/* Privates - don't change these */
const _segmentSkeleton = () => {
  const marginRight1 = useMemo(() => `${randomBetween(1, 15, 1)}rem`, []);
  const marginRight2 = useMemo(() => `${randomBetween(2, 3, 1)}rem`, []);
  const marginRight3 = useMemo(() => `${randomBetween(2, 3, 1)}rem`, []);
  const marginRight4 = useMemo(() => `${randomBetween(2, 5, 1)}rem`, []);



  return (
    <Box style={{ width: '100%', height: '100%', opacity: opacity }}>
      <Skeleton style={{
        height: '4rem',
        background: background,
        marginRight: marginRight1,
      }} />
      <Skeleton style={{
        height: '2rem',
        background: background,
        marginRight: marginRight2,
      }} />
      <Skeleton style={{
        height: '2rem',
        background: background,
        marginRight: marginRight3
      }} />
      <Skeleton style={{
        height: '2rem',
        background: background,
        marginRight: marginRight4,
      }} />

    </Box>
  );
};

const _transcript = () => {
  const one = useMemo(() => `${randomBetween(1, 4, 1)}rem`, []);
  const two = useMemo(() => `${randomBetween(1, 3, 1)}rem`, []);
  const three = useMemo(() => `${randomBetween(1, 3, 1)}rem`, []);

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      style={{
        width: '100%',
        height: '100%',
        marginTop: '0rem',
        opacity: opacity
      }}>
      <Skeleton style={{
        height: '3rem',
        width: `calc(100% - ${one})`,
        background: background,
      }} />
      <Skeleton style={{
        height: '3rem',
        width: `calc(100% - ${two})`,
        background: background
      }} />
      <Skeleton style={{
        height: '3rem',
        width: `calc(100% - ${three})`,
        background: background
      }} />
    </Box>)
}

const _metrics = () => {
  return (<Box style={{ width: '5rem', height: '100%', opacity: opacity }}>
    <Skeleton style={{ height: '12rem', background: background }} />
  </Box>)
}


export const SegmentSkeleton = () => {
  return (<Row style={{ background: 'transparent', margin: 0, padding: 0, height: '15rem' }}>
    <RowItem style={{ flex: '0 0 10%', padding: '0 2rem 0 2rem', minWidth: '12rem' }}>
      {_metrics()}
    </RowItem>
    <RowItem style={{ flex: '0 0 20%', minWidth: '20rem' }}>
      {_transcript()}
    </RowItem>
    <RowItem style={{ flex: '1 0 0' }}>
      {_segmentSkeleton()}
    </RowItem>
  </Row>)

}


export const AnalysisResultsShimmer = () => {
  return _segmentSkeleton()
}

