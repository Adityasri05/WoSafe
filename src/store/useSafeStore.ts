import { create } from 'zustand';

export type ViewType =
  | 'landing'
  | 'auth'
  | 'onboarding'
  | 'dashboard'
  | 'routes'
  | 'ai-guardian'
  | 'community'
  | 'report'
  | 'analytics'
  | 'guardian-mode'
  | 'emergency'
  | 'profile'
  | 'settings';

export interface EmergencyContact {
  name: string;
  phone: string;
  relation: string;
}

export interface UserProfile {
  name: string;
  photo: string;
  emergencyContacts: EmergencyContact[];
  bloodGroup: string;
  medicalConditions: string;
  travelPreferences: string;
  dailyRoutes: string[];
}

export interface PermissionState {
  location: boolean;
  camera: boolean;
  microphone: boolean;
  motion: boolean;
  notifications: boolean;
}

export interface IncidentReport {
  id: string;
  title: string;
  category: string;
  location: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  time: string;
  votes: number;
  anonymous: boolean;
  userReported?: boolean;
}

export interface NotificationItem {
  id: string;
  title: string;
  content: string;
  type: 'alert' | 'update' | 'recommendation' | 'emergency';
  time: string;
  read: boolean;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  time: string;
}

interface SafeStore {
  currentView: ViewType;
  setCurrentView: (view: ViewType) => void;
  user: UserProfile;
  setUser: (user: Partial<UserProfile>) => void;
  onboardingStep: number;
  setOnboardingStep: (step: number) => void;
  permissions: PermissionState;
  setPermission: (key: keyof PermissionState, val: boolean) => void;
  safetyScore: number;
  setSafetyScore: (score: number) => void;
  activeJourney: {
    started: boolean;
    destination: string;
    selectedRoute: 'shortest' | 'fastest' | 'safest';
    duration: string;
    eta: string;
    lighting: string;
    crowd: string;
    police: string;
  } | null;
  setActiveJourney: (journey: SafeStore['activeJourney']) => void;
  incidents: IncidentReport[];
  addIncident: (incident: Omit<IncidentReport, 'id' | 'votes' | 'time'>) => void;
  voteIncident: (id: string) => void;
  notifications: NotificationItem[];
  addNotification: (notif: Omit<NotificationItem, 'id' | 'time' | 'read'>) => void;
  markAllNotificationsRead: () => void;
  aiHistory: ChatMessage[];
  addAiMessage: (sender: 'user' | 'ai', text: string) => void;
  clearAiHistory: () => void;
  guardianModeActive: boolean;
  setGuardianModeActive: (active: boolean) => void;
  emergencyActive: boolean;
  setEmergencyActive: (active: boolean) => void;
  safeWord: string;
  setSafeWord: (word: string) => void;
}

export const useSafeStore = create<SafeStore>((set) => ({
  currentView: 'landing',
  setCurrentView: (view) => set({ currentView: view }),
  
  user: {
    name: 'Sarah Chen',
    photo: '',
    emergencyContacts: [
      { name: 'David Chen', phone: '+1 (555) 321-9876', relation: 'Father' },
      { name: 'Emma Watson', phone: '+1 (555) 456-7890', relation: 'Best Friend' }
    ],
    bloodGroup: 'O+',
    medicalConditions: 'Asthma (Carry inhaler)',
    travelPreferences: 'Prefer high-street lighting, avoid dark alleys',
    dailyRoutes: ['Home to Workspace', 'Workspace to Fitness Center']
  },
  setUser: (updatedUser) => set((state) => ({ user: { ...state.user, ...updatedUser } })),
  
  onboardingStep: 1,
  setOnboardingStep: (step) => set({ onboardingStep: step }),
  
  permissions: {
    location: false,
    camera: false,
    microphone: false,
    motion: false,
    notifications: false
  },
  setPermission: (key, val) =>
    set((state) => ({ permissions: { ...state.permissions, [key]: val } })),
  
  safetyScore: 94,
  setSafetyScore: (score) => set({ safetyScore: score }),
  
  activeJourney: null,
  setActiveJourney: (journey) => set({ activeJourney: journey }),
  
  incidents: [
    {
      id: '1',
      title: 'Broken Streetlights',
      category: 'Infrastructure',
      location: '5th Ave & 23rd St',
      description: 'Entire block of streetlights are completely out. Very dark area.',
      severity: 'medium',
      time: '2 hours ago',
      votes: 14,
      anonymous: true
    },
    {
      id: '2',
      title: 'Suspicious Loitering',
      category: 'Safety Alert',
      location: 'Broadway Subway Exit B',
      description: 'Group of individuals harassing passersby near the entrance.',
      severity: 'high',
      time: '45 mins ago',
      votes: 28,
      anonymous: false
    },
    {
      id: '3',
      title: 'Safe Haven Added: Cafe Bloom',
      category: 'Safe Business',
      location: '12 Maple St',
      description: '24/7 cafe. Staff trained in safety protocols. Offers phone charger and safe waiting zone.',
      severity: 'low',
      time: '1 day ago',
      votes: 45,
      anonymous: false
    }
  ],
  addIncident: (incident) =>
    set((state) => ({
      incidents: [
        {
          ...incident,
          id: Date.now().toString(),
          time: 'Just now',
          votes: 0
        },
        ...state.incidents
      ]
    })),
  voteIncident: (id) =>
    set((state) => ({
      incidents: state.incidents.map((inc) =>
        inc.id === id ? { ...inc, votes: inc.votes + 1 } : inc
      )
    })),
  
  notifications: [
    {
      id: '1',
      title: 'Safety Recommendation',
      content: 'AI detected low street lighting on your standard return path. Consider using Safest Route alternate tonight.',
      type: 'recommendation',
      time: '15m ago',
      read: false
    },
    {
      id: '2',
      title: 'Guardian Alert',
      content: 'David Chen verified active emergency link connection.',
      type: 'update',
      time: '30m ago',
      read: false
    },
    {
      id: '3',
      title: 'High Risk Incident Nearby',
      content: 'A harassment incident reported 200m from your current position. AI Guardian is monitoring.',
      type: 'alert',
      time: '1h ago',
      read: true
    }
  ],
  addNotification: (notif) =>
    set((state) => ({
      notifications: [
        {
          ...notif,
          id: Date.now().toString(),
          time: 'Just now',
          read: false
        },
        ...state.notifications
      ]
    })),
  markAllNotificationsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true }))
    })),
  
  aiHistory: [
    {
      id: '1',
      sender: 'ai',
      text: 'Hello Sarah. I am WoSafe Guardian AI, your continuous personal safety intelligence. How can I help protect you today?',
      time: '8:00 PM'
    }
  ],
  addAiMessage: (sender, text) =>
    set((state) => ({
      aiHistory: [
        ...state.aiHistory,
        {
          id: Date.now().toString(),
          sender,
          text,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]
    })),
  clearAiHistory: () =>
    set({
      aiHistory: [
        {
          id: '1',
          sender: 'ai',
          text: 'AI Guardian history cleared. I am ready to protect you.',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]
    }),
  
  guardianModeActive: false,
  setGuardianModeActive: (active) => set({ guardianModeActive: active }),
  
  emergencyActive: false,
  setEmergencyActive: (active) => set({ emergencyActive: active }),
  
  safeWord: 'Phoenix',
  setSafeWord: (word) => set({ safeWord: word })
}));
