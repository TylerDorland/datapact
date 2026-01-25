import { apiClient } from './client';
import type { ComplianceCheck, ComplianceSummary } from '@/types/compliance';

export interface ComplianceListParams {
  check_type?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export const complianceApi = {
  getSummary: async (): Promise<ComplianceSummary[]> => {
    const { data } = await apiClient.get('/api/v1/compliance/summary');
    return data;
  },

  getContractCompliance: async (contractId: string): Promise<ComplianceSummary> => {
    const { data } = await apiClient.get(`/api/v1/contracts/${contractId}/compliance/summary`);
    return data;
  },

  getHistory: async (
    contractId: string,
    params?: ComplianceListParams
  ): Promise<ComplianceCheck[]> => {
    const { data } = await apiClient.get(`/api/v1/contracts/${contractId}/compliance`, {
      params,
    });
    return data.checks || data;
  },

  triggerCheck: async (contractId: string, checkType?: string): Promise<void> => {
    await apiClient.post(`/api/v1/contracts/${contractId}/validate`, {
      check_type: checkType,
    });
  },

  getLatestChecks: async (limit?: number): Promise<ComplianceCheck[]> => {
    const { data } = await apiClient.get('/api/v1/compliance/latest', {
      params: { limit },
    });
    return data;
  },
};
