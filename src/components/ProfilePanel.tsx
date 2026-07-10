import React, { useEffect } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion } from 'framer-motion';
import { api } from '@/services/api';
import { 
  User, 
  Phone, 
  MapPin, 
  Award, 
  ShieldCheck, 
  Clock, 
  Activity,
  Heart,
  ChevronRight,
  TrendingUp
} from 'lucide-react';

export default function ProfilePanel() {
  const { user, setUser } = useSafeStore();

  useEffect(() => {
    api.getProfile()
      .then(res => {
        if (res) {
          setUser({
            name: res.name,
            bloodGroup: res.blood_group,
            medicalConditions: res.medical_conditions,
            travelPreferences: res.travel_preferences,
          });
        }
      })
      .catch(err => console.warn("Failed fetching user profile from backend", err));
  }, []);

  const achievements = [
    { title: "Safe Voyager", desc: "Completed 50+ AI-protected commutes.", icon: <ShieldCheck className="w-5 h-5 text-accent-ai" />, date: "June 2026" },
    { title: "Community Shield", desc: "Contributed 5 verified hazard warnings.", icon: <Award className="w-5 h-5 text-accent-primary" />, date: "May 2026" },
    { title: "First Responder Link", desc: "Configured pre-authorized emergency channels.", icon: <Activity className="w-5 h-5 text-emerald-400" />, date: "April 2026" }
  ];

  const travelHistory = [
    { id: 'h1', origin: '5th Ave Workspace', dest: 'Maple St Residence', date: 'Yesterday, 8:40 PM', type: 'Safest Route', duration: '16m' },
    { id: 'h2', origin: 'Fitness Center', dest: '5th Ave Workspace', date: 'Jul 6, 2026, 7:15 PM', type: 'Fastest Route', duration: '12m' },
    { id: 'h3', origin: 'Broadway Cafe Oasis', dest: 'Central Park South', date: 'Jul 4, 2026, 1:30 PM', type: 'Shortest Route', duration: '9m' }
  ];

  return (
    <div className="relative min-h-screen bg-bg-primary pt-24 pb-28 md:pb-16 px-4 max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      {/* Background glow top right */}
      <div className="absolute top-10 right-10 w-[300px] h-[300px] rounded-full bg-accent-primary/5 blur-[90px] pointer-events-none" />

      {/* Left Column: Personal security details card (col-span-4) */}
      <div className="lg:col-span-4 space-y-6">
        
        {/* Main Identity badge */}
        <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md flex flex-col items-center text-center space-y-4">
          <div className="w-20 h-20 rounded-full border-2 border-accent-ai/50 bg-white/5 flex items-center justify-center text-text-secondary relative overflow-hidden">
            <User className="w-10 h-10 text-white" />
          </div>

          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-tight">{user.name}</h2>
            <p className="text-[10px] text-accent-ai font-semibold uppercase tracking-wider mt-0.5">Verified Safe Node</p>
          </div>

          <div className="w-full pt-4 border-t border-white/5 flex justify-around text-center text-xs">
            <div className="flex flex-col">
              <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest">Blood Type</span>
              <span className="font-extrabold text-white mt-1 flex items-center gap-1 justify-center"><Heart className="w-3.5 h-3.5 text-danger-custom" />{user.bloodGroup}</span>
            </div>
            <div className="w-px h-6 bg-white/10" />
            <div className="flex flex-col">
              <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest">Watch Status</span>
              <span className="text-emerald-400 font-extrabold mt-1 uppercase tracking-wider">Active</span>
            </div>
          </div>
        </div>

        {/* Medical / Asthma conditions logs */}
        <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-3">
          <h3 className="text-xs font-bold text-white uppercase tracking-widest border-b border-white/5 pb-2">Medical Dispatch Details</h3>
          <div className="space-y-2 text-xs">
            <div>
              <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest block">Primary Conditions</span>
              <span className="text-white font-medium block mt-0.5">{user.medicalConditions}</span>
            </div>
            <div>
              <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest block">Allergies / Inhaler</span>
              <span className="text-white font-medium block mt-0.5">Penicillin sensitive, Asthma inhaler carried</span>
            </div>
          </div>
        </div>

        {/* Guardian emergency links */}
        <div className="p-6 rounded-3xl glass-panel border-white/5 bg-bg-secondary/40 backdrop-blur-md space-y-3">
          <h3 className="text-xs font-bold text-white uppercase tracking-widest border-b border-white/5 pb-2">Primary Emergency Guardians</h3>
          <div className="space-y-3">
            {user.emergencyContacts.map((contact, i) => (
              <div key={i} className="flex justify-between items-center text-xs">
                <div className="flex flex-col">
                  <span className="font-bold text-white">{contact.name}</span>
                  <span className="text-[10px] text-text-secondary">{contact.relation}</span>
                </div>
                <a href={`tel:${contact.phone}`} className="flex items-center gap-1 px-2.5 py-1 rounded-lg border border-white/5 bg-white/5 text-[10px] font-semibold text-accent-ai hover:text-white transition-colors">
                  <Phone className="w-3 h-3" />
                  <span>Call</span>
                </a>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Right Column: Milestones & Commute Logs (col-span-8) */}
      <div className="lg:col-span-8 space-y-6">
        
        {/* Achievements / Badges */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-white uppercase tracking-widest">Security Badges & Milestones</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {achievements.map((ach, i) => (
              <div key={i} className="p-5 rounded-2xl glass-panel border-white/5 bg-bg-secondary/20 flex flex-col justify-between min-h-[140px]">
                <div className="p-2.5 w-fit rounded-xl bg-white/5 border border-white/5">
                  {ach.icon}
                </div>
                
                <div className="space-y-0.5 mt-2">
                  <h4 className="text-xs font-bold text-white uppercase tracking-tight">{ach.title}</h4>
                  <p className="text-[9px] text-text-secondary leading-normal">{ach.desc}</p>
                </div>

                <span className="text-[8px] text-text-secondary/70 font-mono mt-2 block">{ach.date}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Journey History Logs */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-white uppercase tracking-widest">Safety Commute Audit Logs</h3>
          
          <div className="space-y-3">
            {travelHistory.map((item) => (
              <div key={item.id} className="p-4 rounded-xl border border-white/5 bg-bg-secondary/45 flex flex-col sm:flex-row justify-between sm:items-center gap-2">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-[10px] text-text-secondary">
                    <span className="font-mono">{item.date}</span>
                    <span>&bull;</span>
                    <span className="text-accent-ai font-bold uppercase">{item.type}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-white font-bold">
                    <span>{item.origin}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-text-secondary" />
                    <span>{item.dest}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 sm:justify-end text-xs text-text-secondary">
                  <span className="flex items-center gap-1 font-mono"><Clock className="w-3.5 h-3.5 text-accent-primary" />{item.duration}</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-[9px] text-emerald-400 font-bold uppercase tracking-wider">Completed</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
