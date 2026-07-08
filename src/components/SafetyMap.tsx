'use client';

import React, { useState, useEffect } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  MapPin, 
  Navigation,
  Eye, 
  Layers,
  AlertTriangle,
  Locate,
  Info,
  ShieldAlert
} from 'lucide-react';

export default function SafetyMap() {
  const { activeJourney, incidents, guardianModeActive } = useSafeStore();
  
  // Toggles for layers
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showSafeZones, setShowSafeZones] = useState(true);
  const [showHospitals, setShowHospitals] = useState(true);
  const [showPolice, setShowPolice] = useState(true);
  const [showIncidents, setShowIncidents] = useState(true);

  // Selected map pin detail
  const [selectedPin, setSelectedPin] = useState<{
    id: string;
    type: 'police' | 'hospital' | 'safehaven' | 'incident';
    name: string;
    description: string;
    x: number;
    y: number;
  } | null>(null);

  // Simulated coordinate data for pins
  const pins = [
    { id: 'p1', type: 'police' as const, name: 'North Precinct Police Station', description: '24/7 Active patrol base. Response time < 3 mins.', x: 120, y: 150 },
    { id: 'p2', type: 'police' as const, name: 'Metro Police Kiosk', description: 'Active duty officers stationed here. Safe checkpoint.', x: 450, y: 320 },
    
    { id: 'h1', type: 'hospital' as const, name: 'St. Jude Emergency Center', description: '24-hour emergency room & security desk.', x: 300, y: 80 },
    { id: 'h2', type: 'hospital' as const, name: 'Mercy Medical Kiosk', description: 'Pharmacy and localized emergency clinic.', x: 80, y: 380 },
    
    { id: 's1', type: 'safehaven' as const, name: 'Cafe Bloom (Safe Business)', description: 'WoSafe Certified Haven. Staff trained in distress support. Free chargers.', x: 220, y: 250 },
    { id: 's2', type: 'safehaven' as const, name: 'Beacon Library (Safe Zone)', description: 'Public safety desk, emergency call box active.', x: 380, y: 160 },
  ];

  // Danger heat circles
  const heatCircles = [
    { x: 340, y: 280, r: 45, severity: 'high', label: 'Dark Alley Alleyway (Low Streetlights)' },
    { x: 180, y: 110, r: 35, severity: 'medium', label: 'Recent loitering reports' },
  ];

  // Map click triggers details close
  const handleMapClick = (e: React.MouseEvent<SVGSVGElement>) => {
    // If clicking empty map area, clear selection
    if ((e.target as SVGElement).tagName === 'svg' || (e.target as SVGElement).tagName === 'rect') {
      setSelectedPin(null);
    }
  };

  return (
    <div className="relative w-full h-[380px] sm:h-[450px] rounded-3xl overflow-hidden border border-white/5 bg-[#030611] shadow-2xl">
      
      {/* HUD Layers Toggles */}
      <div className="absolute top-4 left-4 z-10 flex flex-wrap gap-1.5 max-w-[85%]">
        <button
          onClick={() => setShowHeatmap(!showHeatmap)}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[9px] font-bold tracking-wider uppercase border transition-all ${
            showHeatmap 
              ? 'bg-danger-custom/15 border-danger-custom/30 text-danger-custom shadow-[0_0_10px_rgba(255,77,109,0.15)]' 
              : 'bg-bg-secondary/40 border-white/5 text-text-secondary hover:text-white'
          }`}
        >
          <AlertTriangle className="w-3 h-3" />
          <span>Heatmap</span>
        </button>
        <button
          onClick={() => setShowSafeZones(!showSafeZones)}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[9px] font-bold tracking-wider uppercase border transition-all ${
            showSafeZones 
              ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.15)]' 
              : 'bg-bg-secondary/40 border-white/5 text-text-secondary hover:text-white'
          }`}
        >
          <Shield className="w-3 h-3" />
          <span>Safe Havens</span>
        </button>
        <button
          onClick={() => setShowPolice(!showPolice)}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[9px] font-bold tracking-wider uppercase border transition-all ${
            showPolice 
              ? 'bg-accent-primary/15 border-accent-primary/30 text-accent-primary shadow-[0_0_10px_rgba(108,99,255,0.15)]' 
              : 'bg-bg-secondary/40 border-white/5 text-text-secondary hover:text-white'
          }`}
        >
          <Locate className="w-3 h-3" />
          <span>Police</span>
        </button>
        <button
          onClick={() => setShowHospitals(!showHospitals)}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[9px] font-bold tracking-wider uppercase border transition-all ${
            showHospitals 
              ? 'bg-blue-500/15 border-blue-500/30 text-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.15)]' 
              : 'bg-bg-secondary/40 border-white/5 text-text-secondary hover:text-white'
          }`}
        >
          <Layers className="w-3 h-3" />
          <span>Hospitals</span>
        </button>
      </div>

      {/* Map simulation container */}
      <svg 
        viewBox="0 0 600 450" 
        className="w-full h-full cursor-grab active:cursor-grabbing select-none"
        onClick={handleMapClick}
      >
        {/* Dark Grid Background */}
        <defs>
          <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
            <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(255, 255, 255, 0.02)" strokeWidth="1" />
          </pattern>
          <radialGradient id="mapGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#080e22" stopOpacity="1" />
            <stop offset="100%" stopColor="#030611" stopOpacity="1" />
          </radialGradient>
        </defs>

        <rect width="600" height="450" fill="url(#mapGlow)" />
        <rect width="600" height="450" fill="url(#grid)" />

        {/* Cyberpunk Streets/Paths */}
        <g stroke="rgba(255,255,255,0.04)" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" fill="none">
          <path d="M 50,50 L 550,50" />
          <path d="M 50,150 L 550,150" />
          <path d="M 50,250 L 550,250" />
          <path d="M 50,350 L 550,350" />
          <path d="M 100,50 L 100,400" />
          <path d="M 250,50 L 250,400" />
          <path d="M 400,50 L 400,400" />
          <path d="M 520,50 L 520,400" />
          <path d="M 50,50 L 400,400" /> {/* Diagonal avenue */}
        </g>
        <g stroke="rgba(255,255,255,0.015)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none">
          <path d="M 50,50 L 550,50" />
          <path d="M 50,150 L 550,150" />
          <path d="M 50,250 L 550,250" />
          <path d="M 50,350 L 550,350" />
          <path d="M 100,50 L 100,400" />
          <path d="M 250,50 L 250,400" />
          <path d="M 400,50 L 400,400" />
          <path d="M 520,50 L 520,400" />
          <path d="M 50,50 L 400,400" />
        </g>

        {/* Danger Heatmaps Overlay */}
        {showHeatmap && heatCircles.map((circle, i) => (
          <g key={i}>
            <circle 
              cx={circle.x} 
              cy={circle.y} 
              r={circle.r} 
              fill="rgba(255, 77, 109, 0.15)" 
              stroke="rgba(255, 77, 109, 0.3)" 
              strokeWidth="1.5"
              className="animate-pulse"
            />
            <circle 
              cx={circle.x} 
              cy={circle.y} 
              r={circle.r - 15} 
              fill="rgba(255, 77, 109, 0.1)" 
            />
          </g>
        ))}

        {/* Draw Live Active Journey Path */}
        {activeJourney && (
          <>
            {/* Shortest Route (Passes through danger) */}
            {activeJourney.selectedRoute === 'shortest' && (
              <g>
                <path 
                  d="M 100,250 L 250,250 L 340,280 L 400,350" 
                  stroke="rgba(255, 255, 255, 0.2)" 
                  strokeWidth="4" 
                  strokeLinecap="round" 
                  fill="none" 
                />
                <path 
                  d="M 100,250 L 250,250 L 340,280 L 400,350" 
                  stroke="#FF4D6D" 
                  strokeWidth="3.5" 
                  strokeDasharray="8 6" 
                  strokeLinecap="round" 
                  fill="none"
                  className="animate-[dash_1.5s_linear_infinite]"
                />
              </g>
            )}

            {/* Safest Route (Diverts around danger, links with Cafe Bloom and Police Kiosk) */}
            {activeJourney.selectedRoute === 'safest' && (
              <g>
                <path 
                  d="M 100,250 L 220,250 L 250,150 L 380,160 L 400,350" 
                  stroke="rgba(0, 229, 255, 0.2)" 
                  strokeWidth="4.5" 
                  strokeLinecap="round" 
                  fill="none" 
                />
                <path 
                  d="M 100,250 L 220,250 L 250,150 L 380,160 L 400,350" 
                  stroke="#00E5FF" 
                  strokeWidth="3.5" 
                  strokeDasharray="10 6" 
                  strokeLinecap="round" 
                  fill="none"
                />
                {/* Flowing navigation arrows */}
                <circle cx="220" cy="250" r="5" fill="#00E5FF" className="animate-ping" />
                <circle cx="380" cy="160" r="5" fill="#00E5FF" className="animate-ping" />
              </g>
            )}

            {/* Fastest Route */}
            {activeJourney.selectedRoute === 'fastest' && (
              <g>
                <path 
                  d="M 100,250 L 250,250 L 400,250 L 400,350" 
                  stroke="rgba(108, 99, 255, 0.25)" 
                  strokeWidth="4" 
                  strokeLinecap="round" 
                  fill="none" 
                />
                <path 
                  d="M 100,250 L 250,250 L 400,250 L 400,350" 
                  stroke="#6C63FF" 
                  strokeWidth="3" 
                  strokeDasharray="6 6" 
                  strokeLinecap="round" 
                  fill="none"
                />
              </g>
            )}

            {/* Destination Marker */}
            <g transform="translate(400, 350)">
              <circle r="18" fill="rgba(108, 99, 255, 0.15)" stroke="rgba(108, 99, 255, 0.4)" strokeWidth="1" />
              <circle r="8" fill="#6C63FF" />
              <circle r="4" fill="#FFFFFF" />
            </g>
          </>
        )}

        {/* User Current Position (Sarah Chen) */}
        <g transform="translate(100, 250)">
          {/* Pulsing radar */}
          <circle r="22" fill="rgba(0, 229, 255, 0.12)" className="animate-ping" />
          <circle r="12" fill="rgba(0, 229, 255, 0.2)" stroke="#00E5FF" strokeWidth="1.5" />
          <circle r="5" fill="#00E5FF" className="shadow-[0_0_8px_#00E5FF]" />
        </g>

        {/* Static Map Pin Markers */}
        {showPolice && pins.filter(p => p.type === 'police').map((pin) => (
          <g 
            key={pin.id} 
            transform={`translate(${pin.x}, ${pin.y})`}
            className="cursor-pointer group"
            onClick={() => setSelectedPin(pin)}
          >
            <circle r="12" fill="rgba(108, 99, 255, 0.1)" stroke="rgba(108, 99, 255, 0.4)" strokeWidth="1" />
            <circle r="5" fill="#6C63FF" className="group-hover:scale-125 transition-transform" />
          </g>
        ))}

        {showHospitals && pins.filter(p => p.type === 'hospital').map((pin) => (
          <g 
            key={pin.id} 
            transform={`translate(${pin.x}, ${pin.y})`}
            className="cursor-pointer group"
            onClick={() => setSelectedPin(pin)}
          >
            <circle r="12" fill="rgba(59, 130, 246, 0.1)" stroke="rgba(59, 130, 246, 0.4)" strokeWidth="1" />
            <rect x="-4" y="-4" width="8" height="8" rx="1.5" fill="#3B82F6" className="group-hover:scale-125 transition-transform" />
          </g>
        ))}

        {showSafeZones && pins.filter(p => p.type === 'safehaven').map((pin) => (
          <g 
            key={pin.id} 
            transform={`translate(${pin.x}, ${pin.y})`}
            className="cursor-pointer group"
            onClick={() => setSelectedPin(pin)}
          >
            <circle r="14" fill="rgba(16, 185, 129, 0.12)" stroke="rgba(16, 185, 129, 0.4)" strokeWidth="1" />
            <polygon points="0,-6 6,0 0,6 -6,0" fill="#10B981" className="group-hover:scale-125 transition-transform" />
          </g>
        ))}

        {/* Live Crowdsourced Incidents */}
        {showIncidents && incidents.map((inc, i) => {
          // Map index to coordinates
          const coords = [
            { x: 340, y: 280 }, // Broken streetlights (aligns with dark alley)
            { x: 450, y: 150 }, // Suspicious loitering
            { x: 220, y: 250 }  // Cafe Bloom
          ];
          const coord = coords[i % coords.length];
          const color = inc.severity === 'critical' || inc.severity === 'high' ? '#FF4D6D' : '#F8C630';
          return (
            <g 
              key={inc.id} 
              transform={`translate(${coord.x + 10}, ${coord.y - 10})`}
              className="cursor-pointer group"
              onClick={() => setSelectedPin({
                id: inc.id,
                type: 'incident',
                name: inc.title,
                description: `${inc.category} reported ${inc.time}. ${inc.description}`,
                x: coord.x + 10,
                y: coord.y - 10
              })}
            >
              <circle r="10" fill="none" stroke={color} strokeWidth="1.5" className="animate-ping" />
              <polygon points="0,-5 5,4 -5,4" fill={color} />
            </g>
          );
        })}

        {/* Guardian Mode Radar Sweeper */}
        {guardianModeActive && (
          <g transform="translate(100, 250)">
            <circle r="120" fill="none" stroke="rgba(0, 229, 255, 0.08)" strokeWidth="1" />
            <line x1="0" y1="0" x2="84" y2="84" stroke="rgba(0, 229, 255, 0.3)" strokeWidth="1.5" className="origin-center animate-[spin_5s_linear_infinite]" />
            <circle r="120" fill="rgba(0, 229, 255, 0.02)" />
          </g>
        )}
      </svg>

      {/* Selected Node Details Popup Modal */}
      <AnimatePresence>
        {selectedPin && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-4 left-4 right-4 z-10 p-4 rounded-xl glass-panel bg-bg-secondary/90 border-white/10 backdrop-blur-md flex items-start gap-3 shadow-xl"
          >
            <div className={`p-2 rounded-lg ${
              selectedPin.type === 'police' ? 'bg-accent-primary/10 text-accent-primary' :
              selectedPin.type === 'hospital' ? 'bg-blue-500/10 text-blue-400' :
              selectedPin.type === 'safehaven' ? 'bg-emerald-500/10 text-emerald-400' :
              'bg-danger-custom/10 text-danger-custom'
            }`}>
              {selectedPin.type === 'police' && <Shield className="w-5 h-5" />}
              {selectedPin.type === 'hospital' && <Info className="w-5 h-5" />}
              {selectedPin.type === 'safehaven' && <ShieldAlert className="w-5 h-5" />}
              {selectedPin.type === 'incident' && <AlertTriangle className="w-5 h-5" />}
            </div>

            <div className="flex-1 space-y-1">
              <h4 className="text-xs font-bold text-white uppercase tracking-tight">{selectedPin.name}</h4>
              <p className="text-[10px] text-text-secondary leading-relaxed font-light">{selectedPin.description}</p>
            </div>

            <button 
              onClick={() => setSelectedPin(null)}
              className="text-[10px] text-text-secondary hover:text-white uppercase font-bold tracking-wider px-2 py-1 rounded bg-white/5"
            >
              Close
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Active Compass HUD */}
      <div className="absolute bottom-4 right-4 z-10 flex flex-col gap-2">
        <div className="p-3 rounded-xl glass-panel border-white/5 bg-bg-secondary/60 text-white flex items-center justify-center shadow-lg">
          <Navigation className="w-4 h-4 text-accent-ai animate-pulse" />
        </div>
      </div>
    </div>
  );
}
