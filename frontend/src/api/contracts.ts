import { apiClient } from './client';
import type { Contract, ContractVersion } from '@/types/contract';

export interface ContractListParams {
  skip?: number;
  limit?: number;
  status?: string;
  publisher_team?: string;
  tag?: string;
}

export interface ContractListResponse {
  contracts: Contract[];
  total: number;
  skip: number;
  limit: number;
}

export const contractsApi = {
  list: async (params: ContractListParams = {}): Promise<ContractListResponse> => {
    const { data } = await apiClient.get('/api/v1/contracts', { params });
    return data;
  },

  get: async (id: string): Promise<Contract> => {
    const { data } = await apiClient.get(`/api/v1/contracts/${id}`);
    return data;
  },

  getByName: async (name: string): Promise<Contract> => {
    const { data } = await apiClient.get(`/api/v1/contracts/name/${name}`);
    return data;
  },

  create: async (contract: Partial<Contract>): Promise<Contract> => {
    const { data } = await apiClient.post('/api/v1/contracts', contract);
    return data;
  },

  update: async (id: string, contract: Partial<Contract>): Promise<Contract> => {
    const { data } = await apiClient.put(`/api/v1/contracts/${id}`, contract);
    return data;
  },

  deprecate: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/contracts/${id}`);
  },

  getVersions: async (id: string): Promise<ContractVersion[]> => {
    const { data } = await apiClient.get(`/api/v1/contracts/${id}/versions`);
    return data.versions;
  },

  subscribe: async (
    id: string,
    subscription: {
      team: string;
      use_case?: string;
      fields_used?: string[];
      contact_email?: string;
    }
  ): Promise<void> => {
    await apiClient.post(`/api/v1/contracts/${id}/subscribers`, subscription);
  },

  unsubscribe: async (id: string, subscriberId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/contracts/${id}/subscribers/${subscriberId}`);
  },
};
