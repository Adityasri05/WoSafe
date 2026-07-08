'use client';

import React, { useState } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileWarning, 
  MapPin, 
  UploadCloud, 
  Mic, 
  Sparkles, 
  ArrowRight, 
  CheckCircle2,
  Trash2,
  Lock,
  EyeOff
} from 'lucide-react';

export default function IncidentForm() {
  const { addIncident, setCurrentView } = useSafeStore();

  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Safety Alert');
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState<'low' | 'medium' | 'high' | 'critical'>('medium');
  const [anonymous, setAnonymous] = useState(true);

  // Media / Audio uploads
  const [files, setFiles] = useState<{ name: string; size: string }[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState(false);

  // AI Summary generator state
  const [aiSummary, setAiSummary] = useState('');
  const [aiLoading, setAiLoading] = useState(false);

  const triggerUpload = () => {
    // Simulate uploading a file
    setFiles([{ name: 'IMG_8432.JPG', size: '2.4 MB' }]);
  };

  const clearFiles = () => {
    setFiles([]);
  };

  const handleVoiceRecord = () => {
    if (!isRecording) {
      setIsRecording(true);
      setTimeout(() => {
        setIsRecording(false);
        setRecordedAudio(true);
      }, 3000);
    }
  };

  const generateAISummary = () => {
    if (!description.trim()) return;
    setAiLoading(true);
    setTimeout(() => {
      setAiLoading(false);
      setAiSummary(`AI SUMMARY: Verified incident report at ${location || 'current node'}. Category: ${category}. Telemetry matches ambient lighting deficit. Recommendation: Alert localized patrol units and suggest alternate route mappings for pedestrians.`);
    }, 1500);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description) return;

    addIncident({
      title,
      category,
      location: location || '5th Ave & 23rd St (GPS Checkin)',
      description: aiSummary ? `${description}\n\n[${aiSummary}]` : description,
      severity,
      anonymous,
      userReported: true
    });

    setCurrentView('community');
  };

  return (
    <div className="relative min-h-screen bg-bg-primary pt-24 pb-28 md:pb-16 px-4 max-w-4xl mx-auto space-y-6">
      
      {/* Background glow top right */}
      <div className="absolute top-10 right-10 w-[300px] h-[300px] rounded-full bg-accent-ai/5 blur-[90px] pointer-events-none" />

      {/* Header info */}
      <div className="flex items-center gap-2.5 border-b border-white/5 pb-4">
        <div className="p-2 rounded-xl bg-danger-custom/10 border border-danger-custom/25 text-danger-custom animate-pulse">
          <FileWarning className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">File Incident Testimony</h2>
          <p className="text-[10px] text-text-secondary">Incident feeds are automatically verified by regional dispatch networks</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Form Details (col-span-8) */}
        <div className="lg:col-span-8 space-y-4 p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md">
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">Report Title</label>
              <input 
                type="text" 
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Broken Streetlights"
                className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none"
                required
              />
            </div>
            
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">Category</label>
              <select 
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none"
              >
                <option value="Safety Alert">Safety Alert (Harassment, loitering)</option>
                <option value="Infrastructure">Infrastructure (Light failure, broken locks)</option>
                <option value="Safe Business">Safe Haven / Safe Business</option>
                <option value="Hazard">Physical Hazard / Construction block</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">Incident Location</label>
              <div className="relative">
                <MapPin className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                <input 
                  type="text" 
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. 5th Ave & 23rd St"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">Severity Index</label>
              <select 
                value={severity}
                onChange={(e) => setSeverity(e.target.value as any)}
                className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none"
              >
                <option value="low">Low Severity</option>
                <option value="medium">Medium Severity</option>
                <option value="high">High Severity</option>
                <option value="critical">Critical Emergency Dispatch</option>
              </select>
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">Testimony Description</label>
            <textarea 
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the environment, activity, and any active threats..."
              rows={4}
              className="w-full px-4 py-3 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none resize-none"
              required
            />
          </div>

          {/* AI Generator Button Panel */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
            <button
              type="button"
              onClick={generateAISummary}
              disabled={!description.trim() || aiLoading}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-accent-ai/20 bg-accent-ai/5 text-accent-ai text-xs font-bold hover:bg-accent-ai/10 transition-colors disabled:opacity-50 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 animate-pulse" />
              <span>{aiLoading ? 'Analyzing text...' : 'Generate AI Safety Summary'}</span>
            </button>

            {/* Anonymous Toggle */}
            <div className="flex items-center gap-2">
              <input 
                type="checkbox" 
                id="anon"
                checked={anonymous}
                onChange={(e) => setAnonymous(e.target.checked)}
                className="w-4 h-4 bg-bg-primary border-white/10 rounded focus:ring-accent-primary text-accent-primary"
              />
              <label htmlFor="anon" className="text-xs font-bold text-text-secondary uppercase tracking-wider flex items-center gap-1.5 cursor-pointer">
                <EyeOff className="w-3.5 h-3.5" />
                <span>Mask Identity (Anonymous)</span>
              </label>
            </div>
          </div>

          {/* Render AI summary result */}
          <AnimatePresence>
            {aiSummary && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0 }}
                className="p-4 rounded-xl border border-accent-ai/20 bg-accent-ai/5 text-accent-ai text-[10px] leading-relaxed font-semibold whitespace-pre-wrap"
              >
                {aiSummary}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Column: Upload Files & Audio (col-span-4) */}
        <div className="lg:col-span-4 space-y-4">
          
          {/* File Upload Zone */}
          <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 border-b border-white/5 pb-3">
              <UploadCloud className="w-4 h-4 text-accent-primary" />
              <h3 className="text-xs font-bold text-white uppercase tracking-widest">
                Attach Media Evidence
              </h3>
            </div>

            {files.length === 0 ? (
              <div 
                onClick={triggerUpload}
                className="border border-dashed border-white/10 rounded-2xl p-6 text-center hover:border-accent-primary/50 transition-colors cursor-pointer flex flex-col items-center justify-center space-y-2 bg-bg-primary/20"
              >
                <UploadCloud className="w-8 h-8 text-text-secondary opacity-60" />
                <span className="text-[10px] font-bold text-white uppercase tracking-wider">Upload Video / Photo</span>
                <span className="text-[9px] text-text-secondary">Drag & drop or browse files</span>
              </div>
            ) : (
              <div className="flex justify-between items-center p-3 rounded-xl bg-white/5 border border-white/5 text-xs text-white">
                <div className="flex flex-col truncate pr-2">
                  <span className="font-bold truncate">{files[0].name}</span>
                  <span className="text-[9px] text-text-secondary">{files[0].size}</span>
                </div>
                <button type="button" onClick={clearFiles} className="text-text-secondary hover:text-danger-custom p-1">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Voice testimony recorder */}
          <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 border-b border-white/5 pb-3">
              <Mic className="w-4 h-4 text-accent-ai" />
              <h3 className="text-xs font-bold text-white uppercase tracking-widest">
                Voice Testimony
              </h3>
            </div>

            {!recordedAudio ? (
              <button
                type="button"
                onClick={handleVoiceRecord}
                className={`w-full flex items-center justify-center gap-2 py-4 rounded-2xl border transition-all ${
                  isRecording 
                    ? 'bg-danger-custom/10 border-danger-custom/30 text-danger-custom animate-pulse shadow-[0_0_15px_rgba(255,77,109,0.1)]' 
                    : 'bg-bg-primary/20 border-white/10 text-text-secondary hover:text-white hover:border-white/20'
                }`}
              >
                <Mic className="w-4 h-4 text-accent-ai animate-bounce" />
                <span className="text-xs font-bold uppercase tracking-wider">
                  {isRecording ? 'Recording (Scream/distress scan active)' : 'Record Audio Testimony'}
                </span>
              </button>
            ) : (
              <div className="flex justify-between items-center p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-white">
                <div className="flex items-center gap-2 text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span className="font-bold">Audio Clip Recorded</span>
                </div>
                <button type="button" onClick={() => setRecordedAudio(false)} className="text-text-secondary hover:text-danger-custom p-1">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Submit panel */}
          <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md text-center space-y-3">
            <div className="flex items-center gap-1.5 justify-center text-[10px] text-text-secondary">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>Federal Security Encryption</span>
            </div>
            
            <button
              type="submit"
              className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-accent-primary hover:bg-[#594fff] text-white text-xs font-bold shadow-[0_0_15px_rgba(108,99,255,0.2)] transition-colors cursor-pointer"
            >
              <span>Compile & Dispatch Report</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

        </div>

      </form>

    </div>
  );
}
