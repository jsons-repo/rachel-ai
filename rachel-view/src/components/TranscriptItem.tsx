// src/components/TranscriptItem.tsx

import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { COLORS } from '../styles';
import { ExitReason, Flag, Segment, SegmentStatus } from '../types';
import { BE_HOST, BE_PORT, BE_PROTOCOL } from '../sharedConfig';
import { useUIContext } from '../context/UIContext';
import { UserSearchText } from './UserSearchText';
import { prgba } from '../utils';

type HighlightStyle = {
  background: string;
  color: string;
  border?: string;
};

const Item = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'isHovered',
}) <{ isHovered?: boolean }>`
  padding: 0;
  margin-top: 0;
  line-height: 2rem;
  font-family: 'Courier Prime', monospace;
  font-size: .9rem;
  font-style: italic;
  text-align: center;
  color: ${({ isHovered }) => (isHovered ? COLORS.primaryText : COLORS.citation.text)};
`;

const QuoteBlock = styled.div`
  position: relative;
  user-select: text;

  &::before,
  &::after {
    content: '"';
    font-size: 2.5rem;
    position: absolute;
    font-family: Georgia, serif;
    color: ${COLORS.citation.text};
    opacity: .25;
  }

  &::before {
    top: .25rem;
    left: -1.5rem;
  }

  &::after {
    content: '"';
    right: -1.5rem;
    bottom: -1.5rem;
  }

  &::selection {
    background: rgba(255, 0, 106, 1);
    color: #fff;
  }
`;

const Highlight = styled.span<{
  bg: string;
  color: string;
  border?: string;
  loading?: boolean;
}>`
  background-color: ${({ bg }) => bg};
  color: ${({ color }) => color};
  border: ${({ border }) => border ?? 'none'};
  font-weight: 800;
  font-size: 1.2rem;
  padding: 0.5rem;
  display: inline;

  ${({ loading }) =>
    loading &&
    `
    filter: blur(2px);
    opacity: 0.6;
    transition: filter 0.3s ease, opacity 0.3s ease;
  `}
`;

const getHighlightStyle = (flag?: Flag): HighlightStyle => {
  if (!flag) {
    return {
      background: COLORS.citation.highlight.background,
      color: COLORS.citation.highlight.text,
      border: 'none',
    };
  }

  if (flag.exit_reason === ExitReason.DUPLICATE) {
    return {
      background: prgba(COLORS.table.cellBackground, '#fff', 0.05),
      color: COLORS.citation.text,
      border: 'none',
    };
  }

  if (flag.source === 'shallow') {
    return {
      background: prgba(COLORS.table.cellBackground, '#fff', 0.2),
      color: '#ddd',
      border: `none`,
    };
  }

  return {
    background: COLORS.citation.highlight.background,
    color: COLORS.citation.highlight.text,
    border: 'none'
  };
};

const TranscriptItem = ({ segment, isHovered }: { segment: Segment, isHovered?: boolean }) => {
  const { transcript, flags } = segment;
  const citations: string[] = flags?.[0]?.matches || [];
  const escapedCitations = citations
    .map(c => c.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'))
    .sort((a, b) => b.length - a.length);

  const regex = new RegExp(`(${escapedCitations.join('|')})`, 'gi');
  const parts = transcript.split(regex);
  const isLoading = segment.status === SegmentStatus.IN_PROGRESS

  const renderPart = (part: string, idx: number) => {
    const isCitation = citations.some(c => c.toLowerCase() === part.toLowerCase());
    if (isCitation) {
      const flag = flags?.[0];
      const style = getHighlightStyle(segment.flags?.[0]);
      return (<Highlight
        bg={style.background}
        color={style.color}
        border={style.border}
        loading={isLoading}
      >{part}</Highlight>)
    }
    return <span key={idx}>{part}</span>;

  };


  return (
    <UserSearchText segmentId={segment.id}>
      <Item isHovered={isHovered}>
        <QuoteBlock>
          {parts.map((part, idx) => renderPart(part, idx))}
        </QuoteBlock>
      </Item>
    </UserSearchText>
  );
};

export default TranscriptItem;
