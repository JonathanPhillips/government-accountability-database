import axios from 'axios';
import type {
  PaginatedResponse,
  IncidentListItem,
  IncidentDetail,
  IncidentFilters,
  Category,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL !== undefined ? import.meta.env.VITE_API_URL : 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses - redirect to login
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Incidents API
export const incidentsApi = {
  list: async (filters?: IncidentFilters): Promise<PaginatedResponse<IncidentListItem>> => {
    const response = await apiClient.get<PaginatedResponse<IncidentListItem>>('/api/incidents/', {
      params: filters,
    });
    return response.data;
  },

  get: async (id: string): Promise<IncidentDetail> => {
    const response = await apiClient.get<IncidentDetail>(`/api/incidents/${id}`);
    return response.data;
  },

  create: async (data: Partial<IncidentDetail>): Promise<IncidentDetail> => {
    const response = await apiClient.post<IncidentDetail>('/api/incidents/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<IncidentDetail>): Promise<IncidentDetail> => {
    const response = await apiClient.put<IncidentDetail>(`/api/incidents/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/incidents/${id}`);
  },
};

// Categories API
export const categoriesApi = {
  list: async (): Promise<PaginatedResponse<Category>> => {
    const response = await apiClient.get<PaginatedResponse<Category>>('/api/categories/', {
      params: { limit: 100 },
    });
    return response.data;
  },

  get: async (id: string): Promise<Category> => {
    const response = await apiClient.get<Category>(`/api/categories/${id}`);
    return response.data;
  },
};

export default apiClient;
