// App.tsx
import { ColorFadeContainer, Container, GlobalStyle } from './styles';
import TranscriptStream from './components/TranscriptStream';
import { UIStateProvider } from './context/UIContext';
import { TopMetricsBar } from './components/SystemMetrics';
import { SegmentStreamProvider } from './context/SegmentContext';
import { FeedStatus } from './components/FeedStatus';
import { ModalView } from './components/ModalView';

const App = () => {
  return (
    <>
      <GlobalStyle />
      <SegmentStreamProvider>
        <UIStateProvider>
          <FeedStatus />
          <Container>
            <ColorFadeContainer>
              {/* <TopMetricsBar /> */}

              <TranscriptStream />
            </ColorFadeContainer>
          </Container>
          <ModalView />
        </UIStateProvider>
      </SegmentStreamProvider>
    </>
  );
};

export default App;