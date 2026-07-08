'use client';

import React from 'react';
import { useSafeStore, ViewType } from '@/store/useSafeStore';
import { 
  Shield, 
  LayoutDashboard, 
  MapPin, 
  MessageSquareCode, 
  Users, 
  FileWarning, 
  BarChart3, 
  Settings, 
  User,
  AlertTriangle
} from 'lucide-react';

export default function Navigation() {
  const { currentView, setCurrentView, setEmergencyActive } = useSafeStore();

  // Hide navigation on full-screen emergency or guardian mode
  if (currentView === 'emergency' || currentView === 'guardian-mode') {
    return null;
  }

  const navItems: { view: ViewType; label: string; icon: React.ReactNode }[] = [
    { view: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { view: 'routes', label: 'Safe Routes', icon: <MapPin className="w-4 h-4" /> },
    { view: 'ai-guardian', label: 'AI Guardian', icon: <MessageSquareCode className="w-4 h-4" /> },
    { view: 'community', label: 'Community', icon: <Users className="w-4 h-4" /> },
    { view: 'report', label: 'Report', icon: <FileWarning className="w-4 h-4" /> },
    { view: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
    { view: 'profile', label: 'Profile', icon: <User className="w-4 h-4" /> },
    { view: 'settings', label: 'Settings', icon: <Settings className="w-4 h-4" /> },
  ];

  // Mobile navigation items (limited to 5 key actions)
  const mobileNavItems: { view: ViewType; label: string; icon: React.ReactNode }[] = [
    { view: 'dashboard', label: 'Cockpit', icon: <LayoutDashboard className="w-5 h-5" /> },
    { view: 'routes', label: 'Routes', icon: <MapPin className="w-5 h-5" /> },
    { view: 'ai-guardian', label: 'AI Guardian', icon: <MessageSquareCode className="w-5 h-5" /> },
    { view: 'community', label: 'Feed', icon: <Users className="w-5 h-5" /> },
    { view: 'profile', label: 'Profile', icon: <User className="w-5 h-5" /> },
  ];

  return (
    <>
      {/* Top Navigation Bar (Visible on all devices, hides links on mobile) */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-4 py-3 mx-auto max-w-7xl">
        <div className="flex items-center justify-between w-full px-6 py-2.5 glass-panel rounded-2xl border-white/5 bg-bg-secondary/40 backdrop-blur-md">
          
          {/* Logo / Brand */}
          <div 
            onClick={() => setCurrentView('landing')} 
            className="flex items-center gap-2 cursor-pointer group"
          >
            <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-accent-primary/20 border border-accent-primary/30 group-hover:border-accent-primary/60 transition-all duration-300">
              <Shield className="w-4 h-4 text-accent-primary group-hover:scale-110 transition-transform duration-300" />
              <div className="absolute inset-0 rounded-lg bg-accent-primary/20 blur group-hover:blur-md opacity-50 group-hover:opacity-100 transition-all duration-300" />
            </div>
            <span className="text-lg font-bold tracking-tight text-white group-hover:text-glow-primary transition-all duration-300">
              WoSafe
            </span>
          </div>

          {/* Desktop Navigation Links (hidden on mobile) */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = currentView === item.view;
              return (
                <button
                  key={item.view}
                  onClick={() => setCurrentView(item.view)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all duration-300 border ${
                    isActive
                      ? 'bg-accent-primary/15 border-accent-primary/30 text-white shadow-[0_0_15px_rgba(108,99,255,0.15)]'
                      : 'border-transparent text-text-secondary hover:text-white hover:bg-white/5'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* Navigation Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Landing / Sign-in Toggle */}
            {currentView === 'landing' ? (
              <button 
                onClick={() => setCurrentView('auth')}
                className="px-4 py-1.5 text-xs font-semibold rounded-xl border border-white/10 text-white hover:bg-white/5 hover:border-white/20 transition-all duration-300"
              >
                Sign In
              </button>
            ) : (
              <button 
                onClick={() => setCurrentView('landing')}
                className="hidden lg:block px-4 py-1.5 text-xs font-semibold rounded-xl border border-white/5 text-text-secondary hover:text-white hover:bg-white/5 transition-all duration-300"
              >
                Home
              </button>
            )}

            {/* SOS Trigger */}
            <button
              onClick={() => {
                setEmergencyActive(true);
                setCurrentView('emergency');
              }}
              className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold text-white rounded-xl bg-danger-custom hover:bg-red-600 transition-all duration-300 shadow-[0_0_15px_rgba(255,77,109,0.4)] hover:shadow-[0_0_25px_rgba(255,77,109,0.7)] animate-pulse"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>SOS</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Floating Bottom Navigation Bar (Mobile Viewports Only) */}
      {currentView !== 'landing' && currentView !== 'auth' && currentView !== 'onboarding' && (
        <div className="md:hidden fixed bottom-4 left-4 right-4 z-40">
          <div className="flex items-center justify-around py-2.5 glass-panel rounded-2xl border-white/10 bg-bg-secondary/75 backdrop-blur-lg shadow-2xl">
            {mobileNavItems.map((item) => {
              const isActive = currentView === item.view;
              return (
                <button
                  key={item.view}
                  onClick={() => setCurrentView(item.view)}
                  className={`flex flex-col items-center justify-center gap-1 px-3 py-1 rounded-xl transition-all duration-300 ${
                    isActive 
                      ? 'text-accent-ai scale-110' 
                      : 'text-text-secondary hover:text-white'
                  }`}
                >
                  <div className={isActive ? 'text-glow-ai' : ''}>
                    {item.icon}
                  </div>
                  <span className="text-[9px] font-medium tracking-tight">
                    {item.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
}
