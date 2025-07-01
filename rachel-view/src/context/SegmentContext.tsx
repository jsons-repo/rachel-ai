// src/context/SegmentContext.tsx
import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  ReactNode,
} from 'react';
import { Segment } from '../types';
import { BE_HOST, BE_PORT, BE_PROTOCOL } from '../sharedConfig';
import { FEED_STATUS } from '../components/FeedStatus';
import { real_example } from '../dummy/chunks';

// Context type
interface SegmentContextType {
  segments: Segment[];
  setSegments: React.Dispatch<React.SetStateAction<Segment[]>>;
  streamState: FEED_STATUS;
  setStreamState: React.Dispatch<React.SetStateAction<FEED_STATUS>>;
}

const SegmentContext = createContext<SegmentContextType | undefined>(undefined);

export const useSegmentContext = () => {
  const context = useContext(SegmentContext);
  if (!context) throw new Error('useSegmentContext must be used within SegmentProvider');
  return context;
};

const mergeSegment = (prev: Segment, next: Segment): Segment => ({
  ...prev,
  ...next,
  flags: next.flags ?? prev.flags,
  status: next.status ?? prev.status,
});


// 🔒 Module-global connection holder
let sourceRef: EventSource | null = null;
let retryTimeoutRef: number | null = null;

const useStream = (
  setSegments: React.Dispatch<React.SetStateAction<Segment[]>>,
  setStreamState: React.Dispatch<React.SetStateAction<FEED_STATUS>>
) => {
  useEffect(() => {
    const connect = () => {
      if (sourceRef) {
        return;
      }

      const url = `${BE_PROTOCOL}://${BE_HOST}:${BE_PORT}/stream`;
      setStreamState(FEED_STATUS.CONNECTION);
      sourceRef = new EventSource(url);

      sourceRef.onopen = () => {
        console.log('[SSE] Connection opened');
        setStreamState(FEED_STATUS.LISTENING);
      };

      sourceRef.onmessage = (event) => {
        try {
          const data: Segment = JSON.parse(event.data);
          setSegments((prev) => {
            const existingIndex = prev.findIndex((seg) => seg.id === data.id);
            let updated: Segment[];

            if (existingIndex !== -1) {
              const existing = prev[existingIndex];
              const isNewer =
                !existing.last_updated || !data.last_updated || data.last_updated > existing.last_updated;

              if (isNewer) {
                updated = [...prev];
                updated[existingIndex] = data;
              } else {
                // Skip stale update
                return prev;
              }
            } else {
              updated = [...prev, data];
            }

            updated.sort((a, b) => a.start - b.start);
            return updated;
          });

          setStreamState(FEED_STATUS.LISTENING);
        } catch (e) {
          console.error('[SSE] Failed to parse event data:', e);
          setStreamState(FEED_STATUS.ERROR);
        }
      };


      sourceRef.onerror = (err) => {
        console.log('[SSE] Error — reconnecting in 5s:', err);
        sourceRef?.close();
        sourceRef = null;
        setStreamState(FEED_STATUS.CONNECTION);

        if (retryTimeoutRef) clearTimeout(retryTimeoutRef);

        retryTimeoutRef = window.setTimeout(() => {
          console.log('[SSE] Retrying connection...');
          sourceRef = null;
          connect(); // ⬅️ manually call reconnect
        }, 2000);
      };



      return () => {
        sourceRef?.close();
        sourceRef = null;
        retryTimeoutRef && clearTimeout(retryTimeoutRef);
      };
    }

    connect();
  }, []);
};


export const SegmentStreamProvider = ({ children }: { children: ReactNode }) => {
  const [segments, setSegments] = useState<Segment[]>([]);
  const [streamState, setStreamState] = useState<FEED_STATUS>(FEED_STATUS.CONNECTION);

  useStream(setSegments, setStreamState);

  return (
    <SegmentContext.Provider value={{ segments, setSegments, streamState, setStreamState }}>
      {children}
    </SegmentContext.Provider>
  );
};
