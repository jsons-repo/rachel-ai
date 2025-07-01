// src/components/ModalView.tsx
import { Modal, Box, IconButton, CircularProgress, Typography } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { COLORS } from '../styles';
import { Ellipsis } from './Shimmer';
import styled from 'styled-components';
import { useUIContext } from '../context/UIContext';

const ModalBox = styled(Box)`
  position: relative;
  padding: 2rem;
  background-color: rgb(30, 28, 26);
  width: 67%;
  height: calc(100vh - 33%);
  margin: 10vh auto;
  border-radius: 1rem;
  box-shadow: 2px 2px 10px #000;
  display: flex;
  flex-direction: column;
  overflow: hidden;

&:focus {
    outline: none;
  }
`;

const CloseButton = styled(IconButton)`
  position: absolute !important;
  top: 1rem;
  right: 1rem;
  z-index: 2;
`;

const ScrollArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding-right: 1rem;
`;

export const ModalView = () => {
    const {
        modalOpen,
        modalContent,
        modalLoading,
        setModalOpen
    } = useUIContext();

    const loadingText = "Running deep model"

    const handleClose = () => {
        setModalOpen(false);
    };

    return (
        <Modal open={modalOpen} onClose={handleClose}>
            <ModalBox onClick={(e) => e.stopPropagation()}>
                <CloseButton
                    aria-label="close"
                    onClick={handleClose}
                    sx={{
                        background: 'inherit',
                        color: COLORS.deepSearch.text.content,
                        '&:hover': {
                            background: COLORS.primaryAccent,
                            color: 'rgba(255, 255, 255, .9)',
                        },
                    }}
                >
                    <CloseIcon sx={{ fontSize: '2rem' }} />
                </CloseButton>

                <ScrollArea>
                    {modalLoading ? (
                        <Box
                            sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: 2,
                                height: '100%',
                            }}
                        >
                            <CircularProgress
                                size={30}
                                thickness={4}
                                sx={{ color: COLORS.primaryAccent }}
                            />
                            <Typography
                                variant="body1"
                                sx={{
                                    color: '#aaa',
                                    fontSize: '1rem',
                                    fontWeight: 400,
                                    letterSpacing: '0.5px',
                                }}
                            >
                                {loadingText}<Ellipsis />
                            </Typography>
                        </Box>
                    ) : modalContent}
                </ScrollArea>
            </ModalBox>
        </Modal>
    );
};
