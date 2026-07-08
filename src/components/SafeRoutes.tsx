'use client';

import React, { useState } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion } from 'framer-motion';
import { 
  ShieldCheck, 
  Clock, 
  MapPin, 
  ShieldAlert, 
  ChevronRight, 
  Flame, 
  Moon, 
  Users, 
  Info,
  Check
} from 'lucide-react';

export default function SafeRoutes() {
  const { activeJourney, setActiveJourney, setSafetyScore, setCurrentView } = useSafeStore();
  const [destination, setDestination] = useState('Central Library Hub');
  const [selectedRoute, setSelectedRoute] = useState<'shortest' | 'fastest' | 'safest'>('safest');

  const routesList = [
    {
      type: 'safest' as const,
      name: 'WoSafe Neural Path',
      eta: '16 mins',
      distance: '1.2 miles',
      score: 98,
      details: {
        lighting: 'High (98% Coverage)',
        crowd: 'Active Streets (Cafe districts)',
        police: '3 Active Checkpoints',
        stops: 'Cafe Bloom, Beacon Library'
      },
      badge: 'RECOMMENDED',
      color: 'border-accent-ai bg-accent-ai/5 text-accent-ai',
      glow: 'shadow-[0_0_15px_rgba(0,229,255,0.1)]'
    },
    {
      type: 'fastest' as const,
      name: 'Transit Core Ave',
      eta: '12 mins',
      distance: '0.9 miles',
      score: 75,
      details: {
        lighting: 'Medium (68% Coverage)',
        crowd: 'Sparse (Transit terminals)',
        police: '1 Active Checkpoint',
        stops: 'Metro Kiosk C'
      },
      badge: 'BALANCED',
      color: 'border-accent-primary/40 bg-accent-primary/5 text-accent-primary',
      glow: 'shadow-[0_0_15px_rgba(108,99,255,0.05)]'
    },
    {
      type: 'shortest' as const,
      name: 'Backalley Cut-through',
      eta: '9 mins',
      distance: '0.6 miles',
      score: 45,
      details: {
        lighting: 'Critical Low (12% Coverage)',
        crowd: 'Deserted sectors',
        police: 'No active patrols',
        stops: 'None verified'
      },
      badge: 'HIGH RISK SECTOR',
      color: 'border-danger-custom/30 bg-danger-custom/5 text-danger-custom',
      glow: ''
    }
  ];

  const handleStartJourney = () => {
    const selected = routesList.find(r => r.type === selectedRoute);
    if (!selected) return;

    setActiveJourney({
      started: true,
      destination,
      selectedRoute,
      duration: selected.eta,
      eta: new Date(Date.now() + (selectedRoute === 'safest' ? 16 : selectedRoute === 'fastest' ? 12 : 9) * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      lighting: selected.details.lighting,
      crowd: selected.details.crowd,
      police: selected.details.police
    });

    // Update safety score dynamically based on route selection
    setSafetyScore(selected.score);
    
    // Redirect back to dashboard to see active route drawing
    setCurrentView('dashboard');
  };

  const handleCancelJourney = () => {
    setActiveJourney(null);
    setSafetyScore(94); // Reset to baseline
  };

  return (
    <div className="relative min-h-screen bg-bg-primary pt-24 pb-28 md:pb-16 px-4 max-w-5xl mx-auto space-y-6">
      
      {/* Background glow top left */}
      <div className="absolute top-10 left-10 w-[300px] h-[300px] rounded-full bg-accent-primary/5 blur-[90px] pointer-events-none" />

      {/* Top Search Parameter Bar */}
      <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
        <div className="flex items-center justify-between border-b border-white/5 pb-3">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Path-Finding Parameters</h2>
          <span className="text-[10px] text-accent-ai font-semibold">Continuous GPS Grid Sync</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">Current Origin</label>
            <input 
              type="text" 
              value="5th Avenue Tech Center (Current Location)" 
              disabled
              className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/30 border border-white/5 text-text-secondary text-xs font-semibold"
            />
          </div>
          <div className="space-y-1">
            <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">Secure Destination</label>
            <input 
              type="text" 
              value={destination} 
              onChange={(e) => setDestination(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none"
            />
          </div>
        </div>
      </div>

      {/* Compare routes section */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-white uppercase tracking-widest">Select Route Safety Configuration</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {routesList.map((route) => {
            const isSelected = selectedRoute === route.type;
            const isSafest = route.type === 'safest';
            
            return (
              <div
                key={route.type}
                onClick={() => setSelectedRoute(route.type)}
                className={`p-5 rounded-2xl border cursor-pointer transition-all duration-300 relative flex flex-col justify-between min-h-[220px] ${
                  isSelected 
                    ? `border-white/20 bg-bg-secondary/70 ${route.glow}` 
                    : 'border-white/5 bg-bg-secondary/20 hover:border-white/10 hover:bg-bg-secondary/40'
                }`}
              >
                {/* Header info */}
                <div className="space-y-2">
                  <div className="flex justify-between items-start">
                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded border uppercase ${
                      isSelected ? route.color : 'text-text-secondary border-white/5 bg-white/5'
                    }`}>
                      {route.badge}
                    </span>
                    
                    {isSelected && (
                      <div className="w-5 h-5 rounded-full bg-accent-ai text-bg-primary flex items-center justify-center">
                        <Check className="w-3.5 h-3.5" />
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col">
                    <h4 className="text-xs font-bold text-white uppercase tracking-tight">{route.name}</h4>
                    <div className="flex items-center gap-2 text-[10px] text-text-secondary mt-0.5">
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{route.eta}</span>
                      <span>·</span>
                      <span>{route.distance}</span>
                    </div>
                  </div>
                </div>

                {/* Score indicators */}
                <div className="mt-4 pt-4 border-t border-white/5 space-y-2 text-[10px] text-text-secondary">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1"><Moon className="w-3.5 h-3.5" />Streetlights</span>
                    <span className="text-white font-bold">{route.details.lighting}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" />Crowds</span>
                    <span className="text-white font-semibold">{route.details.crowd}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5" />Police nodes</span>
                    <span className="text-white font-semibold">{route.details.police}</span>
                  </div>
                </div>

                {/* Bottom Safety Score Gauge */}
                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between">
                  <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest">Safety Score</span>
                  <span className={`text-sm font-black ${
                    route.score >= 90 ? 'text-success-custom' : route.score >= 70 ? 'text-warning-custom' : 'text-danger-custom'
                  }`}>
                    {route.score}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Action button */}
      <div className="flex justify-end gap-3">
        {activeJourney && (
          <button
            onClick={handleCancelJourney}
            className="px-6 py-3 rounded-xl border border-danger-custom/30 text-danger-custom text-xs font-bold hover:bg-danger-custom/5 transition-colors cursor-pointer"
          >
            Terminate Current Journey
          </button>
        )}

        <button
          onClick={handleStartJourney}
          className="px-8 py-3.5 rounded-xl bg-accent-primary hover:bg-[#594fff] text-white text-xs font-bold shadow-[0_0_15px_rgba(108,99,255,0.25)] transition-all cursor-pointer"
        >
          {activeJourney ? 'Re-Route Safe Journey' : 'Lock Route & Launch Telemetry'}
        </button>
      </div>

    </div>
  );
}
