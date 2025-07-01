// src/styles.ts
import { Button } from '@mui/material';
import styled, { createGlobalStyle } from 'styled-components';

const _color = {
  primaryText: 'rgb(220, 220, 220)',
  secondaryText: 'rgb(130, 130, 130)',
  lightGray: 'rgb(190, 190, 190)',
  darkGray: 'rgb(84, 84, 84)',
  primaryAccent: 'rgb(255, 0, 170)',
  secondaryAccent: 'rgb(18, 172, 244)',
  high: 'rgb(255, 10, 88)',
  medium: 'rgb(208, 193, 23)',
  low: 'rgb(129, 255, 11)',
}

export const GLOBAL_STYLES = {
  transition: {
    background: "180ms ease-in-out",
    text: "190ms ease-in-out"
  },
}

export const COLORS = {
  primaryText: _color.primaryText,
  secondaryText: _color.secondaryText,
  primaryAccent: _color.primaryAccent,
  secondaryAccent: _color.secondaryAccent,
  deepSearch: {
    text: {
      content: 'rgba(255, 2555, 255, .7)'
    }
  },
  status: {
    statusBorder: _color.secondaryAccent,
    inactive: _color.darkGray,
    activeAccent: _color.secondaryAccent,
    activeText: '#eee'
  },
  analysis: {
    headline: _color.primaryText,
    deep: _color.secondaryText,
  },
  citation: {
    text: _color.secondaryText,
    highlight: {
      text: 'rgba(0, 0, 0, 1)',
      background: _color.secondaryAccent
    },
  },
  table: {
    background: 'rgba(69, 69, 69, 0.0)',
    backgroundGradiant: {
      start: _color.secondaryAccent,
      end: _color.primaryAccent
    },
    border: 'rgba(0, 0, 0, 0)',
    cellDividerBorder: 'rgba(255, 255, 255, 0.05)',
    cellBackground: 'rgb(29, 30, 28)',
    cellBackgroundHover: 'rgb(31, 30, 29)'
  },
  metrics: {
    label: _color.darkGray,
    text: _color.lightGray
  },
  severity: {
    text: {
      high: _color.high,
      medium: _color.medium,
      low: _color.low,
    },
    background: {
      high: 'rgba(255, 111, 111, 0.15)',
      medium: 'rgba(255, 215, 147, 0.12)',
      low: 'rgba(170, 255, 151, 0.12)',
    },
    border: {
      high: _color.high,
      medium: _color.medium,
      low: _color.low,
    },
  },
};

export const GlobalStyle = createGlobalStyle`
  /* Import Google Fonts */
  @import url('https://fonts.googleapis.com/css2?family=Courier+Prime&family=Montserrat:wght@600&display=swap');

  html, body, #root {
    margin: 0;
    padding: 0;
    height: 100%;
    width: 100%;
    background-color: #000;
    box-sizing: border-box;
    color: ${_color.primaryText};
    font-family: 'Montserrat', sans-serif;
    overflow-x: hidden;
  }

  *, *::before, *::after {
    box-sizing: inherit;
  }

  code {
    font-family: 'Courier Prime', monospace;
  }

  /* Optional: Disable scrollbars globally if desired */
  ::-webkit-scrollbar {
    display: none;
  }
  body {
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none;  /* IE/Edge */
  }
`;

export const StyledButton = styled(Button)(() => ({
  '&.MuiButton-root': {
    marginTop: '2em',
    borderRadius: '8px',
    padding: '0.75em 2em',
    fontWeight: 600,
    letterSpacing: '0.03em',
    textTransform: 'none',
    backgroundColor: 'rgba(34, 191, 239, .07)',
    border: `1px solid ${COLORS.secondaryAccent}`,
    color: COLORS.secondaryAccent,
    transition: 'all 0.2s ease-in-out',

    '&:hover': {
      backgroundColor: 'rgba(34, 191, 239, .2)',
      color: '#fff'
    },

    '&:disabled': {
      backgroundColor: '#555',
      color: '#aaa',
      opacity: 0.6,
      cursor: 'not-allowed',
    },
  },
}));


export const Container = styled.div`
  height: 100vh;
  width: 100vw;
  overflow-y: auto;
  display: flex;
  flex-direction: row;
  background: linear-gradient(45deg, ${COLORS.table.backgroundGradiant.start} 0%, ${COLORS.table.backgroundGradiant.end} 80%);
  box-sizing: border-box;
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    width: 0;
    height: 0;
  }

  scrollbar-gutter: stable both-edges;
`;

export const ColorFadeContainer = styled.div`
  height: 100vh;
  width: 100vw;
  overflow-y: auto;
  display: flex;
  flex-direction: row;
  border: '5px solid green';
  background: ${COLORS.table.background};
`

export const DeepHeader = styled.div`
  font-family: 'Montserrat', sans-serif;
  font-size: 1.4rem;
  font-weight: 600;
  color: ${COLORS.analysis.headline};
  margin: 3rem 0 0.5rem 0;
`;

export const DeepSubHeader = styled.div`
  font-family: 'Montserrat', sans-serif;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.8rem;
  color: ${COLORS.analysis.headline};
  margin: 0 0 2rem 0;
  padding: 0;
  flex: 1;
  display: flex;
  flex-wrap: wrap;
`;

export const DeepList = styled.ul`
  padding-left: 1.5rem;
  margin: 0 0 1.5rem 0;
  color: ${COLORS.analysis.headline};
  font-size: 1.1rem;
  line-height: 1.6rem;
  font-style: italic;

  li {
    margin-bottom: 0.25rem;
  }
`;

export const DeepText = styled.div`
  font-family: 'Montserrat', sans-serif;
  font-size: 1.05rem;
  font-weight: 400;
  line-height: 1.8rem;
  color: rgba(255, 255, 255, .7);
  margin: 0;
  padding: 0;
`;

export const DeepMeta = styled.div`
  margin-top: 4rem;
  padding-top: 1rem;
  border-top: 1px solid #555;
  color: #777;
  font-size: .85rem;
  line-height: 1.5rem;
  display: flex;
  flex-direction: column;
`;
