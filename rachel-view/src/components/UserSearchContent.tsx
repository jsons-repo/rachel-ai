// src/components/UserSearchContent.tsx
import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { TextField, Button, Box } from '@mui/material';
import { BE_HOST, BE_PORT, BE_PROTOCOL, DEEP_NAME, DEEP_SEARCH_TEMP } from '../sharedConfig';
import { useUIContext } from '../context/UIContext';
import { COLORS, DeepHeader, DeepList, DeepMeta, DeepSubHeader, DeepText, StyledButton } from '../styles';
import {
    Timeline,
    TimelineItem,
    TimelineSeparator,
    TimelineConnector,
    TimelineContent,
    TimelineDot,
    TimelineOppositeContent
} from '@mui/lab';

const Container = styled.div`
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const InnerBox = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  width: 50%;
`;

const Citation = styled.div`
  font-size: 2rem;
  color: #eee;
  font-style: italic;
`

interface UserSearchContentProps {
    segmentId: string;
    selectedText: string;
}

export interface UserSearchResults {
    header: string;
    keyFigures: string[];
    timeline: string[];
    body: string;
    queryDuration: number
}

export const renderUserSearchResults = (result: UserSearchResults) => (
    <Box p={2}>
        <DeepHeader>{result.header}</DeepHeader>

        {result.keyFigures?.length > 0 && (
            <>
                <DeepHeader>Key Figures:</DeepHeader>
                <DeepList>{result.keyFigures.map((k: string, i: number) => <li key={i}>{k}</li>)}</DeepList>
            </>
        )}


        {result.timeline?.length > 0 && (
            // <>
            //     <h4>Timeline:</h4>
            //     <ol>{result.timeline.map((t: string, i: number) => <li key={i}>{t}</li>)}</ol>
            // </>
            <>
                <DeepHeader>Timeline:</DeepHeader>
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
            </>
        )}
        <DeepText>{result.body}</DeepText>
        <DeepMeta>
            <span>Context: <i>{result.header}</i></span>
            <span>Model: {DEEP_NAME}</span>
            <span>Duration: {result.queryDuration}s</span>
            <span>Temperature: {DEEP_SEARCH_TEMP}</span>
        </DeepMeta>
    </Box>
);


export const UserSearchContent = ({ segmentId, selectedText }: UserSearchContentProps) => {
    const [query, setQuery] = useState('');
    const [focused, setFocused] = useState(false);
    const { setModalLoading, setModalContent } = useUIContext();
    const inputRef = useRef<HTMLInputElement | null>(null);


    const handleSearch = async () => {
        setModalLoading(true);
        try {
            const url = `${BE_PROTOCOL}://${BE_HOST}:${BE_PORT}/user-search`;
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    segment_id: segmentId,
                    selected_text: selectedText,
                    query,
                }),
            });
            const result = await response.json();
            setModalContent(renderUserSearchResults({
                header: result.headline,
                body: result.body,
                keyFigures: result.key_figures,
                timeline: result.timeline,
                queryDuration: result.query_duration
            } as UserSearchResults));
        } catch (err) {
            setModalContent(<div style={{ color: 'red' }}>Error: {String(err)}</div>);
        } finally {
            setModalLoading(false);
        }
    };

    const inputStyles = {
        margin: '4rem 0 1rem 0',
        backgroundColor: 'rgba(52, 46, 43, 0.4)',
        label: {
            color: '#aaa',
            '&.Mui-focused': {
                color: '#aaa',
            },
        },
        '& .MuiOutlinedInput-root': {
            '& fieldset': {
                borderColor: '#444',
            },
            '&:hover fieldset': {
                borderColor: '#444',
            },
            '&.Mui-focused fieldset': {
                borderColor: COLORS.primaryAccent,
            },
            '& textarea': {
                fontStyle: !focused && !query ? 'italic' : 'normal',
                color: !focused && !query ? '#888' : '#ddd',
                transition: 'all 0.2s ease-in-out',
            },
        },
    };




    return (
        <Container>
            <InnerBox>
                <Citation>"{selectedText}"</Citation>
                <TextField
                    inputRef={inputRef}
                    label="Add details"
                    variant="outlined"
                    multiline
                    maxRows={3}
                    minRows={focused ? 2 : 1}
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(!!query)}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    fullWidth
                    sx={inputStyles}
                />
                <StyledButton
                    variant="contained"
                    onClick={handleSearch}
                    sx={{
                        backgroundColor: COLORS.primaryAccent,
                        width: '11rem',
                        color: '#fff',
                        '&:hover': {
                            backgroundColor: COLORS.primaryAccent, // or a lighter/darker variant if you have one
                            opacity: 0.9,
                        },
                    }}
                >
                    Deep Search
                </StyledButton>

            </InnerBox>
        </Container>
    );
};
