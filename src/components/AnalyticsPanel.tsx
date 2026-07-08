'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  CartesianGrid
} from 'recharts';
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  ShieldAlert, 
  CheckCircle,
  HelpCircle
} from 'lucide-react';

export default function AnalyticsPanel() {
  
  // Simulated analytics data
  const tripData = [
    { name: 'Jan', trips: 42, score: 91 },
    { name: 'Feb', trips: 48, score: 92 },
    { name: 'Mar', trips: 55, score: 94 },
    { name: 'Apr', trips: 60, score: 93 },
    { name: 'May', trips: 65, score: 95 },
    { name: 'Jun', trips: 72, score: 98 },
  ];

  const riskTrendData = [
    { day: 'Mon', reports: 12, threatPct: 24 },
    { day: 'Tue', reports: 15, threatPct: 28 },
    { day: 'Wed', reports: 8, threatPct: 15 },
    { day: 'Thu', reports: 22, threatPct: 40 },
    { day: 'Fri', reports: 30, threatPct: 55 },
    { day: 'Sat', reports: 28, threatPct: 48 },
    { day: 'Sun', reports: 14, threatPct: 30 }
  ];

  const safetyScoreGrowth = [
    { week: 'Wk 1', score: 85 },
    { week: 'Wk 2', score: 88 },
    { week: 'Wk 3', score: 91 },
    { week: 'Wk 4', score: 94 }
  ];

  const customTooltipStyle = {
    backgroundColor: '#0E1324',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: '12px',
    fontSize: '11px',
    color: '#FFF'
  };

  return (
    <div className="relative min-h-screen bg-bg-primary pt-24 pb-16 px-4 max-w-6xl mx-auto space-y-6">
      
      {/* Background glow top right */}
      <div className="absolute top-10 right-10 w-[300px] h-[300px] rounded-full bg-accent-ai/5 blur-[90px] pointer-events-none" />

      {/* Header bar */}
      <div className="flex items-center gap-2.5 border-b border-white/5 pb-4">
        <div className="p-2 rounded-xl bg-accent-primary/10 border border-accent-primary/20 text-accent-primary shadow-[0_0_15px_rgba(108,99,255,0.15)] animate-pulse">
          <BarChart3 className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Safety Analytics Workspace</h2>
          <p className="text-[10px] text-text-secondary">AI-modeled risk trend indices and spatial safety calculations</p>
        </div>
      </div>

      {/* Upper overview metrics row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        
        {/* Metric 1 */}
        <div className="p-5 rounded-2xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md">
          <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest block">Safe Trips Logged</span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-2xl font-black text-white">342</span>
            <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-0.5"><TrendingUp className="w-3 h-3" />+12%</span>
          </div>
          <span className="text-[9px] text-text-secondary/70 mt-1 block">Past 90 days audit window</span>
        </div>

        {/* Metric 2 */}
        <div className="p-5 rounded-2xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md">
          <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest block">Avg Safety Index</span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-2xl font-black text-accent-ai">94.2%</span>
            <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-0.5"><TrendingUp className="w-3 h-3" />+4%</span>
          </div>
          <span className="text-[9px] text-text-secondary/70 mt-1 block">Optimal safety performance</span>
        </div>

        {/* Metric 3 */}
        <div className="p-5 rounded-2xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md">
          <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest block">Danger Sectors Evaded</span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-2xl font-black text-white">28</span>
            <span className="text-[10px] text-accent-primary font-bold">Safe Re-Route</span>
          </div>
          <span className="text-[9px] text-text-secondary/70 mt-1 block">Automatic alert bypass</span>
        </div>

        {/* Metric 4 */}
        <div className="p-5 rounded-2xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md">
          <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest block">Community Votes</span>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-2xl font-black text-white">184</span>
            <span className="text-[10px] text-emerald-400 font-bold">Verified Helper</span>
          </div>
          <span className="text-[9px] text-text-secondary/70 mt-1 block">Risk network participation</span>
        </div>

      </div>

      {/* Middle row: Chart widgets */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart 1: Trips and Baseline Score */}
        <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-widest">
            Monthly Safe Commutes & Index
          </h3>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tripData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                <XAxis dataKey="name" stroke="#A6B0CF" fontSize={10} />
                <YAxis stroke="#A6B0CF" fontSize={10} />
                <Tooltip contentStyle={customTooltipStyle} />
                <Bar dataKey="trips" fill="#6C63FF" radius={[4, 4, 0, 0]} barSize={25} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Threat Pct & Local Reports */}
        <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-widest">
            Weekly Threat Level Trends (Temporal)
          </h3>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={riskTrendData}>
                <defs>
                  <linearGradient id="threatGlow" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FF4D6D" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#FF4D6D" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                <XAxis dataKey="day" stroke="#A6B0CF" fontSize={10} />
                <YAxis stroke="#A6B0CF" fontSize={10} />
                <Tooltip contentStyle={customTooltipStyle} />
                <Area type="monotone" dataKey="threatPct" stroke="#FF4D6D" strokeWidth={2} fillOpacity={1} fill="url(#threatGlow)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Weekly Safety Score Growth */}
        <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4 lg:col-span-2">
          <h3 className="text-xs font-bold text-white uppercase tracking-widest">
            Guardian Safety Score Improvement
          </h3>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={safetyScoreGrowth}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" />
                <XAxis dataKey="week" stroke="#A6B0CF" fontSize={10} />
                <YAxis domain={[70, 100]} stroke="#A6B0CF" fontSize={10} />
                <Tooltip contentStyle={customTooltipStyle} />
                <Line type="monotone" dataKey="score" stroke="#00E5FF" strokeWidth={3} activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

    </div>
  );
}
