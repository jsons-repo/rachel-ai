# 🧠 Rachel View (Frontend)

This is the real-time transcript UI for Rachel, built with **React**, **Vite**, and **TypeScript**. It supports low-latency transcript streaming and dynamic updates through a modern virtualized interface.

## 🚀 Getting Started

We recommend using **Yarn**, but you can also use **npm** if preferred.

### 1. Clone the Repository

```bash
git clone git@github.com:jsons-repo/rachel-ai.git
cd rachel-view
```

### 2. Install Dependencies

#### Using Yarn (recommended)
```bash
yarn install
```

#### Using npm
```bash
npm install
```

### 3. Start the Development Server

#### Using Yarn
```bash
yarn dev
```

#### Using npm
```bash
npm run dev
```

This will:
- Generate the local config via `scripts/gen-config.ts`
- Start the Vite development server

### 4. Build for Production

#### Using Yarn
```bash
yarn build
```

#### Using npm
```bash
npm run build
```

### 5. Preview the Production Build

#### Using Yarn
```bash
yarn preview
```

#### Using npm
```bash
npm run preview
```

---

### To Use
The app should start in "paused" mode.

Click the arrow to start or pause.

 - Click any item to expand
 - Deep search will give a deeper analysis
 - Click on any transcription text to initiate manual search
