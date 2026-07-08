'use client';

import React from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import Navigation from '@/components/Navigation';

// Component imports
import LandingPage from '@/components/LandingPage';
import AuthScreen from '@/components/AuthScreen';
import OnboardingFlow from '@/components/OnboardingFlow';
import Dashboard from '@/components/Dashboard';
import SafeRoutes from '@/components/SafeRoutes';
import AIGuardian from '@/components/AIGuardian';
import CommunityFeed from '@/components/CommunityFeed';
import IncidentForm from '@/components/IncidentForm';
import GuardianMode from '@/components/GuardianMode';
import EmergencySOS from '@/components/EmergencySOS';
import ProfilePanel from '@/components/ProfilePanel';
import SettingsPanel from '@/components/SettingsPanel';
import AnalyticsPanel from '@/components/AnalyticsPanel';

import { ShieldCheck, Compass, Info, MapPin } from 'lucide-react';

export default function Home() {
  const { currentView, activeJourney, safetyScore } = useSafeStore();

  // Helper to render active tab views
  const renderCurrentView = () => {
    switch (currentView) {
      case 'landing':
        return <LandingPage />;
      case 'auth':
        return <AuthScreen />;
      case 'onboarding':
        return <OnboardingFlow />;
      case 'dashboard':
        return <Dashboard />;
      case 'routes':
        return <SafeRoutes />;
      case 'ai-guardian':
        return <AIGuardian />;
      case 'community':
        return <CommunityFeed />;
      case 'report':
        return <IncidentForm />;
      case 'guardian-mode':
        return <GuardianMode />;
      case 'emergency':
        return <EmergencySOS />;
      case 'profile':
        return <ProfilePanel />;
      case 'settings':
        return <SettingsPanel />;
      case 'analytics':
        return <AnalyticsPanel />;
      default:
        return <LandingPage />;
    }
  };

  return (
    <div className="relative min-h-screen bg-[#050816] text-white flex flex-col">
      {/* Global Particle Overlay & Aurora backgrounds */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-accent-primary/5 blur-[120px] animate-aurora-1" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[550px] h-[550px] rounded-full bg-accent-ai/5 blur-[130px] animate-aurora-2" />
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:40px_40px] opacity-40" />
      </div>

      {/* Floating Header Navigation Bar */}
      <Navigation />

      {/* Active Journey Top Overlay Alert Banner (if travelling and not on full screen modes) */}
      {activeJourney && 
       activeJourney.started && 
       currentView !== 'emergency' && 
       currentView !== 'guardian-mode' && (
        <div className="fixed bottom-20 md:bottom-6 left-4 right-4 md:left-6 md:right-auto md:w-80 z-30">
          <div className="p-3 rounded-xl glass-panel-glow border-accent-ai/30 bg-bg-secondary/90 flex items-center justify-between shadow-lg text-[10px]">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-accent-ai animate-ping" />
              <div className="flex flex-col">
                <span className="font-bold text-white uppercase tracking-wider">Active Commute Tracking</span>
                <span className="text-text-secondary">Destination: {activeJourney.destination} &bull; ETA {activeJourney.eta}</span>
              </div>
            </div>
            <div className="flex items-center gap-1 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 text-emerald-400 font-bold uppercase tracking-wider">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>{safetyScore}% Safe</span>
            </div>
          </div>
        </div>
      )}

      {/* Active Content Screen container */}
      <div className="relative z-10 flex-1 flex flex-col">
        {renderCurrentView()}
      </div>

      {/* Footer bar (only on landing page) */}
      {currentView === 'landing' && (
        <footer className="relative z-10 border-t border-white/5 py-8 text-center text-xs text-text-secondary bg-[#03060f]">
          <p>&copy; {new Date().getFullYear()} WoSafe Technologies, Inc. All rights protected.</p>
        </footer>
      )}
    </div>
  );
}
