// src/components/AnalysisItem.tsx
import styled from 'styled-components';
import { ExitReason, Segment, SegmentStatus } from '../types';
import { COLORS } from '../styles';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { useUIContext } from '../context/UIContext';
import DeepSearchModal from './DeepSearchModal';
import { AnalysisResultsShimmer } from './Shimmer';
import {
  getSeverityTextColor,
  getSeverityBGColor,
  getSeverityBorder,
  getSeverityIcon
} from '../utils';
import { AnalysisExits } from './AnalysisExits';

const SummaryRow = styled.div`
  display: flex;
  align-items: flex-start;
`;

const Citation = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'isHovered',
}) <{
  isHovered?: boolean;
}>`
  font-family: 'Courier Prime', monospace;
  font-size: .9rem;
  font-style: italic;
  margin: 2rem 0;
  color: ${COLORS.primaryText}
`;

const Summary = styled.div`
  font-family: 'Montserrat', sans-serif;
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 2rem;
  color: ${COLORS.analysis.headline};
  margin: 0 0 2rem 0;
  padding: 0;
  flex: 1;
  display: flex;
  flex-wrap: wrap;
`;

const DeepAnalysis = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'isHovered' && prop !== 'expanded',
}) <{
  isHovered?: boolean;
  expanded?: boolean;
}>`
  font-family: 'Montserrat', sans-serif;
  font-size: 1rem;
  color: ${({ isHovered }) => (isHovered ? COLORS.primaryText : COLORS.analysis.deep)};
  line-height: 1.5;
  position: relative;
  transition: all 200ms ease-in-out;
  
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;

  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: ${({ expanded }) => (expanded ? 'unset' : 2)};
  max-height: ${({ expanded }) => (expanded ? 'none' : '3em')};
`;

const ToggleArrow = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'isHovered',
}) <{ isHovered?: boolean }>`
  position: absolute;
  top: .1rem;
  left: 2.8rem;
  cursor: pointer;
  user-select: none;
  z-index: 1;
  opacity: ${({ isHovered }) => (isHovered ? '1' : '0')};

  svg {
    font-size: 1.5rem;
    color: ${COLORS.analysis.deep};
  }
`;

const Expandable = styled.div`
  position: relative;
  padding-left: 4.5rem;
`;

const IconContainer = styled.div<{ color: string }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  color: ${({ color }) => color};
`;

const ScoreBox = styled.div.withConfig({
  shouldForwardProp: (prop) => prop !== 'background' && prop !== 'border',
}) <{ background: string; border: string }>`
  background: ${({ background }) => background}; 
  border: 1px solid ${({ border }) => border};
  width: 56px;
  height: 56px;
  margin: 0.17rem 1rem 0 0;
  box-sizing: border-box;
  flex-shrink: 0;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
`;

const AnalysisBox = styled.div`
  padding: 0;
  margin: 0;
`;


type AnalysisItemProps = {
  segment: Segment;
  index: number;
  isHovered?: boolean;
}

const AnalysisItem = ({ segment, isHovered, index }: AnalysisItemProps) => {
  const flags = segment.flags;

  if (!flags || flags.length === 0) {
    return (
      <div style={{ padding: '1em', fontStyle: 'italic', color: '#aaa' }}>
        No analysis needed...
      </div>
    );
  }

  const currentFlag = flags[0];
  const hasOnlyShallowFlags = flags?.every(f => f.source === "shallow");
  const hasDeepFlag = flags?.some(f => f.source === "deep");

  if (hasOnlyShallowFlags && !hasDeepFlag) {
    if (segment.status !== SegmentStatus.COMPLETE) {
      return <AnalysisResultsShimmer />;
    }
  }


  const {
    expandedIndex,
    setExpandedIndex,
    setModalContent,
    setModalOpen,
    modalOpen
  } = useUIContext();

  const isExpanded = expandedIndex === index;
  const iconColor = getSeverityTextColor(currentFlag.severity);
  const citationList = currentFlag.matches.length > 0
    ? currentFlag.matches.map(c => `"${c}"`).join(', ')
    : '';

  if (currentFlag.exit_reason !== ExitReason.NONE) {
    return (
      <AnalysisBox>
        <AnalysisExits flag={currentFlag} />
      </AnalysisBox>
    );
  }

  return (
    <AnalysisBox>
      <SummaryRow>
        <ScoreBox
          background={getSeverityBGColor(currentFlag.severity)}
          border={getSeverityBorder(currentFlag.severity)}
        >
          <IconContainer color={iconColor}>
            {getSeverityIcon(currentFlag.severity)}
          </IconContainer>
        </ScoreBox>
        <Summary>{currentFlag.summary}</Summary>
      </SummaryRow>


      <Expandable>
        <ToggleArrow
          isHovered={isHovered}
          onClick={() =>
            setExpandedIndex(prev => (prev === index ? null : index))
          }
        >
          {isExpanded ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
        </ToggleArrow>

        <DeepAnalysis isHovered={isHovered} expanded={isExpanded}>
          {currentFlag.text}
        </DeepAnalysis>

        {isExpanded && (
          <>
            <Citation isHovered={isHovered}><p style={{ color: COLORS.secondaryAccent }}>Citation:</p>{citationList}</Citation>
            <DeepSearchModal segment={segment} />
          </>
        )}
      </Expandable>
    </AnalysisBox>
  );
};


export default AnalysisItem;
