'use client';

import React, { useState, useEffect } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion } from 'framer-motion';
import { 
  CloudSun, 
  BatteryCharging, 
  Wifi, 
  ShieldCheck, 
  Compass, 
  ShieldAlert, 
  Users, 
  MessageSquareCode, 
  ChevronRight,
  TrendingUp,
  MapPin,
  Flame,
  Radio,
  Lock,
  Plus
} from 'lucide-react';
import SafetyMap from './SafetyMap';

export default function Dashboard() {
  const { 
    currentView, 
    setCurrentView, 
    user, 
    safetyScore, 
    setSafetyScore, 
    guardianModeActive, 
    setGuardianModeActive,
    setEmergencyActive,
    notifications
  } = useSafeStore();

  const [time, setTime] = useState('');
  const [battery, setBattery] = useState(87);

  // Time and Battery updates
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateTime();
    const tInterval = setInterval(updateTime, 1000);

    // Battery simulation
    const bInterval = setInterval(() => {
      setBattery(prev => {
        if (prev <= 1) return 100;
        return prev - 1;
      });
    }, 120000);

    return () => {
      clearInterval(tInterval);
      clearInterval(bInterval);
    };
  }, []);

  // Determine safety level parameters
  const getSafetyDetails = (score: number) => {
    if (score >= 90) return { label: 'Safe', color: 'text-success-custom', stroke: '#00D26A', glow: 'shadow-[0_0_20px_rgba(0,210,106,0.35)]', bg: 'bg-emerald-500/10 border-emerald-500/20' };
    if (score >= 70) return { label: 'Moderate', color: 'text-warning-custom', stroke: '#F8C630', glow: 'shadow-[0_0_20px_rgba(248,198,48,0.35)]', bg: 'bg-amber-500/10 border-amber-500/20' };
    if (score >= 40) return { label: 'High Risk', color: 'text-orange-400', stroke: '#FB923C', glow: 'shadow-[0_0_20px_rgba(251,146,60,0.35)]', bg: 'bg-orange-500/10 border-orange-500/20' };
    return { label: 'Critical', color: 'text-danger-custom', stroke: '#FF4D6D', glow: 'shadow-[0_0_20px_rgba(255,77,109,0.35)]', bg: 'bg-red-500/10 border-red-500/20' };
  };

  const safetyInfo = getSafetyDetails(safetyScore);

  // SVG Gauge variables
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (safetyScore / 100) * circumference;

  return (
    <div className="relative min-h-screen bg-bg-primary overflow-hidden pt-24 pb-28 md:pb-16 px-4">
      
      {/* Background radial overlays */}
      <div className="absolute top-1/3 left-1/4 w-[350px] h-[350px] rounded-full bg-accent-primary/5 blur-[90px] animate-pulse pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[350px] h-[350px] rounded-full bg-accent-ai/5 blur-[90px] animate-pulse pointer-events-none" />

      <main className="mx-auto max-w-7xl space-y-6 relative z-10">
        
        {/* Top Status Header */}
        <section className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          
          {/* Welcome greeting */}
          <div className="md:col-span-6 flex flex-col space-y-1">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">
              Good evening, {user.name.split(' ')[0]}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-text-secondary text-xs font-medium">
              <span className="flex items-center gap-1">
                <CloudSun className="w-3.5 h-3.5 text-amber-400" />
                72°F · Clear Sky
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-white/20" />
              <span className="font-mono tracking-wider">{time}</span>
            </div>
          </div>

          {/* Diagnostics widgets */}
          <div className="md:col-span-6 flex flex-wrap gap-2 md:justify-end">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-white/5 bg-bg-secondary/40 text-[10px] font-bold text-white uppercase tracking-wider">
              <BatteryCharging className="w-3.5 h-3.5 text-emerald-400" />
              <span>{battery}% Charged</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-white/5 bg-bg-secondary/40 text-[10px] font-bold text-white uppercase tracking-wider">
              <Wifi className="w-3.5 h-3.5 text-accent-ai" />
              <span>Secure 5G Connected</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-white/5 bg-bg-secondary/40 text-[10px] font-bold text-white uppercase tracking-wider">
              <Lock className="w-3.5 h-3.5 text-accent-primary animate-pulse" />
              <span>AI Shield Lock Active</span>
            </div>
          </div>
        </section>

        {/* Middle Core Grid */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Left Block: Interactive Safety Map Viewport */}
          <div className="lg:col-span-8 flex flex-col space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Radio className="w-4 h-4 text-danger-custom animate-pulse" />
                <h3 className="text-sm font-bold text-white uppercase tracking-widest">
                  Live Safety Radar Map
                </h3>
              </div>
              <button 
                onClick={() => setCurrentView('routes')}
                className="text-[10px] font-bold text-accent-ai hover:underline flex items-center gap-1"
              >
                <span>Compare Safe Routes</span>
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>

            <SafetyMap />
          </div>

          {/* Right Block: AI Safety Gauge & Recommendations */}
          <div className="lg:col-span-4 flex flex-col space-y-6">
            
            {/* Circular Safety Score Widget */}
            <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md flex flex-col items-center text-center relative">
              <h3 className="text-[10px] font-bold text-text-secondary uppercase tracking-widest mb-4">
                AI Safety Assessment Score
              </h3>

              <div className="relative w-36 h-36 flex items-center justify-center">
                {/* SVG Circle Gauge */}
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="72"
                    cy="72"
                    r={radius}
                    className="stroke-white/5"
                    strokeWidth="8"
                    fill="transparent"
                  />
                  <motion.circle
                    cx="72"
                    cy="72"
                    r={radius}
                    stroke={safetyInfo.stroke}
                    strokeWidth="8"
                    fill="transparent"
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 1.2, ease: 'easeOut' }}
                    strokeLinecap="round"
                  />
                </svg>
                
                {/* Center score labels */}
                <div className="absolute inset-0 flex flex-col items-center justify-center space-y-0.5">
                  <span className="text-3xl font-extrabold text-white tracking-tight">
                    {safetyScore}
                  </span>
                  <span className={`text-[10px] font-extrabold uppercase tracking-wider ${safetyInfo.color}`}>
                    {safetyInfo.label}
                  </span>
                </div>
              </div>

              {/* Confidence interval */}
              <div className="mt-4 text-[10px] text-text-secondary">
                Prediction Confidence: <span className="text-white font-bold">98.4% (Ultra-high)</span>
              </div>

              {/* Quick test sliders to toggle Safety State */}
              <div className="mt-4 flex gap-1 bg-bg-primary/50 p-1 rounded-xl border border-white/5">
                {[94, 75, 45, 25].map((s) => (
                  <button 
                    key={s} 
                    onClick={() => setSafetyScore(s)}
                    className={`px-2 py-1 text-[8px] font-extrabold rounded-lg ${
                      safetyScore === s ? 'bg-accent-primary text-white' : 'text-text-secondary hover:text-white'
                    }`}
                  >
                    Simulate {s}%
                  </button>
                ))}
              </div>
            </div>

            {/* AI Advisor Recommendations */}
            <div className={`p-6 rounded-3xl border ${safetyInfo.bg} flex flex-col space-y-3`}>
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-accent-ai animate-pulse" />
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                  AI Guardian Insights
                </h4>
              </div>
              <p className="text-[11px] text-text-secondary leading-relaxed font-light">
                {safetyScore >= 90 
                  ? 'Your current environment is highly secure with active police patrol visibility, street illumination at 96%, and strong crowdsourced check-ins.'
                  : safetyScore >= 70
                  ? 'Standard path home contains moderately low lighting levels. Avoid side avenues. Consider using Cafe Bloom (Safe Haven) as a waiting checkpoint.'
                  : safetyScore >= 40
                  ? 'High loitering incident occurred 200m away. Lighting on standard route is down. AI suggests activating Guardian Mode immediately.'
                  : 'Critical threat parameters logged nearby. Siren and immediate emergency contact linkage recommended. Tap SOS below or whisper safe word.'
                }
              </p>
              <div className="flex flex-col gap-1.5 pt-2 text-[10px] text-white">
                <div className="flex items-center justify-between border-b border-white/5 pb-1">
                  <span className="text-text-secondary">Street Illuminance</span>
                  <span className="font-bold">{safetyScore >= 90 ? '96%' : safetyScore >= 70 ? '64%' : '23%'}</span>
                </div>
                <div className="flex items-center justify-between border-b border-white/5 pb-1">
                  <span className="text-text-secondary">Crowd density</span>
                  <span className="font-bold">{safetyScore >= 90 ? 'Moderate (Safe)' : safetyScore >= 70 ? 'Sparse' : 'Critical Low'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-secondary">Emergency Services Coverage</span>
                  <span className="font-bold">{safetyScore >= 90 ? 'High' : safetyScore >= 70 ? 'Normal' : 'Delayed'}</span>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* Bottom Section: Quick Actions Hub */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white uppercase tracking-widest">
              Quick Safety Operations
            </h3>
            <span className="text-[10px] text-accent-ai font-semibold uppercase">5 Channels Deployed</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {/* Start Safe Journey */}
            <div 
              onClick={() => setCurrentView('routes')}
              className="p-5 rounded-2xl glass-panel border-white/5 hover:border-accent-primary/20 hover:bg-bg-secondary/40 transition-all duration-300 group cursor-pointer flex flex-col justify-between min-h-[130px]"
            >
              <div className="p-3 w-fit rounded-xl bg-accent-primary/10 border border-accent-primary/20 text-accent-primary group-hover:scale-110 transition-transform">
                <Compass className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white uppercase tracking-tight">Start Journey</h4>
                <p className="text-[9px] text-text-secondary mt-1">Smart secure navigation routing</p>
              </div>
            </div>

            {/* Guardian Mode */}
            <div 
              onClick={() => {
                setGuardianModeActive(!guardianModeActive);
                setCurrentView('guardian-mode');
              }}
              className={`p-5 rounded-2xl border transition-all duration-300 group cursor-pointer flex flex-col justify-between min-h-[130px] ${
                guardianModeActive 
                  ? 'bg-accent-ai/10 border-accent-ai/30 text-accent-ai shadow-[0_0_15px_rgba(0,229,255,0.15)]'
                  : 'glass-panel border-white/5 hover:border-accent-ai/20 hover:bg-bg-secondary/40'
              }`}
            >
              <div className={`p-3 w-fit rounded-xl border group-hover:scale-110 transition-transform ${
                guardianModeActive 
                  ? 'bg-accent-ai/20 border-accent-ai/40 text-accent-ai' 
                  : 'bg-white/5 border-white/10 text-text-secondary'
              }`}>
                <Radio className={`w-5 h-5 ${guardianModeActive ? 'animate-pulse' : ''}`} />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white uppercase tracking-tight">Guardian Mode</h4>
                <p className="text-[9px] text-text-secondary mt-1">
                  {guardianModeActive ? 'Monitoring telemetry LIVE' : 'Continuous recording checks'}
                </p>
              </div>
            </div>

            {/* Emergency SOS */}
            <div 
              onClick={() => {
                setEmergencyActive(true);
                setCurrentView('emergency');
              }}
              className="p-5 rounded-2xl glass-panel border-white/5 hover:border-danger-custom/30 hover:bg-bg-secondary/40 transition-all duration-300 group cursor-pointer flex flex-col justify-between min-h-[130px]"
            >
              <div className="p-3 w-fit rounded-xl bg-danger-custom/10 border border-danger-custom/20 text-danger-custom group-hover:scale-110 transition-transform">
                <ShieldAlert className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white uppercase tracking-tight">Emergency SOS</h4>
                <p className="text-[9px] text-text-secondary mt-1">Instant police & guardian dispatch</p>
              </div>
            </div>

            {/* Community Intelligence */}
            <div 
              onClick={() => setCurrentView('community')}
              className="p-5 rounded-2xl glass-panel border-white/5 hover:border-accent-primary/20 hover:bg-bg-secondary/40 transition-all duration-300 group cursor-pointer flex flex-col justify-between min-h-[130px]"
            >
              <div className="p-3 w-fit rounded-xl bg-white/5 border border-white/10 text-text-secondary group-hover:scale-110 transition-transform">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white uppercase tracking-tight">Community</h4>
                <p className="text-[9px] text-text-secondary mt-1">Local hazard feeds and check-ins</p>
              </div>
            </div>

            {/* AI Assistant */}
            <div 
              onClick={() => setCurrentView('ai-guardian')}
              className="p-5 rounded-2xl glass-panel border-white/5 hover:border-accent-ai/20 hover:bg-bg-secondary/40 transition-all duration-300 group cursor-pointer flex flex-col justify-between min-h-[130px]"
            >
              <div className="p-3 w-fit rounded-xl bg-accent-ai/10 border border-accent-ai/20 text-accent-ai group-hover:scale-110 transition-transform">
                <MessageSquareCode className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white uppercase tracking-tight">AI Guardian Chat</h4>
                <p className="text-[9px] text-text-secondary mt-1">Chat & ask safety configurations</p>
              </div>
            </div>
          </div>
        </section>

        {/* Priority Notification Banner */}
        {notifications.filter(n => !n.read).length > 0 && (
          <section 
            onClick={() => setCurrentView('profile')} 
            className="p-4 rounded-2xl bg-accent-primary/10 border border-accent-primary/25 flex items-center justify-between cursor-pointer hover:bg-accent-primary/15 transition-all"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-accent-primary/20 text-accent-primary animate-pulse">
                <TrendingUp className="w-4 h-4" />
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-bold text-white">Active Guardian Recommendation</span>
                <span className="text-[10px] text-text-secondary">{notifications.filter(n => !n.read)[0].content}</span>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-text-secondary" />
          </section>
        )}

      </main>

      {/* Floating Action Button */}
      <div className="fixed bottom-6 right-6 z-40 group">
        <div className="absolute inset-0 rounded-full bg-accent-primary blur group-hover:blur-md opacity-40 group-hover:opacity-75 transition-all" />
        <button
          onClick={() => {
            setEmergencyActive(true);
            setCurrentView('emergency');
          }}
          className="relative w-14 h-14 rounded-full bg-danger-custom text-white flex items-center justify-center shadow-lg hover:bg-red-600 transition-colors cursor-pointer"
        >
          <ShieldAlert className="w-6 h-6 animate-pulse" />
        </button>
      </div>

    </div>
  );
}
