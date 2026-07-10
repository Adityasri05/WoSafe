'use client';

import React, { useState } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/services/api';
import { 
  Shield, 
  Mail, 
  Phone, 
  Smartphone,
  Eye, 
  EyeOff, 
  ArrowRight,
  Sparkles,
  Lock
} from 'lucide-react';

export default function AuthScreen() {
  const { setCurrentView } = useSafeStore();
  const [activeTab, setActiveTab] = useState<'phone' | 'email' | 'google'>('phone');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [otpCode, setOtpCode] = useState('');
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);

  const handlePhoneSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otpSent) {
      if (!phoneNumber) return;
      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        setOtpSent(true);
      }, 1200);
    } else {
      if (otpCode.length < 4) return;
      setLoading(true);
      try {
        await api.loginWithFirebase("mock-token");
        setLoading(false);
        setCurrentView('onboarding');
      } catch (err) {
        console.warn("Backend auth failed, proceeding in offline/mock mode", err);
        setLoading(false);
        setCurrentView('onboarding');
      }
    }
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    setLoading(true);
    try {
      await api.loginWithFirebase("mock-token");
      setLoading(false);
      setCurrentView('onboarding');
    } catch (err) {
      console.warn("Backend auth failed, proceeding in offline/mock mode", err);
      setLoading(false);
      setCurrentView('onboarding');
    }
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      await api.loginWithFirebase("mock-token");
      setLoading(false);
      setCurrentView('onboarding');
    } catch (err) {
      console.warn("Backend auth failed, proceeding in offline/mock mode", err);
      setLoading(false);
      setCurrentView('onboarding');
    }
  };

  return (
    <div className="relative min-h-screen bg-bg-primary flex items-center justify-center px-4 overflow-hidden pt-20">
      {/* Background blobs */}
      <div className="absolute top-1/4 left-1/3 w-[300px] h-[300px] rounded-full bg-accent-primary/10 blur-[80px] animate-pulse pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/3 w-[300px] h-[300px] rounded-full bg-accent-ai/10 blur-[90px] animate-pulse pointer-events-none" />

      {/* Main Glass Card */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md p-8 rounded-3xl glass-panel border-white/5 relative z-10 bg-bg-secondary/45 backdrop-blur-lg shadow-2xl flex flex-col"
      >
        {/* Top Header Logo */}
        <div className="flex flex-col items-center text-center space-y-2 mb-8">
          <div className="flex items-center justify-center w-12 h-12 rounded-2xl bg-accent-primary/10 border border-accent-primary/20 shadow-[0_0_20px_rgba(108,99,255,0.25)]">
            <Shield className="w-6 h-6 text-accent-primary" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-white mt-2">
            Initialize Security
          </h2>
          <p className="text-xs text-text-secondary">
            Secure entry to the world&apos;s first Safety Intelligence network.
          </p>
        </div>

        {/* Custom Tab Switchers */}
        <div className="flex p-1 mb-6 rounded-xl bg-bg-primary/60 border border-white/5">
          <button
            onClick={() => { setActiveTab('phone'); setOtpSent(false); }}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-xs font-semibold transition-all duration-300 ${
              activeTab === 'phone'
                ? 'bg-accent-primary/20 border border-accent-primary/30 text-white'
                : 'text-text-secondary hover:text-white border border-transparent'
            }`}
          >
            <Smartphone className="w-3.5 h-3.5" />
            <span>Phone</span>
          </button>
          <button
            onClick={() => setActiveTab('email')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-xs font-semibold transition-all duration-300 ${
              activeTab === 'email'
                ? 'bg-accent-primary/20 border border-accent-primary/30 text-white'
                : 'text-text-secondary hover:text-white border border-transparent'
            }`}
          >
            <Mail className="w-3.5 h-3.5" />
            <span>Email</span>
          </button>
          <button
            onClick={() => setActiveTab('google')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-xs font-semibold transition-all duration-300 ${
              activeTab === 'google'
                ? 'bg-accent-primary/20 border border-accent-primary/30 text-white'
                : 'text-text-secondary hover:text-white border border-transparent'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Google</span>
          </button>
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 'phone' && (
            <motion.form
              key="phone"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              onSubmit={handlePhoneSubmit}
              className="space-y-4"
            >
              {!otpSent ? (
                <div className="space-y-2">
                  <label className="text-[11px] font-bold text-text-secondary uppercase tracking-widest block">
                    Phone Number
                  </label>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-text-secondary text-sm font-semibold">
                      +1
                    </span>
                    <input
                      type="tel"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, '').slice(0, 10))}
                      placeholder="(555) 000-0000"
                      className="w-full pl-12 pr-4 py-3 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-sm font-medium focus:border-accent-primary focus:outline-none transition-colors"
                      required
                    />
                  </div>
                  <p className="text-[10px] text-text-secondary leading-relaxed">
                    We will send a high-priority 6-digit verification code to secure your node coordinates.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <label className="text-[11px] font-bold text-text-secondary uppercase tracking-widest block">
                      Verification Code
                    </label>
                    <button 
                      type="button" 
                      onClick={() => setOtpSent(false)} 
                      className="text-[10px] text-accent-ai hover:underline"
                    >
                      Change Number
                    </button>
                  </div>
                  <input
                    type="text"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="Enter code"
                    maxLength={6}
                    className="w-full px-4 py-3 rounded-xl bg-bg-primary/50 border border-white/10 text-center tracking-widest text-lg font-bold text-white focus:border-accent-primary focus:outline-none transition-colors"
                    required
                  />
                  <p className="text-[10px] text-text-secondary text-center">
                    Didn&apos;t receive code? <button type="button" className="text-accent-primary hover:underline">Resend</button>
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-accent-primary hover:bg-[#594fff] text-white text-sm font-bold shadow-[0_0_15px_rgba(108,99,255,0.2)] hover:shadow-[0_0_25px_rgba(108,99,255,0.45)] transition-all duration-300 cursor-pointer disabled:opacity-50"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <span>{otpSent ? 'Verify & Continue' : 'Send Authentication Code'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </motion.form>
          )}

          {activeTab === 'email' && (
            <motion.form
              key="email"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              onSubmit={handleEmailSubmit}
              className="space-y-4"
            >
              <div className="space-y-1.5">
                <label className="text-[11px] font-bold text-text-secondary uppercase tracking-widest block">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@wosafe.com"
                    className="w-full pl-11 pr-4 py-3 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-sm font-medium focus:border-accent-primary focus:outline-none transition-colors"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <label className="text-[11px] font-bold text-text-secondary uppercase tracking-widest block">
                    Security Password
                  </label>
                  <button type="button" className="text-[10px] text-text-secondary hover:text-white">
                    Forgot?
                  </button>
                </div>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-11 pr-11 py-3 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-sm font-medium focus:border-accent-primary focus:outline-none transition-colors"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-text-secondary hover:text-white"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-accent-primary hover:bg-[#594fff] text-white text-sm font-bold shadow-[0_0_15px_rgba(108,99,255,0.2)] hover:shadow-[0_0_25px_rgba(108,99,255,0.45)] transition-all duration-300 cursor-pointer disabled:opacity-50"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Authenticate Account</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </motion.form>
          )}

          {activeTab === 'google' && (
            <motion.div
              key="google"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="space-y-6 text-center py-4"
            >
              <p className="text-xs text-text-secondary max-w-xs mx-auto leading-relaxed">
                Connect your pre-verified Google Workspace profile to sync trusted guardians and contact history instantly.
              </p>
              
              <button
                onClick={handleGoogleLogin}
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 py-3.5 rounded-xl bg-white text-bg-primary font-bold text-sm hover:bg-zinc-200 transition-colors duration-300 shadow-md cursor-pointer disabled:opacity-50"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-bg-primary border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <svg className="w-4 h-4" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                      />
                    </svg>
                    <span>Log in with Google</span>
                  </>
                )}
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer info links */}
        <div className="mt-8 pt-6 border-t border-white/5 text-center flex justify-between text-[10px] text-text-secondary">
          <span>Need Assistance?</span>
          <button onClick={() => setCurrentView('landing')} className="hover:text-white transition-colors">
            Return Home
          </button>
        </div>
      </motion.div>
    </div>
  );
}
