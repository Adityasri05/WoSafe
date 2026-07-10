import React, { useState, useRef, useEffect } from 'react';
import { useSafeStore } from '@/store/useSafeStore';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/services/api';
import { 
  Send, 
  Mic, 
  Sparkles, 
  AlertTriangle,
  HelpCircle,
  ShieldCheck,
  Volume2,
  Trash2
} from 'lucide-react';

export default function AIGuardian() {
  const { 
    aiHistory, 
    addAiMessage, 
    clearAiHistory, 
    setGuardianModeActive, 
    setCurrentView,
    setEmergencyActive
  } = useSafeStore();

  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isVoiceRecording, setIsVoiceRecording] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [aiHistory, isTyping]);

  const suggestions = [
    "I think someone is following me.",
    "Find the safest route home.",
    "Nearby Police Station?",
    "Activate Guardian Mode"
  ];

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    
    // Add user message
    addAiMessage('user', text);
    setInput('');
    setIsTyping(true);

    try {
      const result = await api.chatWithAI(text, conversationId, {
        latitude: 37.7749,
        longitude: -122.4194,
      });
      
      setIsTyping(false);
      addAiMessage('ai', result.response);
      if (result.conversation_id) {
        setConversationId(result.conversation_id);
      }
      
      if (result.emergency_detected) {
        setEmergencyActive(true);
        setCurrentView('emergency');
      } else if (text.toLowerCase().includes('guardian')) {
        setGuardianModeActive(true);
        setTimeout(() => setCurrentView('guardian-mode'), 2000);
      } else if (text.toLowerCase().includes('route')) {
        setTimeout(() => setCurrentView('routes'), 2000);
      }
    } catch (error) {
      console.warn("Backend chat failed, running fallback mock simulator", error);
      setTimeout(() => {
        setIsTyping(false);
        const query = text.toLowerCase();
        
        if (query.includes('follow') || query.includes('danger') || query.includes('scared')) {
          addAiMessage('ai', "🚨 CRITICAL RISK STATE DETECTED. I have flagged your location. I am ready to link with David Chen (+1 (555) 321-9876) and Emma Watson. Would you like me to trigger emergency SOS or activate Guardian Mode HUD right now?");
        } 
        else if (query.includes('guardian') || query.includes('activate guardian')) {
          setGuardianModeActive(true);
          addAiMessage('ai', "🛡️ Guardian Mode initialized. Telemetry tracking active. Front-facing camera lens calibrated. Audio scan active for safe word: 'Phoenix'. Let's walk safely together.");
          setTimeout(() => {
            setCurrentView('guardian-mode');
          }, 2200);
        } 
        else if (query.includes('route') || query.includes('path') || query.includes('home') || query.includes('safest')) {
          addAiMessage('ai', "🗺️ Analyzing local street lighting indexes and crowd clusters. I've computed the 'Safest Route' which bypasses a dark alley on 5th Ave and has active police presence. Let's switch to the Safe Routes planner.");
          setTimeout(() => {
            setCurrentView('routes');
          }, 2200);
        } 
        else if (query.includes('police') || query.includes('station') || query.includes('help')) {
          addAiMessage('ai', "📍 North Precinct Police Station is located 400m North-East (estimated arrival 4 mins walking). There is also a Metro Police Kiosk located 350m ahead. I have pinned them on your radar map.");
        }
        else {
          addAiMessage('ai', "I am monitoring your local safety parameters continuously. You can ask me to compare safe routes, activate Guardian Mode, locate secure sanctuaries, or alert your emergency contacts.");
        }
      }, 1000);
    }
  };

  const handleVoiceToggle = () => {
    if (!isVoiceRecording) {
      setIsVoiceRecording(true);
      // Simulate speaking after 3 seconds
      setTimeout(() => {
        setIsVoiceRecording(false);
        handleSend("I think someone is following me.");
      }, 3000);
    } else {
      setIsVoiceRecording(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-bg-primary pt-24 pb-28 md:pb-16 px-4 flex flex-col justify-between max-w-4xl mx-auto">
      
      {/* Aurora glow top right */}
      <div className="absolute top-10 right-10 w-[300px] h-[300px] rounded-full bg-accent-ai/5 blur-[90px] pointer-events-none" />

      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-white/5 pb-4 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-accent-ai/10 border border-accent-ai/20 text-accent-ai shadow-[0_0_15px_rgba(0,229,255,0.15)] animate-pulse">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">AI Guardian Core</h2>
            <p className="text-[10px] text-text-secondary">Fully Encrypted Neural Safety Link</p>
          </div>
        </div>

        <button 
          onClick={clearAiHistory}
          title="Clear History"
          className="p-2 rounded-xl border border-white/5 bg-bg-secondary/40 text-text-secondary hover:text-white transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Messages viewport */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 min-h-[350px] max-h-[50vh] scrollbar-thin">
        {aiHistory.map((msg) => {
          const isAi = msg.sender === 'ai';
          const isAlert = msg.text.includes('🚨') || msg.text.includes('CRITICAL');
          return (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${isAi ? 'justify-start' : 'justify-end'}`}
            >
              <div className={`max-w-[80%] p-4 rounded-2xl border text-xs leading-relaxed ${
                !isAi 
                  ? 'bg-accent-primary/20 border-accent-primary/30 text-white rounded-tr-none'
                  : isAlert
                  ? 'bg-danger-custom/10 border-danger-custom/25 text-white rounded-tl-none shadow-[0_0_15px_rgba(255,77,109,0.05)]'
                  : 'bg-bg-secondary/60 border-white/5 text-text-secondary rounded-tl-none'
              }`}>
                {/* Message text */}
                <p className="whitespace-pre-line">{msg.text}</p>
                
                {/* Meta details footer */}
                <div className="mt-2 flex justify-between items-center text-[9px] opacity-60">
                  <span className="font-mono">{msg.time}</span>
                  {isAi && (
                    <div className="flex items-center gap-1">
                      <Volume2 className="w-3 h-3 hover:text-white cursor-pointer" />
                      <span>Speech enabled</span>
                    </div>
                  )}
                </div>

                {/* Inline Actions if critical */}
                {isAlert && (
                  <div className="mt-3 flex gap-2">
                    <button 
                      onClick={() => {
                        setGuardianModeActive(true);
                        setCurrentView('guardian-mode');
                      }}
                      className="px-3 py-1.5 rounded-lg bg-accent-ai text-bg-primary font-bold text-[9px] hover:bg-[#1feaff] transition-colors"
                    >
                      Enter Guardian Mode
                    </button>
                    <button 
                      onClick={() => {
                        setEmergencyActive(true);
                        setCurrentView('emergency');
                      }}
                      className="px-3 py-1.5 rounded-lg bg-danger-custom text-white font-bold text-[9px] hover:bg-red-600 transition-colors"
                    >
                      Trigger SOS
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-bg-secondary/60 border border-white/5 p-4 rounded-2xl rounded-tl-none flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-ai animate-bounce" />
              <span className="w-1.5 h-1.5 rounded-full bg-accent-ai animate-bounce [animation-delay:0.2s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-accent-ai animate-bounce [animation-delay:0.4s]" />
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Suggested Questions Grid */}
      <div className="mt-4 py-2">
        <span className="text-[9px] font-bold text-text-secondary uppercase tracking-widest block mb-2">
          Suggested Actions
        </span>
        <div className="grid grid-cols-2 gap-2">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => handleSend(s)}
              className="text-left px-3 py-2 rounded-xl border border-white/5 bg-bg-secondary/20 text-text-secondary hover:text-white hover:bg-white/5 hover:border-white/10 text-[10px] transition-all truncate"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Voice active indicator visual overlay */}
      <AnimatePresence>
        {isVoiceRecording && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-bg-primary/90 flex flex-col items-center justify-center space-y-6"
          >
            <div className="flex items-end gap-1.5 h-16">
              {[1, 2.5, 4, 2, 5.5, 3, 1.5, 4, 3, 5, 2, 1].map((h, i) => (
                <motion.div 
                  key={i}
                  animate={{ height: [8, h * 10, 8] }}
                  transition={{ duration: 0.8 + (i * 0.04), repeat: Infinity, ease: 'easeInOut' }}
                  className="w-1.5 bg-accent-ai rounded-full"
                />
              ))}
            </div>
            <div className="text-center space-y-1">
              <span className="text-xs font-bold text-accent-ai uppercase tracking-wider block">Listening to Ambient Environment</span>
              <span className="text-[10px] text-text-secondary">Whisper your safe word to activate crisis SOS</span>
            </div>
            <button 
              onClick={() => setIsVoiceRecording(false)}
              className="px-5 py-2 rounded-xl border border-white/10 text-white text-xs font-semibold hover:bg-white/5 transition-colors"
            >
              Cancel Listening
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom input area */}
      <div className="mt-4 flex gap-2 items-center bg-bg-secondary/40 p-2 rounded-2xl border border-white/5 backdrop-blur-md">
        <button
          onClick={handleVoiceToggle}
          title="Voice Command"
          className="p-3 rounded-xl bg-white/5 border border-white/10 text-text-secondary hover:text-white hover:border-white/20 transition-all cursor-pointer"
        >
          <Mic className="w-4 h-4 text-accent-ai" />
        </button>
        <input 
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask AI Guardian or state your situation..."
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSend(input);
          }}
          className="flex-1 bg-transparent px-2 border-0 text-xs text-white placeholder-text-secondary focus:outline-none focus:ring-0"
        />
        <button
          onClick={() => handleSend(input)}
          className="p-3 rounded-xl bg-accent-primary text-white hover:bg-[#594fff] shadow-[0_0_10px_rgba(108,99,255,0.2)] transition-colors cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>

    </div>
  );
}
