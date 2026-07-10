'use client';

import React, { useState } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/services/api';
import { 
  User, 
  MapPin, 
  Camera, 
  Mic, 
  Bell, 
  Activity,
  Plus, 
  Trash2,
  CheckCircle2, 
  Sparkles, 
  ShieldCheck, 
  ArrowRight, 
  ArrowLeft,
  Eye
} from 'lucide-react';

export default function OnboardingFlow() {
  const { 
    currentView, 
    setCurrentView, 
    user, 
    setUser, 
    permissions, 
    setPermission,
    safeWord,
    setSafeWord
  } = useSafeStore();

  const [step, setStep] = useState(1);
  const [profileName, setProfileName] = useState(user.name);
  const [bloodGroup, setBloodGroup] = useState(user.bloodGroup);
  const [medical, setMedical] = useState(user.medicalConditions);
  const [contacts, setContacts] = useState(user.emergencyContacts);
  const [newContactName, setNewContactName] = useState('');
  const [newContactPhone, setNewContactPhone] = useState('');
  const [newContactRelation, setNewContactRelation] = useState('');

  // AI Setup variables
  const [safeWordVal, setSafeWordVal] = useState(safeWord);
  const [pref, setPref] = useState(user.travelPreferences);
  const [routes, setRoutes] = useState<string[]>(user.dailyRoutes);
  const [newRoute, setNewRoute] = useState('');

  const addContact = () => {
    if (!newContactName || !newContactPhone) return;
    setContacts([...contacts, { name: newContactName, phone: newContactPhone, relation: newContactRelation || 'Contact' }]);
    setNewContactName('');
    setNewContactPhone('');
    setNewContactRelation('');
  };

  const removeContact = (index: number) => {
    setContacts(contacts.filter((_, i) => i !== index));
  };

  const addRouteItem = () => {
    if (!newRoute) return;
    setRoutes([...routes, newRoute]);
    setNewRoute('');
  };

  const removeRouteItem = (index: number) => {
    setRoutes(routes.filter((_, i) => i !== index));
  };

  // Simulated permission triggers
  const requestPermission = (key: keyof typeof permissions) => {
    setPermission(key, true);
  };

  const handleNextStep = () => {
    if (step === 1) {
      setUser({
        name: profileName,
        bloodGroup,
        medicalConditions: medical,
        emergencyContacts: contacts
      });
      setStep(2);
    } else if (step === 2) {
      setStep(3);
    } else if (step === 3) {
      setUser({
        travelPreferences: pref,
        dailyRoutes: routes
      });
      setSafeWord(safeWordVal);
      
      // Save profile to backend
      api.updateProfile({
        name: profileName,
        blood_group: bloodGroup,
        medical_conditions: medical,
        travel_preferences: pref,
        safe_word: safeWordVal,
      }).catch(err => console.warn("Failed saving profile to backend", err));
      
      // Save contacts to backend
      contacts.forEach(contact => {
        api.addContact({
          name: contact.name,
          phone: contact.phone,
          relation: contact.relation,
          priority: 1,
        }).catch(err => console.warn("Failed saving contact to backend", err));
      });
      
      setStep(4);
    } else if (step === 4) {
      setCurrentView('dashboard');
    }
  };

  const handlePrevStep = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  // Steps headers
  const stepsMeta = [
    { title: "Profile Credentials", subtitle: "Build your secure medical and emergency identity." },
    { title: "Hardware Permissions", subtitle: "Connect WoSafe to device sensors for active telemetry." },
    { title: "AI Guardian Configuration", subtitle: "Define your safe parameters, routes, and emergency triggers." },
    { title: "Guardian Activated", subtitle: "Your protective shield is fully deployed." }
  ];

  return (
    <div className="relative min-h-screen bg-bg-primary flex items-center justify-center px-4 overflow-hidden pt-24 pb-16">
      
      {/* Background blobs */}
      <div className="absolute top-1/4 left-1/3 w-[300px] h-[300px] rounded-full bg-accent-primary/5 blur-[80px] animate-pulse pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/3 w-[300px] h-[300px] rounded-full bg-accent-ai/5 blur-[90px] animate-pulse pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl p-5 sm:p-8 rounded-3xl glass-panel border-white/5 relative z-10 bg-bg-secondary/40 backdrop-blur-lg shadow-2xl flex flex-col"
      >
        
        {/* Step progress indicators */}
        <div className="flex items-center gap-2 mb-8">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex-1 flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 border ${
                s === step 
                  ? 'bg-accent-primary border-accent-primary text-white shadow-[0_0_12px_rgba(108,99,255,0.4)]'
                  : s < step 
                  ? 'bg-accent-ai/20 border-accent-ai/30 text-accent-ai' 
                  : 'bg-bg-primary/50 border-white/10 text-text-secondary'
              }`}>
                {s < step ? <CheckCircle2 className="w-4 h-4" /> : s}
              </div>
              {s < 4 && (
                <div className={`flex-1 h-0.5 mx-2 rounded-full transition-colors duration-300 ${
                  s < step ? 'bg-accent-ai' : 'bg-white/10'
                }`} />
              )}
            </div>
          ))}
        </div>

        {/* Dynamic header details */}
        <div className="mb-6 space-y-1">
          <h2 className="text-xl font-bold text-white tracking-tight">
            {stepsMeta[step - 1].title}
          </h2>
          <p className="text-xs text-text-secondary">
            {stepsMeta[step - 1].subtitle}
          </p>
        </div>

        {/* Steps Content Area */}
        <div className="min-h-[280px] flex flex-col justify-between py-2">
          <AnimatePresence mode="wait">
            {step === 1 && (
              <motion.div 
                key="step1"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                className="space-y-4"
              >
                {/* Photo and Name */}
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-center">
                  <div className="flex flex-col items-center sm:items-start col-span-1">
                    <div className="w-16 h-16 rounded-full border border-white/10 bg-white/5 flex items-center justify-center text-text-secondary relative overflow-hidden group">
                      <User className="w-8 h-8" />
                      <button className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center text-[9px] font-bold text-white transition-opacity">
                        Upload
                      </button>
                    </div>
                  </div>
                  
                  <div className="col-span-3 space-y-1">
                    <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">
                      Full Name
                    </label>
                    <input 
                      type="text" 
                      value={profileName}
                      onChange={(e) => setProfileName(e.target.value)}
                      placeholder="Enter full name"
                      className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                {/* Medical parameters */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">
                      Blood Group
                    </label>
                    <select 
                      value={bloodGroup} 
                      onChange={(e) => setBloodGroup(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none transition-colors"
                    >
                      <option value="O+">O Positive (O+)</option>
                      <option value="O-">O Negative (O-)</option>
                      <option value="A+">A Positive (A+)</option>
                      <option value="A-">A Negative (A-)</option>
                      <option value="B+">B Positive (B+)</option>
                      <option value="B-">B Negative (B-)</option>
                      <option value="AB+">AB Positive (AB+)</option>
                      <option value="AB-">AB Negative (AB-)</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">
                      Medical Conditions
                    </label>
                    <input 
                      type="text" 
                      value={medical}
                      onChange={(e) => setMedical(e.target.value)}
                      placeholder="e.g. Asthma, Allergies, None"
                      className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                {/* Emergency Contacts builder */}
                <div className="space-y-3">
                  <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">
                    Emergency Contacts
                  </label>

                  {/* List of contacts */}
                  <div className="space-y-2 max-h-[120px] overflow-y-auto pr-1">
                    {contacts.map((c, i) => (
                      <div key={i} className="flex justify-between items-center px-4 py-2 rounded-xl bg-white/5 border border-white/5">
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-white">{c.name} ({c.relation})</span>
                          <span className="text-[10px] text-text-secondary">{c.phone}</span>
                        </div>
                        <button 
                          onClick={() => removeContact(i)}
                          className="p-1.5 rounded-lg text-text-secondary hover:text-danger-custom hover:bg-white/5 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))}
                    {contacts.length === 0 && (
                      <p className="text-xs italic text-text-secondary">No contacts added yet. Minimum 1 required for SOS alerts.</p>
                    )}
                  </div>

                  {/* Add form */}
                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 items-end bg-bg-primary/30 p-3 rounded-xl border border-white/5">
                    <input 
                      type="text" 
                      placeholder="Name" 
                      value={newContactName}
                      onChange={(e) => setNewContactName(e.target.value)}
                      className="sm:col-span-1.5 px-3 py-1.5 rounded-lg bg-bg-primary/60 border border-white/10 text-white text-xs"
                    />
                    <input 
                      type="tel" 
                      placeholder="Phone (+1...)" 
                      value={newContactPhone}
                      onChange={(e) => setNewContactPhone(e.target.value)}
                      className="sm:col-span-1.5 px-3 py-1.5 rounded-lg bg-bg-primary/60 border border-white/10 text-white text-xs"
                    />
                    <input 
                      type="text" 
                      placeholder="Relation" 
                      value={newContactRelation}
                      onChange={(e) => setNewContactRelation(e.target.value)}
                      className="px-3 py-1.5 rounded-lg bg-bg-primary/60 border border-white/10 text-white text-xs"
                    />
                    <button 
                      type="button" 
                      onClick={addContact}
                      className="flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-accent-primary text-white text-xs font-bold hover:bg-[#594fff] transition-all cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Add</span>
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div 
                key="step2"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                className="space-y-4"
              >
                <p className="text-xs text-text-secondary leading-relaxed">
                  WoSafe is an active intelligence service. It requires device sensors to monitor locations, analyze risks, record testimony, and send priority push alerts.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Location */}
                  <div className="p-4 rounded-xl border border-white/5 bg-bg-primary/30 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <MapPin className={`w-5 h-5 ${permissions.location ? 'text-accent-ai' : 'text-text-secondary'}`} />
                      <div className="flex flex-col">
                        <span className="text-xs font-bold text-white">Location</span>
                        <span className="text-[10px] text-text-secondary">Active route mapping</span>
                      </div>
                    </div>
                    <button 
                      type="button"
                      onClick={() => requestPermission('location')}
                      className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all ${
                        permissions.location 
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                          : 'bg-white/5 border border-white/10 text-white hover:bg-white/10'
                      }`}
                    >
                      {permissions.location ? 'Allowed' : 'Grant'}
                    </button>
                  </div>

                  {/* Camera */}
                  <div className="p-4 rounded-xl border border-white/5 bg-bg-primary/30 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Camera className={`w-5 h-5 ${permissions.camera ? 'text-accent-primary' : 'text-text-secondary'}`} />
                      <div className="flex flex-col">
                        <span className="text-xs font-bold text-white">Camera</span>
                        <span className="text-[10px] text-text-secondary">Automatic incident clips</span>
                      </div>
                    </div>
                    <button 
                      type="button"
                      onClick={() => requestPermission('camera')}
                      className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all ${
                        permissions.camera 
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                          : 'bg-white/5 border border-white/10 text-white hover:bg-white/10'
                      }`}
                    >
                      {permissions.camera ? 'Allowed' : 'Grant'}
                    </button>
                  </div>

                  {/* Microphone */}
                  <div className="p-4 rounded-xl border border-white/5 bg-bg-primary/30 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Mic className={`w-5 h-5 ${permissions.microphone ? 'text-accent-ai' : 'text-text-secondary'}`} />
                      <div className="flex flex-col">
                        <span className="text-xs font-bold text-white">Microphone</span>
                        <span className="text-[10px] text-text-secondary">Acoustic safe word scan</span>
                      </div>
                    </div>
                    <button 
                      type="button"
                      onClick={() => requestPermission('microphone')}
                      className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all ${
                        permissions.microphone 
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                          : 'bg-white/5 border border-white/10 text-white hover:bg-white/10'
                      }`}
                    >
                      {permissions.microphone ? 'Allowed' : 'Grant'}
                    </button>
                  </div>

                  {/* Motion sensors */}
                  <div className="p-4 rounded-xl border border-white/5 bg-bg-primary/30 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Activity className={`w-5 h-5 ${permissions.motion ? 'text-accent-primary' : 'text-text-secondary'}`} />
                      <div className="flex flex-col">
                        <span className="text-xs font-bold text-white">Motion Sensors</span>
                        <span className="text-[10px] text-text-secondary">Deviation and impact trigger</span>
                      </div>
                    </div>
                    <button 
                      type="button"
                      onClick={() => requestPermission('motion')}
                      className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all ${
                        permissions.motion 
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                          : 'bg-white/5 border border-white/10 text-white hover:bg-white/10'
                      }`}
                    >
                      {permissions.motion ? 'Allowed' : 'Grant'}
                    </button>
                  </div>

                  {/* Notifications */}
                  <div className="p-4 rounded-xl border border-white/5 bg-bg-primary/30 flex items-center justify-between sm:col-span-2">
                    <div className="flex items-center gap-3">
                      <Bell className={`w-5 h-5 ${permissions.notifications ? 'text-accent-ai' : 'text-text-secondary'}`} />
                      <div className="flex flex-col">
                        <span className="text-xs font-bold text-white">Push Notifications</span>
                        <span className="text-[10px] text-text-secondary">Priority warnings, hazard announcements, and safety check-ins</span>
                      </div>
                    </div>
                    <button 
                      type="button"
                      onClick={() => requestPermission('notifications')}
                      className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all ${
                        permissions.notifications 
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                          : 'bg-white/5 border border-white/10 text-white hover:bg-white/10'
                      }`}
                    >
                      {permissions.notifications ? 'Allowed' : 'Grant'}
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div 
                key="step3"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                className="space-y-4"
              >
                {/* Emergency Safe word */}
                <div className="space-y-1.5 p-4 rounded-2xl bg-danger-custom/5 border border-danger-custom/25 shadow-[0_0_15px_rgba(255,77,109,0.05)]">
                  <div className="flex justify-between items-center">
                    <label className="text-[10px] font-bold text-danger-custom uppercase tracking-widest block">
                      Emergency Safe Word
                    </label>
                    <span className="text-[9px] text-text-secondary italic">Continuous Acoustic Trigger</span>
                  </div>
                  <div className="relative">
                    <input 
                      type="text" 
                      value={safeWordVal}
                      onChange={(e) => setSafeWordVal(e.target.value)}
                      placeholder="e.g. Phoenix"
                      className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-danger-custom/20 text-white text-xs font-bold focus:border-danger-custom focus:outline-none transition-colors"
                    />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5 text-[9px] text-danger-custom/75">
                      <Eye className="w-3 h-3" />
                      <span>Confidential</span>
                    </div>
                  </div>
                  <p className="text-[9px] text-text-secondary leading-relaxed">
                    Saying this word aloud when WoSafe is active will instantly bypass all locks and activate emergency SOS mode without audio confirmation.
                  </p>
                </div>

                {/* Travel preferences */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">
                    Travel Preferences
                  </label>
                  <input 
                    type="text" 
                    value={pref}
                    onChange={(e) => setPref(e.target.value)}
                    placeholder="e.g. High lighting density, verified safe businesses"
                    className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/50 border border-white/10 text-white text-xs font-semibold focus:border-accent-primary focus:outline-none transition-colors"
                  />
                </div>

                {/* Standard routes */}
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-text-secondary uppercase tracking-widest block">
                    Daily Travel Routes (AI Monitoring)
                  </label>

                  <div className="space-y-1 max-h-[80px] overflow-y-auto">
                    {routes.map((r, i) => (
                      <div key={i} className="flex justify-between items-center px-3 py-1.5 rounded-lg bg-white/5 text-xs text-white">
                        <span>{r}</span>
                        <button type="button" onClick={() => removeRouteItem(i)} className="text-text-secondary hover:text-danger-custom">
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>

                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      value={newRoute}
                      onChange={(e) => setNewRoute(e.target.value)}
                      placeholder="e.g. Commute to Office"
                      className="flex-1 px-3 py-2 rounded-lg bg-bg-primary/60 border border-white/10 text-xs text-white focus:outline-none focus:border-accent-primary"
                    />
                    <button 
                      type="button" 
                      onClick={addRouteItem}
                      className="px-3 rounded-lg bg-accent-ai text-bg-primary text-xs font-bold hover:bg-[#1feaff] transition-colors cursor-pointer"
                    >
                      Add Route
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 4 && (
              <motion.div 
                key="step4"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center text-center space-y-6 py-6"
              >
                <div className="relative flex items-center justify-center w-20 h-20 rounded-full bg-accent-ai/10 border border-accent-ai/20 shadow-[0_0_25px_rgba(0,229,255,0.25)] animate-pulse">
                  <ShieldCheck className="w-10 h-10 text-accent-ai" />
                  <div className="absolute inset-0 rounded-full bg-accent-ai/20 blur-md animate-ping opacity-60" />
                </div>

                <div className="space-y-2 max-w-md">
                  <h3 className="text-2xl font-bold tracking-tight text-white flex items-center justify-center gap-1.5">
                    <span>Platform Online</span>
                    <Sparkles className="w-5 h-5 text-accent-ai" />
                  </h3>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    Welcome to the node, Sarah. Your personal profile, location credentials, emergency triggers, and daily safety path models have been compiled.
                  </p>
                  <div className="p-4 rounded-2xl bg-bg-primary/45 border border-white/5 text-[11px] text-accent-ai font-semibold inline-block">
                    AI Guardian Security Score: 94% (Stable)
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Wizard Controls */}
        <div className="mt-8 pt-6 border-t border-white/5 flex justify-between items-center">
          {step > 1 && step < 4 ? (
            <button 
              onClick={handlePrevStep}
              className="flex items-center gap-1.5 px-4 py-2.5 text-xs font-semibold rounded-xl border border-white/10 text-white hover:bg-white/5 transition-all duration-300 cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </button>
          ) : (
            <div />
          )}

          <button
            onClick={handleNextStep}
            className={`flex items-center gap-1.5 px-6 py-2.5 rounded-xl text-xs font-bold transition-all duration-300 cursor-pointer ${
              step === 4 
                ? 'bg-accent-ai hover:bg-[#1feaff] text-bg-primary shadow-[0_0_15px_rgba(0,229,255,0.25)]' 
                : 'bg-accent-primary hover:bg-[#594fff] text-white shadow-[0_0_15px_rgba(108,99,255,0.2)]'
            }`}
          >
            <span>{step === 4 ? 'Enter Cockpit' : 'Next Step'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

      </motion.div>
    </div>
  );
}
