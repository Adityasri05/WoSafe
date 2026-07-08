'use client';

import React, { useEffect, useState } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion } from 'framer-motion';
import { 
  Shield, 
  Map, 
  Zap, 
  Eye, 
  Users, 
  VolumeX, 
  ChevronRight, 
  Activity,
  Play,
  CheckCircle2,
  Lock,
  Globe2
} from 'lucide-react';

export default function LandingPage() {
  const { setCurrentView } = useSafeStore();
  const [stats, setStats] = useState({
    protected: 2150000,
    predictions: 18450000,
    trips: 45100000,
    responseTime: 4.2
  });

  // Animate stats counting upwards slightly
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        protected: prev.protected + Math.floor(Math.random() * 3) + 1,
        predictions: prev.predictions + Math.floor(Math.random() * 5) + 2,
        trips: prev.trips + Math.floor(Math.random() * 8) + 3,
        responseTime: parseFloat((4.2 - (Math.random() * 0.1)).toFixed(2))
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: <Shield className="w-6 h-6 text-accent-ai animate-pulse" />,
      title: "AI Guardian",
      tagline: "Predictive Risk Intelligence",
      description: "Continuous real-time threat calculations analysing environment, history, light levels, and crowd densities to predict danger before it materializes."
    },
    {
      icon: <Eye className="w-6 h-6 text-accent-primary" />,
      title: "Guardian Mode",
      tagline: "Automatic Emergency Protection",
      description: "An active companion that monitors walking speed, detects impacts or deviations, and activates audio/video recording if unsafe behavior is sensed."
    },
    {
      icon: <Map className="w-6 h-6 text-emerald-400" />,
      title: "Smart Safe Navigation",
      tagline: "AI Powered Safer Routes",
      description: "Avoids isolated alleys and low-light areas. Calculates routes based on live police availability, community safety check-ins, and street visibility."
    },
    {
      icon: <Users className="w-6 h-6 text-blue-400" />,
      title: "Community Intelligence",
      tagline: "Real-time Safety Network",
      description: "Crowdsourced logs, emergency volunteer notifications, and verification of business safe zones to build a shared shield of protection."
    },
    {
      icon: <Activity className="w-6 h-6 text-amber-400" />,
      title: "Incident AI",
      tagline: "Automatic Evidence Hub",
      description: "Automatically indexes video, audio recordings, and telemetry into verified, encrypted packages with AI summaries ready for dispatch to authorities."
    },
    {
      icon: <VolumeX className="w-6 h-6 text-danger-custom" />,
      title: "Silent Emergency",
      tagline: "Voice-Activated SOS",
      description: "Trigger emergencies hands-free. Whisper your custom Safe Word or scream for help to bypass screen lock and instantly dispatch responders."
    }
  ];

  return (
    <div className="relative min-h-screen bg-bg-primary overflow-hidden pt-24 pb-16">
      
      {/* Background Aurora Lighting Effect */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-accent-primary/10 blur-[120px] animate-aurora-1 pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[55%] h-[55%] rounded-full bg-accent-ai/10 blur-[130px] animate-aurora-2 pointer-events-none" />

      {/* Hero Section */}
      <section className="relative px-6 mx-auto max-w-7xl pt-10 lg:pt-16 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        
        {/* Left Side: Headline and CTAs */}
        <div className="lg:col-span-7 flex flex-col items-start text-left space-y-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-accent-ai/20 bg-accent-ai/5 backdrop-blur-sm text-accent-ai text-xs font-semibold"
          >
            <Shield className="w-3.5 h-3.5" />
            <span>AI GUARDIAN PLATFORM</span>
            <div className="w-1.5 h-1.5 rounded-full bg-accent-ai animate-ping" />
          </motion.div>

          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1] max-w-2xl"
          >
            The Future of <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-primary via-accent-ai to-white text-glow-primary">
              Women&apos;s Safety
            </span> Starts Here.
          </motion.h1>

          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-text-secondary text-base sm:text-lg max-w-xl leading-relaxed font-light"
          >
            WoSafe continuously predicts potential risks before they escalate using Artificial Intelligence, Community Intelligence, Smart Navigation, and Intelligent Emergency Response.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.3 }}
            className="flex flex-wrap gap-4 w-full sm:w-auto"
          >
            <button 
              onClick={() => setCurrentView('auth')}
              className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl text-sm font-bold bg-accent-primary text-white hover:bg-[#594fff] transition-all duration-300 shadow-[0_0_20px_rgba(108,99,255,0.35)] hover:shadow-[0_0_30px_rgba(108,99,255,0.6)] cursor-pointer group"
            >
              <span>Start Safe Journey</span>
              <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button 
              onClick={() => setCurrentView('dashboard')}
              className="flex items-center justify-center gap-2 px-6 py-4 rounded-xl text-sm font-semibold border border-white/10 text-white hover:bg-white/5 hover:border-white/20 transition-all duration-300 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Watch Live Demo</span>
            </button>
          </motion.div>

          {/* Core assurances */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="flex items-center gap-6 pt-4 text-xs text-text-secondary border-t border-white/5 w-full max-w-md"
          >
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-accent-ai" />
              <span>PWA Ready</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>Zero-knowledge Encryption</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Globe2 className="w-3.5 h-3.5 text-accent-primary" />
              <span>24/7 Dispatch Net</span>
            </div>
          </motion.div>
        </div>

        {/* Right Side: Futuristic Guardian Orb */}
        <div className="lg:col-span-5 flex justify-center items-center relative min-h-[300px] sm:min-h-[450px]">
          {/* Background spinning radar rings */}
          <div className="absolute w-[280px] h-[280px] sm:w-[380px] sm:h-[380px] rounded-full border border-white/5 animate-[spin_40s_linear_infinite]" />
          <div className="absolute w-[200px] h-[200px] sm:w-[280px] sm:h-[280px] rounded-full border border-dashed border-accent-primary/20 animate-[spin_25s_linear_infinite_reverse]" />
          <div className="absolute w-[120px] h-[120px] sm:w-[180px] sm:h-[180px] rounded-full border border-accent-ai/15 animate-ping opacity-35" />

          {/* Central AI Orb */}
          <motion.div 
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 1 }}
            className="relative w-44 h-44 sm:w-60 sm:h-60 rounded-full flex items-center justify-center"
          >
            {/* Pulsing neon gradients */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-accent-primary to-accent-ai opacity-20 blur-xl animate-pulse" />
            <div className="absolute w-full h-full rounded-full border border-white/10 bg-bg-secondary/40 backdrop-blur-xl flex flex-col items-center justify-center p-4 text-center overflow-hidden">
              {/* Dynamic waveform drawing */}
              <div className="absolute bottom-6 flex items-end gap-1 h-8 opacity-45">
                {[1, 2, 3, 4, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1].map((h, i) => (
                  <motion.div 
                    key={i}
                    animate={{ height: [4, h * 6, 4] }}
                    transition={{ duration: 1.2 + (i * 0.05), repeat: Infinity, ease: 'easeInOut' }}
                    className="w-1 bg-gradient-to-t from-accent-primary to-accent-ai rounded-full"
                  />
                ))}
              </div>

              {/* Glowing core icon */}
              <div className="relative z-10 p-4 rounded-full bg-accent-primary/10 border border-accent-primary/20 shadow-[0_0_30px_rgba(108,99,255,0.3)] animate-bounce">
                <Shield className="w-12 h-12 text-accent-primary" />
              </div>
              <p className="mt-4 text-xs font-bold tracking-widest text-accent-ai uppercase">
                AI PROTECTOR ACTIVE
              </p>
              <p className="text-[10px] text-text-secondary mt-1">
                99.8% Threat Predictability
              </p>
            </div>

            {/* Small Floating Nodes */}
            <div className="absolute top-2 left-6 w-3 h-3 rounded-full bg-accent-ai shadow-[0_0_8px_#00E5FF] animate-bounce" />
            <div className="absolute bottom-10 left-[-15px] w-2 h-2 rounded-full bg-accent-primary shadow-[0_0_8px_#6C63FF] animate-pulse" />
            <div className="absolute right-0 top-1/3 w-3 h-3 rounded-full bg-emerald-400 shadow-[0_0_8px_#10B981] animate-[pulse_1.5s_infinite]" />
          </motion.div>
        </div>
      </section>

      {/* Statistics Counters Section */}
      <section className="relative px-6 mx-auto max-w-7xl mt-24">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 p-8 glass-panel rounded-3xl border-white/5 bg-bg-secondary/20 backdrop-blur-md">
          <div className="flex flex-col items-center justify-center text-center p-4 border-r border-white/5 last:border-0">
            <span className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {(stats.protected / 1000000).toFixed(2)}M+
            </span>
            <span className="text-xs text-text-secondary mt-1">Women Protected</span>
          </div>
          <div className="flex flex-col items-center justify-center text-center p-4 border-r border-white/5 last:border-0">
            <span className="text-2xl sm:text-3xl font-extrabold text-accent-ai tracking-tight">
              {(stats.predictions / 1000000).toFixed(2)}M+
            </span>
            <span className="text-xs text-text-secondary mt-1">AI Predictions</span>
          </div>
          <div className="flex flex-col items-center justify-center text-center p-4 border-r border-white/5 last:border-0">
            <span className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {(stats.trips / 1000000).toFixed(1)}M+
            </span>
            <span className="text-xs text-text-secondary mt-1">Safe Journeys Completed</span>
          </div>
          <div className="flex flex-col items-center justify-center text-center p-4 last:border-0">
            <span className="text-2xl sm:text-3xl font-extrabold text-danger-custom tracking-tight flex items-center justify-center gap-1">
              &lt; {stats.responseTime}s
            </span>
            <span className="text-xs text-text-secondary mt-1">Response Time</span>
          </div>
        </div>
      </section>

      {/* Features Grid Section */}
      <section className="relative px-6 mx-auto max-w-7xl mt-32 space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-xs font-bold text-accent-primary tracking-widest uppercase">
            INTELLIGENT PROTOCOLS
          </h2>
          <p className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            Designed to Protect. Engineered to Predict.
          </p>
          <p className="text-text-secondary text-sm max-w-lg mx-auto font-light">
            Every feature is calibrated to give you confidence and keep you connected to assistance without creating anxiety.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, index) => (
            <div 
              key={index}
              className="flex flex-col p-6 rounded-2xl glass-panel border-white/5 hover:border-accent-primary/20 hover:bg-bg-secondary/40 transition-all duration-300 group cursor-pointer"
            >
              <div className="p-3 w-fit rounded-xl bg-white/5 border border-white/10 group-hover:border-accent-primary/30 group-hover:bg-accent-primary/5 transition-all duration-300">
                {feat.icon}
              </div>
              <h3 className="text-lg font-bold text-white mt-4 group-hover:text-accent-primary transition-colors">
                {feat.title}
              </h3>
              <p className="text-xs text-accent-ai font-semibold mt-0.5">
                {feat.tagline}
              </p>
              <p className="text-text-secondary text-xs leading-relaxed font-light mt-3">
                {feat.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Visual Quote Overlay */}
      <section className="relative px-6 mx-auto max-w-5xl mt-32 text-center">
        <div className="p-12 rounded-3xl bg-gradient-to-tr from-accent-primary/10 via-bg-secondary/50 to-accent-ai/10 border border-white/5 relative">
          <div className="absolute inset-0 bg-bg-secondary/20 blur-md rounded-3xl" />
          <blockquote className="relative z-10 text-xl sm:text-2xl font-light italic text-white/90">
            &ldquo;I used to feel anxious walking back from the hospital after night shifts. With WoSafe&apos;s smart routes and AI Guardian active on my headphones, I feel like I have an invisible security detail with me, every step.&rdquo;
          </blockquote>
          <cite className="relative z-10 block text-xs font-semibold text-accent-ai uppercase tracking-wider mt-6">
            — Dr. Linnea Vance, Trauma Surgeon
          </cite>
        </div>
      </section>

      {/* Bottom Call to Action */}
      <section className="relative px-6 mx-auto max-w-7xl mt-32 text-center flex flex-col items-center">
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
          Ready to Step Into the Future of Personal Safety?
        </h2>
        <p className="text-text-secondary text-sm max-w-md mt-3 font-light">
          Install WoSafe today. Seamlessly connect emergency responders, verify safety zones, and secure your travels.
        </p>
        <button 
          onClick={() => setCurrentView('auth')}
          className="mt-8 px-10 py-4 rounded-xl text-sm font-bold bg-white text-bg-primary hover:bg-zinc-200 transition-all duration-300 cursor-pointer shadow-lg hover:shadow-white/10"
        >
          Activate Your Account
        </button>
      </section>

    </div>
  );
}
