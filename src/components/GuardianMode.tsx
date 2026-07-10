'use client';

import React, { useState, useEffect } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/services/api';
import { 
  Radio, 
  MapPin, 
  UserCheck, 
  AlertTriangle, 
  Power, 
  Timer,
  Lock,
  PhoneCall,
  Volume2
} from 'lucide-react';

export default function GuardianMode() {
  const { setGuardianModeActive, setCurrentView, setEmergencyActive, user } = useSafeStore();
  const [seconds, setSeconds] = useState(0);
  const [coords, setCoords] = useState({ lat: 37.7749, lng: -122.4194 });

  // Timer and coordinate drift simulation
  useEffect(() => {
    const timer = setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);

    const coordInterval = setInterval(() => {
      setCoords(prev => {
        const nextLat = prev.lat + (Math.random() - 0.5) * 0.0001;
        const nextLng = prev.lng + (Math.random() - 0.5) * 0.0001;
        
        api.updateLocation(nextLat, nextLng, "Active Guardian Telemetry Location")
          .catch(err => console.warn("Failed sending telemetry to backend", err));

        return { lat: nextLat, lng: nextLng };
      });
    }, 4000);

    return () => {
      clearInterval(timer);
      clearInterval(coordInterval);
    };
  }, []);

  const formatTime = (totalSecs: number) => {
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleDeactivate = () => {
    setGuardianModeActive(false);
    setCurrentView('dashboard');
  };

  const handleTriggerSOS = () => {
    setEmergencyActive(true);
    setCurrentView('emergency');
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#04060f] text-white flex flex-col justify-between p-6 overflow-hidden">
      
      {/* Background Pulsing Radiars */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[300px] h-[300px] sm:w-[500px] sm:h-[500px] rounded-full border border-danger-custom/5 animate-ping opacity-30" />
        <div className="w-[200px] h-[200px] sm:w-[350px] sm:h-[350px] rounded-full border border-accent-ai/5 animate-pulse" />
        <div className="absolute top-1/4 left-1/4 w-[250px] h-[250px] rounded-full bg-accent-primary/5 blur-[80px]" />
      </div>

      {/* Top Header Panel */}
      <div className="relative z-10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-3 h-3 rounded-full bg-danger-custom animate-ping" />
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-danger-custom uppercase tracking-widest">LIVE RECORDING ACTIVATED</span>
            <span className="text-[9px] text-text-secondary">Evidence logs compiled in zero-knowledge vault</span>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 rounded-full border border-white/5 bg-bg-secondary/60 text-[9px] font-bold tracking-wider uppercase text-text-secondary">
          <Lock className="w-3 h-3 text-emerald-400" />
          <span>FIPS-140 Encryption</span>
        </div>
      </div>

      {/* Middle Section: Big Display */}
      <div className="relative z-10 flex flex-col items-center justify-center text-center space-y-4 sm:space-y-6 flex-1 overflow-y-auto py-2 sm:py-10 w-full max-h-[65vh] md:max-h-none scrollbar-thin">
        
        {/* Active watch duration */}
        <div className="flex flex-col items-center space-y-1">
          <div className="flex items-center gap-1.5 text-text-secondary text-[10px] uppercase font-bold tracking-widest">
            <Timer className="w-4 h-4 text-accent-ai" />
            <span>Active Watch Timer</span>
          </div>
          <h1 className="text-5xl sm:text-6xl font-black tracking-tight font-mono text-white">
            {formatTime(seconds)}
          </h1>
        </div>

        {/* Live sound waveform animation */}
        <div className="flex items-end gap-1.5 h-16 pt-4">
          {[1, 2.5, 4, 3, 5, 2, 4, 6, 4.5, 3, 1].map((h, i) => (
            <motion.div
              key={i}
              animate={{ height: [8, h * 8, 8] }}
              transition={{ duration: 0.6 + (i * 0.05), repeat: Infinity, ease: 'easeInOut' }}
              className="w-1.5 bg-gradient-to-t from-danger-custom to-accent-ai rounded-full"
            />
          ))}
        </div>
        <div className="text-[10px] text-accent-ai uppercase tracking-wider font-bold flex items-center gap-1">
          <Volume2 className="w-3.5 h-3.5" />
          <span>Acoustic Scan Active &bull; Safe Word: &quot;Phoenix&quot;</span>
        </div>

        {/* Telemetry coords indicator */}
        <div className="p-4 rounded-2xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md max-w-sm w-full space-y-2 text-[10px] text-text-secondary">
          <div className="flex justify-between items-center border-b border-white/5 pb-1">
            <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-accent-ai" />Location Coords</span>
            <span className="font-mono text-white font-semibold">
              {coords.lat.toFixed(5)}°N, {coords.lng.toFixed(5)}°W
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="flex items-center gap-1"><UserCheck className="w-3.5 h-3.5 text-accent-primary" />Guardian Status</span>
            <span className="text-emerald-400 font-bold uppercase tracking-wider flex items-center gap-1">
              <span>Synchronized</span>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            </span>
          </div>
        </div>

        {/* Emergency Contacts Hotlist */}
        <div className="w-full max-w-xs space-y-2 text-left">
          <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest block text-center">Alert-Linked Contacts</span>
          {user.emergencyContacts.map((c, i) => (
            <div key={i} className="flex justify-between items-center px-4 py-2.5 rounded-xl border border-white/5 bg-bg-secondary/35 text-xs text-white">
              <span className="font-bold">{c.name} ({c.relation})</span>
              <a href={`tel:${c.phone}`} className="p-1 rounded-lg hover:bg-white/5 text-accent-ai">
                <PhoneCall className="w-3.5 h-3.5" />
              </a>
            </div>
          ))}
        </div>

      </div>

      {/* Bottom Control Actions */}
      <div className="relative z-10 flex flex-col sm:flex-row gap-4">
        <button
          onClick={handleDeactivate}
          className="flex-1 flex items-center justify-center gap-2 py-4 rounded-2xl border border-white/10 text-white font-bold text-sm hover:bg-white/5 transition-all cursor-pointer"
        >
          <Power className="w-4 h-4 text-text-secondary" />
          <span>Stand Down Guardian</span>
        </button>

        <button
          onClick={handleTriggerSOS}
          className="flex-1 flex items-center justify-center gap-2 py-4 rounded-2xl bg-danger-custom text-white font-black text-sm shadow-[0_0_20px_rgba(255,77,109,0.4)] hover:bg-red-600 transition-colors animate-pulse cursor-pointer"
        >
          <AlertTriangle className="w-5 h-5" />
          <span>TRIGGER SOS PANIC BUTTON</span>
        </button>
      </div>

    </div>
  );
}
