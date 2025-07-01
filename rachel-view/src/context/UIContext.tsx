// src/context/UIContext.tsx
import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect
} from 'react';
import { useSegmentContext } from './SegmentContext';

export enum PipelineState {
  IDLE = 'idle',
  PENDING = 'pending',
  ACTIVE = 'active',
}

type UIContextType = {
  expandedIndex: number | null;
  setExpandedIndex: React.Dispatch<React.SetStateAction<number | null>>;
  hoverIndex: number | null;
  setHoverIndex: React.Dispatch<React.SetStateAction<number | null>>;
  shouldAutoScroll: boolean;
  setShouldAutoScroll: React.Dispatch<React.SetStateAction<boolean>>;
  modalOpen: boolean;
  setModalOpen: React.Dispatch<React.SetStateAction<boolean>>;
  modalContent: React.ReactNode | null;
  setModalContent: React.Dispatch<React.SetStateAction<React.ReactNode | null>>;
  modalLoading: boolean;
  setModalLoading: React.Dispatch<React.SetStateAction<boolean>>;
  pipelineState: PipelineState;
  setPipelineState: React.Dispatch<React.SetStateAction<PipelineState>>;
};

const UIContext = createContext<UIContextType | undefined>(undefined);

export const useUIContext = () => {
  const context = useContext(UIContext);
  if (!context) throw new Error('useUIContext must be used within UIStateProvider');
  return context;
};

export const UIStateProvider = ({ children }: { children: ReactNode }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState<React.ReactNode | null>(null);
  const [modalLoading, setModalLoading] = useState<boolean>(false);
  const [pipelineState, setPipelineState] = useState<PipelineState>(PipelineState.IDLE);

  const { streamState, segments } = useSegmentContext(); // 👈 access segment state

  useEffect(() => {
    if (streamState === 'LISTENING' && segments.length > 0) {
      setPipelineState(PipelineState.ACTIVE);
    }
  }, [streamState, segments.length]);

  return (
    <UIContext.Provider value={{
      expandedIndex,
      setExpandedIndex,
      hoverIndex,
      setHoverIndex,
      shouldAutoScroll,
      setShouldAutoScroll,
      modalOpen,
      setModalOpen,
      modalContent,
      setModalContent,
      modalLoading,
      setModalLoading,
      pipelineState,
      setPipelineState
    }}>
      {children}
    </UIContext.Provider>
  );
};
