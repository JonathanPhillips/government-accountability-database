import axios from 'axios';
import type {
  PaginatedResponse,
  IncidentListItem,
  IncidentDetail,
  IncidentFilters,
  Category,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Incidents API
export const incidentsApi = {
  list: async (filters?: IncidentFilters): Promise<PaginatedResponse<IncidentListItem>> => {
    const response = await apiClient.get<PaginatedResponse<IncidentListItem>>('/incidents/', {
      params: filters,
    });
    return response.data;
  },

  get: async (id: string): Promise<IncidentDetail> => {
    const response = await apiClient.get<IncidentDetail>(`/incidents/${id}`);
    return response.data;
  },

  create: async (data: Partial<IncidentDetail>): Promise<IncidentDetail> => {
    const response = await apiClient.post<IncidentDetail>('/incidents/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<IncidentDetail>): Promise<IncidentDetail> => {
    const response = await apiClient.put<IncidentDetail>(`/incidents/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/incidents/${id}`);
  },
};

// Categories API
export const categoriesApi = {
  list: async (): Promise<PaginatedResponse<Category>> => {
    const response = await apiClient.get<PaginatedResponse<Category>>('/categories/', {
      params: { limit: 100 },
    });
    return response.data;
  },

  get: async (id: string): Promise<Category> => {
    const response = await apiClient.get<Category>(`/categories/${id}`);
    return response.data;
  },
};

export default apiClient;
