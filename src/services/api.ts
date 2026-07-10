/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * WoSafe Frontend API Client Service
 * Handles HTTP requests to the FastAPI backend with token storage and automatic header management.
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

class ApiClient {
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('wosafe_access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    return headers;
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = { ...this.getHeaders(), ...options.headers };
    
    try {
      const response = await fetch(url, { ...options, headers });
      
      if (response.status === 401) {
        // Clear token on unauthorized
        if (typeof window !== 'undefined') {
          localStorage.removeItem('wosafe_access_token');
        }
      }
      
      if (!response.ok) {
        const errText = await response.text();
        let errMsg = `Request failed: ${response.status} ${response.statusText}`;
        try {
          const parsed = JSON.parse(errText);
          errMsg = parsed.detail || parsed.message || errMsg;
        } catch {}
        throw new Error(errMsg);
      }
      
      return await response.json() as T;
    } catch (error: any) {
      console.error(`API Error on ${endpoint}:`, error);
      throw error;
    }
  }

  // Auth
  async loginWithFirebase(firebaseToken: string) {
    const data = await this.request<{
      access_token: string;
      refresh_token: string;
      user_id: string;
      role: string;
    }>('/auth/firebase', {
      method: 'POST',
      body: JSON.stringify({ firebase_token: firebaseToken }),
    });
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('wosafe_access_token', data.access_token);
      localStorage.setItem('wosafe_refresh_token', data.refresh_token);
    }
    return data;
  }

  // Profile
  async getProfile() {
    return this.request<any>('/users/profile');
  }

  async updateProfile(profileData: any) {
    return this.request<any>('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async updateLocation(lat: number, lng: number, address?: string) {
    return this.request<any>('/users/location', {
      method: 'POST',
      body: JSON.stringify({ latitude: lat, longitude: lng, address }),
    });
  }

  // Contacts
  async getContacts() {
    return this.request<any[]>('/users/emergency-contacts');
  }

  async addContact(contact: any) {
    return this.request<any>('/users/emergency-contacts', {
      method: 'POST',
      body: JSON.stringify(contact),
    });
  }

  async removeContact(contactId: string) {
    return this.request<any>(`/users/emergency-contacts/${contactId}`, {
      method: 'DELETE',
    });
  }

  // Journeys
  async startJourney(journeyData: any) {
    return this.request<any>('/journeys/start', {
      method: 'POST',
      body: JSON.stringify(journeyData),
    });
  }

  async updateJourneyLocation(journeyId: string, locationData: any) {
    return this.request<any>(`/journeys/${journeyId}/location`, {
      method: 'POST',
      body: JSON.stringify(locationData),
    });
  }

  async pauseJourney(journeyId: string) {
    return this.request<any>(`/journeys/${journeyId}/pause`, {
      method: 'POST',
    });
  }

  async resumeJourney(journeyId: string) {
    return this.request<any>(`/journeys/${journeyId}/resume`, {
      method: 'POST',
    });
  }

  async stopJourney(journeyId: string) {
    return this.request<any>(`/journeys/${journeyId}/stop`, {
      method: 'POST',
    });
  }

  // Emergency / SOS
  async triggerSOS(lat: number, lng: number, address?: string, type = 'sos_button') {
    return this.request<any>('/emergency/sos', {
      method: 'POST',
      body: JSON.stringify({ latitude: lat, longitude: lng, address, trigger_type: type }),
    });
  }

  async resolveSOS(sessionId: string, notes: string) {
    return this.request<any>(`/emergency/resolve/${sessionId}`, {
      method: 'POST',
      body: JSON.stringify({ resolution_notes: notes }),
    });
  }

  // AI assistant
  async chatWithAI(message: string, conversationId?: string, context?: any) {
    return this.request<{
      response: string;
      conversation_id: string;
      emergency_detected: boolean;
      suggested_actions?: string[];
      suggested_prompts?: string[];
    }>('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId, context }),
    });
  }

  async getRiskAssessment(lat: number, lng: number) {
    return this.request<any>('/ai/risk-assessment', {
      method: 'POST',
      body: JSON.stringify({ latitude: lat, longitude: lng }),
    });
  }

  async getSuggestedPrompts() {
    return this.request<{ prompts: string[] }>('/ai/suggested-prompts');
  }

  // Incidents
  async getIncidents(page = 1, pageSize = 20) {
    return this.request<any>(`/incidents?page=${page}&page_size=${pageSize}`);
  }

  async createIncident(incidentData: any) {
    return this.request<any>('/incidents', {
      method: 'POST',
      body: JSON.stringify(incidentData),
    });
  }

  async voteIncident(incidentId: string) {
    return this.request<any>(`/incidents/${incidentId}/vote`, {
      method: 'POST',
    });
  }
}

export const api = new ApiClient();
