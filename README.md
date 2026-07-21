# 🛡️ WoSafe — AI-Powered Women's Safety Intelligence Platform

> **Tagline:** *"AI That Protects Before Danger Begins."*

Welcome to the frontend codebase for **WoSafe**, the world’s most advanced AI-powered Women’s Safety Intelligence Platform. This repository hosts the responsive, interactive, and premium Next.js client interface. 


Unlike traditional SOS alert buttons, WoSafe is a complete safety cockpit. It uses real-time threat intelligence, ambient lighting assessments, and predictive risk mapping to keep users safe on their daily journeys.


---

## 💎 Design Philosophy & UI Aesthetics

WoSafe is built with a premium, state-of-the-art interface designed to feel reliable and calm in critical moments:
* **Glassmorphism Panels**: Semi-transparent frosted-glass containers over deep dark-space backgrounds.
* **Micro-Animations**: Power-efficient transitions using `framer-motion` for tactile response during high-stress inputs.
* **Dynamic Threat Gauges**: Neon pulsing indicators (Emerald Green for Safe, Amber for Moderate, Blood-Red for Critical SOS).
* **Mobile-First Responsive Layout**: Optimised for single-hand gestures, bottom navigation layout, and instantaneous response times.

---

## ⚡ Core Frontend Features

### 1. 🛡️ Safety Cockpit Dashboard
* **Dynamic Geolocation Assessment**: Displays a real-time localized Safety Index Score from 0 to 100.
* **One-Click Guardian Mode**: Calibrates background microphone scanners and location tracking telemetry instantly.
* **Ambient Lighting & Waveform HUD**: Visualises live microphone levels and audio calibration.


### 2. 🗺️ Neural Safe Routing (`SafeRoutes`)
* **Safest Neural Path**: Recommends routes based on highest verified lighting coverage and active police checkpoints rather than just the shortest distance.
* **Commute Details**: Displays live ETA, distance, active checkpoint counts, and verified safe businesses along the path.


### 3. 🚨 Emergency SOS Dispatch HUD
* **5-Second Dispatch Countdown**: Prevents false alarms while allowing immediate emergency alert escalation.
* **Localised Survival Guides**: Step-by-step physical defense and tactical strategies based on specific situations.
* **Priority Contact Dialing**: Quick links to place cellular calls to trusted guardians.

### 4. 💬 AI Guardian Core (`AIGuardian`)
* **Fully Encrypted Chat Interface**: A secure dialog helper powered by conversational AI.
* **Natural Threat Recognition**: Automatically activates Emergency SOS if critical safety phrases or the vocal Safe Word (`"Phoenix"`) is spoken or typed.

### 5. 👥 Crowdsourced Intelligence Feed (`CommunityFeed`)
* **Geotagged Safety Testimonies**: Users can file reports categorized by category (Harassment, Infrastructure Deficit, Unsafe Area).
* **AI Incident Summarization**: Generates brief, objective two-sentence summary summaries of descriptions via the backend LLM.
* **Peer Upvoting System**: Community members verify report credibility in real time.

---


## 🛠️ Technology Stack

* **Framework**: [Next.js 16 (App Router)](https://nextjs.org/)
* **Language**: [TypeScript](https://www.typescriptlang.org/)
* **State Management**: [Zustand](https://github.com/pmndrs/zustand)
* **Styling**: Tailwind CSS & Modern Custom CSS variables
* **Icons**: [Lucide React](https://lucide.dev/)
* **Animations**: [Framer Motion](https://www.framer.com/motion/)

---

## 📁 Repository Structure

```
├── public/                 # Static assets and icons
├── src/
│   ├── app/                # Next.js App Router (Layout & main wrapper)
│   ├── components/         # Premium UI Components
│   │   ├── AIGuardian.tsx      # AI Chat Assistant Core
│   │   ├── AuthScreen.tsx      # Firebase auth screen (Dev mode bypass)
│   │   ├── CommunityFeed.tsx   # Incident alerts & peer verification
│   │   ├── Dashboard.tsx       # Main safety cockpit dial
│   │   ├── EmergencySOS.tsx    # Panic button & survival strategies HUD
│   │   ├── GuardianMode.tsx    # Live tracking telemetry panel
│   │   ├── IncidentForm.tsx    # AI-summarized hazard reporting form
│   │   ├── Navigation.tsx      # Navigation sidebar / Mobile bottom bar
│   │   ├── OnboardingFlow.tsx  # Initial profiles, contacts, and preferences
│   │   ├── SafeRoutes.tsx      # Path scoring & routing parameters
│   │   └── SettingsPanel.tsx   # System permissions and acoustic configuration
│   ├── services/
│   │   └── api.ts          # Central type-safe backend API Client
│   └── store/
│       └── useSafeStore.ts # Centralized Zustand client state management
├── package.json
└── tsconfig.json
```

---

## 📡 Backend Integration (`src/services/api.ts`)

The frontend communicates with a FastAPI REST server via a centralized HTTP helper. In development, it falls back to local simulation states to allow seamless offline preview:
* **Base URL**: `http://127.0.0.1:8000/api/v1`
* **Authorization**: Bearer JWT tokens stored in `localStorage` (`wosafe_access_token`).

---

## 🚀 Getting Started

### Prerequisites
* **Node.js**: `v18.x` or higher
* **npm** or **yarn**

### 1. Install Dependencies
```bash
npm install
```

### 2. Run the Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) (or `http://localhost:3001` if port 3000 is occupied) to view the application.

### 3. Check for Lints and Code Problems
```bash
npm run lint
```

### 4. Build for Production
```bash
npm run build
```
This command compiles TypeScript files, runs ESLint validations, and generates optimized static pages.
