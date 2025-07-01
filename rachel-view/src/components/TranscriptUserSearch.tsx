// src/components/TranscriptUserSearch.tsx
import React, { useState } from 'react';
import axios from 'axios';
import { Button, Box, Typography } from '@mui/material';
import { BE_HOST, BE_PORT, BE_PROTOCOL } from '../sharedConfig';
import { useUIContext } from '../context/UIContext';

interface TranscriptUserSearchProps {
    query: string;
    segmentId: string;
}

export const TranscriptUserSearch = ({ query, segmentId }: TranscriptUserSearchProps) => {
    const [confirmed, setConfirmed] = useState(false);
    const { setModalContent } = useUIContext();

    const handleConfirm = async () => {
        setConfirmed(true);
        try {
            const url = `${BE_PROTOCOL}://${BE_HOST}:${BE_PORT}/user-search`;
            const res = await axios.post(url, {
                segment_id: segmentId,
                query,
            });

            const content = res.data?.result || 'No result returned.';
            setModalContent(<div>📄 {content}</div>);
        } catch (err) {
            console.error("User search error:", err);
            setModalContent(<div>❌ Error fetching result.</div>);
        }
    };

    if (!confirmed) {
        return (
            <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
                <Typography>Search for "{query}"?</Typography>
                <Button variant="contained" onClick={handleConfirm}>
                    Confirm
                </Button>
            </Box>
        );
    }

    return <Typography>🔄 Loading...</Typography>;
};
