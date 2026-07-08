'use client';

import React, { useState, useEffect } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldAlert, 
  PhoneCall, 
  MapPin, 
  HelpCircle, 
  Volume2, 
  Clock, 
  X, 
  CheckCircle2,
  Users
} from 'lucide-react';

export default function EmergencySOS() {
  const { setEmergencyActive, setCurrentView, user } = useSafeStore();
  const [countdown, setCountdown] = useState(5);
  const [dispatchStarted, setDispatchStarted] = useState(false);
  const [activeTab, setActiveTab] = useState<'survival' | 'volunteers'>('survival');

  // Countdown timer before dispatch
  useEffect(() => {
    if (countdown > 0 && !dispatchStarted) {
      const timer = setTimeout(() => {
        setCountdown(prev => prev - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (countdown === 0 && !dispatchStarted) {
      setDispatchStarted(true);
    }
  }, [countdown, dispatchStarted]);

  const handleCancel = () => {
    setEmergencyActive(false);
    setCurrentView('dashboard');
  };

  const guides = [
    { title: "If Followed", desc: "Change walking speed immediately. cross streets. Navigate to Cafe Bloom (Safe Haven 200m ahead) or any lighted storefront. Keep AI Guardian chat voice link open." },
    { title: "If Trapped", desc: "Seek physical backings (walls) to avoid flank attacks. Shout your Safe Word loudly. Hold your phone high; flashlights will begin pulsing distress codes automatically." },
    { title: "Self Defense", desc: "Target soft vitals (eyes, nose, throat, groin). Use keychains or hard objects. Push away and scream, prioritizing running to a safe zone." }
  ];

  return (
    <div className="fixed inset-0 z-50 bg-[#04060f] text-white flex flex-col justify-between p-6 overflow-hidden">
      
      {/* Dynamic Blood-Red Glow overlay */}
      <div className="absolute inset-0 bg-red-950/20 pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] sm:w-[500px] sm:h-[500px] rounded-full bg-danger-custom/10 blur-[100px] pointer-events-none animate-pulse" />

      {/* Header bar */}
      <div className="relative z-10 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <ShieldAlert className="w-5 h-5 text-danger-custom animate-bounce" />
          <h2 className="text-xs font-black text-danger-custom uppercase tracking-widest">
            Emergency Dispatch HUD
          </h2>
        </div>

        <button
          onClick={handleCancel}
          className="p-2.5 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer"
        >
          <X className="w-4 h-4 text-text-secondary hover:text-white" />
        </button>
      </div>

      {/* Core Interactive SOS Button Zone */}
      <div className="relative z-10 flex flex-col items-center justify-center text-center space-y-4 sm:space-y-6 flex-1 overflow-y-auto py-2 w-full max-h-[65vh] md:max-h-none scrollbar-thin">
        
        {/* Countdown / Dispatch Status */}
        <AnimatePresence mode="wait">
          {!dispatchStarted ? (
            <motion.div 
              key="countdown"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-1 text-center"
            >
              <span className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">Dispatching alerts in</span>
              <h1 className="text-6xl font-black text-white font-mono animate-pulse">{countdown}</h1>
              <button 
                onClick={handleCancel} 
                className="text-[10px] text-danger-custom font-bold hover:underline uppercase tracking-wider block mt-2 mx-auto"
              >
                Abort Dispatch
              </button>
            </motion.div>
          ) : (
            <motion.div 
              key="dispatched"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-2 text-center"
            >
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-[10px] font-bold tracking-wider uppercase animate-pulse">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>ALERTS BROADCASTED</span>
              </div>
              <p className="text-[11px] text-text-secondary max-w-xs mx-auto leading-relaxed">
                Emergency coordinate packet dispatched to local Police, verified nearby volunteers, and trusted guardians.
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Large Pulse SOS button */}
        <div className="relative w-44 h-44 sm:w-56 sm:h-56 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full bg-danger-custom/10 animate-sos-pulse" />
          <button 
            onClick={() => setDispatchStarted(true)}
            className="relative w-36 h-36 sm:w-44 sm:h-44 rounded-full bg-danger-custom flex flex-col items-center justify-center text-center p-4 border border-red-400/25 shadow-[0_0_40px_rgba(255,77,109,0.5)] cursor-pointer hover:bg-red-600 transition-colors"
          >
            <ShieldAlert className="w-10 h-10 sm:w-14 sm:h-14 text-white animate-pulse" />
            <span className="text-sm font-black text-white uppercase tracking-wider mt-2 sm:mt-3">SOS ACTIVE</span>
            <span className="text-[8px] text-red-200 uppercase tracking-widest mt-0.5 sm:mt-1">Tap to Broadcast</span>
          </button>
        </div>

        {/* Info panel */}
        <div className="text-[10px] text-text-secondary flex items-center gap-1">
          <Volume2 className="w-3.5 h-3.5 text-danger-custom" />
          <span>Continuous microphone audio feeds streaming live</span>
        </div>

        {/* Dual tab layout for survival guides vs volunteers */}
        <div className="w-full max-w-md bg-bg-secondary/40 rounded-2xl border border-white/5 overflow-hidden">
          <div className="flex border-b border-white/5">
            <button
              onClick={() => setActiveTab('survival')}
              className={`flex-1 py-2 text-[10px] font-bold tracking-wider uppercase transition-colors ${
                activeTab === 'survival' ? 'bg-white/5 text-white border-b border-accent-primary' : 'text-text-secondary hover:text-white'
              }`}
            >
              Emergency Survival Guide
            </button>
            <button
              onClick={() => setActiveTab('volunteers')}
              className={`flex-1 py-2 text-[10px] font-bold tracking-wider uppercase transition-colors ${
                activeTab === 'volunteers' ? 'bg-white/5 text-white border-b border-accent-primary' : 'text-text-secondary hover:text-white'
              }`}
            >
              Nearby Responders (3)
            </button>
          </div>

          <div className="p-4 min-h-[120px] max-h-[160px] overflow-y-auto">
            {activeTab === 'survival' ? (
              <div className="space-y-3 text-left">
                {guides.map((g, i) => (
                  <div key={i} className="space-y-1">
                    <span className="text-[10px] font-bold text-accent-ai uppercase tracking-wide">{g.title}</span>
                    <p className="text-[10px] text-text-secondary leading-relaxed font-light">{g.desc}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2 text-left">
                <div className="flex justify-between items-center px-3 py-2 rounded-xl bg-white/5 border border-white/5 text-[10px]">
                  <div className="flex items-center gap-2">
                    <Users className="w-3.5 h-3.5 text-accent-ai animate-pulse" />
                    <span className="font-bold">Officer Marcus (Kiosk B)</span>
                  </div>
                  <span className="text-text-secondary font-mono">150m away &bull; ETA 1.5m</span>
                </div>
                <div className="flex justify-between items-center px-3 py-2 rounded-xl bg-white/5 border border-white/5 text-[10px]">
                  <div className="flex items-center gap-2">
                    <Users className="w-3.5 h-3.5 text-accent-primary" />
                    <span className="font-bold">Guardian Volunteer Emma</span>
                  </div>
                  <span className="text-text-secondary font-mono">220m away &bull; ETA 2.5m</span>
                </div>
                <div className="flex justify-between items-center px-3 py-2 rounded-xl bg-white/5 border border-white/5 text-[10px]">
                  <div className="flex items-center gap-2">
                    <Users className="w-3.5 h-3.5 text-accent-primary" />
                    <span className="font-bold">Guardian Volunteer Chen</span>
                  </div>
                  <span className="text-text-secondary font-mono">400m away &bull; ETA 4m</span>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Bottom Dispatch Dials */}
      <div className="relative z-10 grid grid-cols-3 gap-3">
        <a 
          href="tel:911"
          className="flex flex-col items-center justify-center p-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-center gap-1.5"
        >
          <PhoneCall className="w-4 h-4 text-accent-primary" />
          <span className="text-[9px] font-bold text-white uppercase tracking-wider">Call Police</span>
        </a>
        
        <a 
          href="tel:911"
          className="flex flex-col items-center justify-center p-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-center gap-1.5"
        >
          <PhoneCall className="w-4 h-4 text-accent-ai" />
          <span className="text-[9px] font-bold text-white uppercase tracking-wider">Call Medic</span>
        </a>
        
        <a 
          href={`tel:${user.emergencyContacts[0]?.phone}`}
          className="flex flex-col items-center justify-center p-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-center gap-1.5"
        >
          <PhoneCall className="w-4 h-4 text-danger-custom" />
          <span className="text-[9px] font-bold text-white uppercase tracking-wider">Call Guardian</span>
        </a>
      </div>

    </div>
  );
}
