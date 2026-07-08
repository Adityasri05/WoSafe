'use client';

import React, { useState } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion } from 'framer-motion';
import { 
  Settings, 
  Lock, 
  Bell, 
  MapPin, 
  Volume2, 
  Key, 
  ShieldAlert, 
  EyeOff, 
  HelpCircle,
  CheckCircle2
} from 'lucide-react';

export default function SettingsPanel() {
  const { 
    permissions, 
    setPermission, 
    safeWord, 
    setSafeWord 
  } = useSafeStore();

  const [safeWordVal, setSafeWordVal] = useState(safeWord);
  const [incognito, setIncognito] = useState(false);
  const [continuousShare, setContinuousShare] = useState(true);
  const [biometrics, setBiometrics] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Notifications toggles
  const [notifPriority, setNotifPriority] = useState(true);
  const [notifGuardians, setNotifGuardians] = useState(true);
  const [notifCommunity, setNotifCommunity] = useState(true);

  const handleSaveSettings = () => {
    setSafeWord(safeWordVal);
    setSaveSuccess(true);
    setTimeout(() => {
      setSaveSuccess(false);
    }, 2000);
  };

  const handleTogglePermission = (key: keyof typeof permissions) => {
    setPermission(key, !permissions[key]);
  };

  return (
    <div className="relative min-h-screen bg-bg-primary pt-24 pb-28 md:pb-16 px-4 max-w-4xl mx-auto space-y-6">
      
      {/* Background glow top right */}
      <div className="absolute top-10 right-10 w-[300px] h-[300px] rounded-full bg-accent-ai/5 blur-[90px] pointer-events-none" />

      {/* Header bar */}
      <div className="flex items-center gap-2.5 border-b border-white/5 pb-4">
        <div className="p-2 rounded-xl bg-accent-primary/10 border border-accent-primary/20 text-accent-primary shadow-[0_0_15px_rgba(108,99,255,0.15)]">
          <Settings className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">System Settings</h2>
          <p className="text-[10px] text-text-secondary">Calibrate threat sensors, dispatch targets, and confidential locks</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        
        {/* Left Column: Security Settings (col-span-8) */}
        <div className="md:col-span-8 space-y-6">
          
          {/* Safe Word & Biometrics */}
          <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 border-b border-white/5 pb-3">
              <Key className="w-4 h-4 text-accent-ai" />
              <h3 className="text-xs font-bold text-white uppercase tracking-widest">
                Acoustic safe word & locks
              </h3>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">
                  Acoustic SOS Word
                </label>
                <span className="text-[9px] text-text-secondary italic">Continuous Background Mic Sync</span>
              </div>
              <input 
                type="text" 
                value={safeWordVal}
                onChange={(e) => setSafeWordVal(e.target.value)}
                placeholder="e.g. Phoenix"
                className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-bold focus:border-accent-primary focus:outline-none"
              />
              <p className="text-[9px] text-text-secondary leading-normal">
                Scream or whisper this word home when walking. It triggers local sirens, shares coordinates, and connects emergency links.
              </p>
            </div>

            <div className="flex items-center justify-between border-t border-white/5 pt-4">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-white">Biometric Quick-Disable SOS</span>
                <span className="text-[10px] text-text-secondary">Require FaceID / TouchID to abort alarms</span>
              </div>
              <input 
                type="checkbox"
                checked={biometrics}
                onChange={(e) => setBiometrics(e.target.checked)}
                className="w-4 h-4 rounded text-accent-primary focus:ring-accent-primary bg-bg-primary"
              />
            </div>
          </div>

          {/* Privacy & Location Sharing */}
          <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 border-b border-white/5 pb-3">
              <EyeOff className="w-4 h-4 text-accent-primary" />
              <h3 className="text-xs font-bold text-white uppercase tracking-widest">
                Privacy Configurations
              </h3>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-white">Mask Map Presence (Incognito Mode)</span>
                <span className="text-[10px] text-text-secondary">Hide your nodes from nearby community volunteers</span>
              </div>
              <input 
                type="checkbox"
                checked={incognito}
                onChange={(e) => setIncognito(e.target.checked)}
                className="w-4 h-4 rounded text-accent-primary focus:ring-accent-primary bg-bg-primary"
              />
            </div>

            <div className="flex items-center justify-between border-t border-white/5 pt-4">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-white">Continuous Coordinate Syncing</span>
                <span className="text-[10px] text-text-secondary">Share live paths with primary emergency guardians 24/7</span>
              </div>
              <input 
                type="checkbox"
                checked={continuousShare}
                onChange={(e) => setContinuousShare(e.target.checked)}
                className="w-4 h-4 rounded text-accent-primary focus:ring-accent-primary bg-bg-primary"
              />
            </div>
          </div>

          {/* Notifications toggles */}
          <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 border-b border-white/5 pb-3">
              <Bell className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-widest">
                Notification parameters
              </h3>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-white">Priority Dispatch Alerts</span>
                <span className="text-[10px] text-text-secondary">Urgent warnings within 500m of your GPS</span>
              </div>
              <input 
                type="checkbox"
                checked={notifPriority}
                onChange={(e) => setNotifPriority(e.target.checked)}
                className="w-4 h-4 rounded text-accent-primary focus:ring-accent-primary bg-bg-primary"
              />
            </div>

            <div className="flex items-center justify-between border-t border-white/5 pt-4">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-white">Guardian Link Confirmations</span>
                <span className="text-[10px] text-text-secondary">Notify when David Chen or Emma Watson verify links</span>
              </div>
              <input 
                type="checkbox"
                checked={notifGuardians}
                onChange={(e) => setNotifGuardians(e.target.checked)}
                className="w-4 h-4 rounded text-accent-primary focus:ring-accent-primary bg-bg-primary"
              />
            </div>

            <div className="flex items-center justify-between border-t border-white/5 pt-4">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-white">Community Updates Feed</span>
                <span className="text-[10px] text-text-secondary">General neighborhood hazard checks, broken streetlight reports</span>
              </div>
              <input 
                type="checkbox"
                checked={notifCommunity}
                onChange={(e) => setNotifCommunity(e.target.checked)}
                className="w-4 h-4 rounded text-accent-primary focus:ring-accent-primary bg-bg-primary"
              />
            </div>
          </div>

        </div>

        {/* Right Column: Hardware permissions (col-span-4) */}
        <div className="md:col-span-4 space-y-6">
          
          {/* Permissions statuses panel */}
          <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 border-b border-white/5 pb-3">
              <ShieldAlert className="w-4 h-4 text-accent-primary animate-pulse" />
              <h3 className="text-xs font-bold text-white uppercase tracking-widest">
                Sensor Access
              </h3>
            </div>

            <div className="space-y-3">
              {Object.keys(permissions).map((key) => {
                const isApproved = permissions[key as keyof typeof permissions];
                return (
                  <div key={key} className="flex justify-between items-center text-xs">
                    <span className="capitalize text-text-secondary font-bold">{key}</span>
                    
                    <button
                      type="button"
                      onClick={() => handleTogglePermission(key as any)}
                      className={`px-2.5 py-1 rounded-lg text-[9px] font-bold uppercase transition-all ${
                        isApproved 
                          ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' 
                          : 'bg-white/5 border border-white/10 text-white hover:bg-white/10'
                      }`}
                    >
                      {isApproved ? 'Approved' : 'Disabled'}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Save Action Banner */}
          <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md text-center space-y-3">
            <div className="flex items-center justify-center gap-1.5 text-[10px] text-text-secondary">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>Settings encrypted in local storage</span>
            </div>

            <button
              onClick={handleSaveSettings}
              className="w-full flex items-center justify-center gap-1.5 py-3 rounded-xl bg-accent-primary hover:bg-[#594fff] text-white text-xs font-bold shadow-[0_0_12px_rgba(108,99,255,0.2)] transition-colors cursor-pointer"
            >
              <span>Save Configurations</span>
            </button>

            {/* Success state */}
            {saveSuccess && (
              <div className="flex items-center justify-center gap-1.5 text-[10px] text-emerald-400 font-bold uppercase tracking-wider animate-pulse pt-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Configurations Saved</span>
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
}
