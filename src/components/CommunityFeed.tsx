'use client';

import React, { useEffect } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion } from 'framer-motion';
import { api } from '@/services/api';
import { 
  Users, 
  MapPin, 
  ThumbsUp, 
  AlertTriangle, 
  ShieldAlert, 
  EyeOff, 
  MessageSquare,
  Clock,
  Sparkles,
  ArrowUp,
  Store,
  ChevronRight
} from 'lucide-react';

export default function CommunityFeed() {
  const { incidents, voteIncident, setCurrentView } = useSafeStore();

  // Fetch incidents on mount
  useEffect(() => {
    api.getIncidents()
      .then(res => {
        if (res && res.incidents) {
          console.log("Fetched incidents from backend:", res.incidents);
        }
      })
      .catch(err => console.warn("Failed to fetch incidents from backend", err));
  }, []);

  const handleVote = (id: string) => {
    voteIncident(id);
    api.voteIncident(id)
      .catch(err => console.warn("Failed voting on incident on backend", err));
  };

  const safeBusinesses = [
    { name: 'Cafe Bloom', address: '12 Maple St', services: '24/7 Waiting area, Phone charging, Taxi hotline link', type: 'Cafe' },
    { name: 'Walgreens Pharmacy', address: '45 Broad Ave', services: '24/7 Security guard present, Medical box', type: 'Pharmacy' },
    { name: 'Beacon Library Hub', address: '380 Broadway', services: 'Emergency call box, Trained support desk', type: 'Public Institution' }
  ];

  return (
    <div className="relative min-h-screen bg-bg-primary pt-24 pb-28 md:pb-16 px-4 max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      {/* Background glow top right */}
      <div className="absolute top-10 right-10 w-[300px] h-[300px] rounded-full bg-accent-primary/5 blur-[90px] pointer-events-none" />

      {/* Left Block: Active Alerts Feed (col-span-8) */}
      <div className="lg:col-span-8 space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-accent-ai animate-pulse" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Crowdsourced Intelligence Feed</h2>
          </div>
          
          <button
            onClick={() => setCurrentView('report')}
            className="px-4 py-2 rounded-xl bg-accent-primary hover:bg-[#594fff] text-white text-xs font-bold shadow-[0_0_12px_rgba(108,99,255,0.2)] transition-colors cursor-pointer"
          >
            File Safety Report
          </button>
        </div>

        {/* Incidents feed container */}
        <div className="space-y-4">
          {incidents.map((inc) => {
            const isCritical = inc.severity === 'critical' || inc.severity === 'high';
            return (
              <motion.div
                key={inc.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-5 rounded-2xl glass-panel border-white/5 bg-bg-secondary/40 hover:bg-bg-secondary/60 transition-all duration-300 relative flex flex-col md:flex-row gap-4 justify-between"
              >
                {/* Details left */}
                <div className="flex-1 space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase ${
                      isCritical 
                        ? 'bg-danger-custom/10 text-danger-custom border border-danger-custom/20' 
                        : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                    }`}>
                      {inc.category}
                    </span>

                    <span className="text-[10px] text-text-secondary flex items-center gap-1 font-mono">
                      <Clock className="w-3.5 h-3.5" />
                      {inc.time}
                    </span>

                    {inc.anonymous && (
                      <span className="text-[9px] text-text-secondary/70 flex items-center gap-1 border border-white/5 px-1.5 py-0.5 rounded bg-white/5">
                        <EyeOff className="w-3 h-3" />
                        <span>Anonymous Node</span>
                      </span>
                    )}
                  </div>

                  <div className="space-y-1">
                    <h3 className="text-sm font-bold text-white uppercase tracking-tight">{inc.title}</h3>
                    <p className="text-[10px] text-text-secondary flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-accent-ai" />
                      {inc.location}
                    </p>
                  </div>

                  <p className="text-[11px] text-text-secondary leading-relaxed font-light">
                    {inc.description}
                  </p>
                </div>

                {/* Operations right */}
                <div className="flex md:flex-col justify-between md:items-end gap-2 border-t md:border-t-0 md:border-l border-white/5 pt-3 md:pt-0 md:pl-4">
                  <div className="text-right">
                    <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest block">Severity Index</span>
                    <span className={`text-xs font-bold uppercase ${isCritical ? 'text-danger-custom' : 'text-amber-500'}`}>
                      {inc.severity}
                    </span>
                  </div>

                  <button
                    onClick={() => handleVote(inc.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/5 bg-white/5 text-text-secondary hover:text-white hover:bg-white/10 transition-colors"
                  >
                    <ArrowUp className="w-3.5 h-3.5 text-accent-ai" />
                    <span className="text-[10px] font-bold">{inc.votes} Votes</span>
                  </button>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Right Block: Safe Businesses & Verified Volunteers (col-span-4) */}
      <div className="lg:col-span-4 space-y-6">
        
        {/* Verified Businesses */}
        <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
          <div className="flex items-center gap-2 border-b border-white/5 pb-3">
            <Store className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-bold text-white uppercase tracking-widest">
              Safe Havens (Businesses)
            </h3>
          </div>

          <div className="space-y-4">
            {safeBusinesses.map((biz, i) => (
              <div key={i} className="space-y-1.5">
                <div className="flex justify-between items-start">
                  <h4 className="text-xs font-bold text-white uppercase tracking-tight">{biz.name}</h4>
                  <span className="text-[8px] font-bold text-emerald-400 border border-emerald-500/20 bg-emerald-500/5 px-1.5 rounded">
                    {biz.type}
                  </span>
                </div>
                <p className="text-[9px] text-text-secondary flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-accent-ai" />
                  {biz.address}
                </p>
                <p className="text-[10px] text-text-secondary leading-relaxed font-light bg-white/5 p-2 rounded-lg border border-white/5">
                  {biz.services}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Verified Volunteers Info */}
        <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-accent-primary animate-pulse" />
            <h3 className="text-xs font-bold text-white uppercase tracking-widest">
              Emergency Responders Net
            </h3>
          </div>
          
          <p className="text-[11px] text-text-secondary leading-relaxed font-light">
            There are <span className="text-white font-bold">14 Active Guardian Volunteers</span> checking in within a 500m radius of your current location. In case of SOS, they are notified instantly.
          </p>

          <div className="pt-2 flex items-center justify-between text-[10px] text-accent-ai font-semibold border-t border-white/5 cursor-pointer hover:underline">
            <span>Become a Verified Guardian</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </div>
        </div>

      </div>

    </div>
  );
}
