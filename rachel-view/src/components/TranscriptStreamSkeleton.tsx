import { Box, Skeleton } from "@mui/material"
import { Row, RowItem } from "./TranscriptStream"

export const SegmentSkeleton = () => {
    return (<Row style={{ background: 'transparent', margin: 0, padding: 0, height: '15rem' }}>
        <RowItem style={{ flex: '0 0 10%', padding: '0 2rem 0 2rem', minWidth: '12rem' }}>
            <Box style={{ width: '5rem', height: '100%' }}>
                <Skeleton style={{ height: '12rem', background: 'rgba(94, 89, 82, 0.15)' }} />
            </Box>
        </RowItem>
        <RowItem
            style={{
                flex: '0 0 20%',
                minWidth: '20rem',
                padding: '2rem 4rem',
                margin: 0
            }}
        >
            <Box style={{ width: '100%', height: '100%', marginTop: '0rem' }}>
                <Skeleton style={{ height: '4rem', background: 'rgba(94, 89, 82, 0.15)' }} />
                <Skeleton style={{ height: '4rem', background: 'rgba(94, 89, 82, 0.15)' }} />
            </Box>
        </RowItem>
        <RowItem style={{
            flex: '1 0 0',
            padding: '0rem 3rem',
            margin: 0
        }}>
            <Box style={{ width: '100%', height: '100%' }}>
                <Skeleton style={{ height: '4rem', background: 'rgba(94, 89, 82, 0.15)', marginBottom: '.25rem' }} />
                <Skeleton style={{ height: '1.9rem', background: 'rgba(94, 89, 82, 0.15)' }} />
                <Skeleton style={{ height: '1.9rem', background: 'rgba(94, 89, 82, 0.15)' }} />
            </Box>
        </RowItem>
    </Row>)
}