import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { complianceApi } from '@/api/compliance';

export function useComplianceSummary() {
  return useQuery({
    queryKey: ['compliance', 'summary'],
    queryFn: () => complianceApi.getSummary(),
    refetchInterval: 60 * 1000, // Refresh every minute
  });
}

export function useContractCompliance(contractId: string) {
  return useQuery({
    queryKey: ['compliance', contractId],
    queryFn: () => complianceApi.getContractCompliance(contractId),
    enabled: !!contractId,
    refetchInterval: 60 * 1000,
  });
}

export function useComplianceHistory(contractId: string, checkType?: string) {
  return useQuery({
    queryKey: ['compliance', contractId, 'history', checkType],
    queryFn: () =>
      complianceApi.getHistory(contractId, { check_type: checkType, limit: 50 }),
    enabled: !!contractId,
  });
}

export function useLatestChecks(limit?: number) {
  return useQuery({
    queryKey: ['compliance', 'latest', limit],
    queryFn: () => complianceApi.getLatestChecks(limit),
    refetchInterval: 30 * 1000, // Refresh every 30 seconds
  });
}

export function useTriggerComplianceCheck() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ contractId, checkType }: { contractId: string; checkType?: string }) =>
      complianceApi.triggerCheck(contractId, checkType),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: ['compliance', contractId] });
      queryClient.invalidateQueries({ queryKey: ['compliance', 'summary'] });
    },
  });
}
