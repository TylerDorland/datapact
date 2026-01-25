import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { contractsApi, type ContractListParams } from '@/api/contracts';
import type { Contract } from '@/types/contract';

export function useContracts(params: ContractListParams = {}) {
  return useQuery({
    queryKey: ['contracts', params],
    queryFn: () => contractsApi.list(params),
  });
}

export function useContract(id: string) {
  return useQuery({
    queryKey: ['contracts', id],
    queryFn: () => contractsApi.get(id),
    enabled: !!id,
  });
}

export function useContractByName(name: string) {
  return useQuery({
    queryKey: ['contracts', 'name', name],
    queryFn: () => contractsApi.getByName(name),
    enabled: !!name,
  });
}

export function useContractVersions(id: string) {
  return useQuery({
    queryKey: ['contracts', id, 'versions'],
    queryFn: () => contractsApi.getVersions(id),
    enabled: !!id,
  });
}

export function useCreateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contract: Partial<Contract>) => contractsApi.create(contract),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

export function useUpdateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, contract }: { id: string; contract: Partial<Contract> }) =>
      contractsApi.update(id, contract),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['contracts', id] });
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

export function useDeprecateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => contractsApi.deprecate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

export function useSubscribeToContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      contractId,
      subscription,
    }: {
      contractId: string;
      subscription: {
        team: string;
        use_case?: string;
        fields_used?: string[];
        contact_email?: string;
      };
    }) => contractsApi.subscribe(contractId, subscription),
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: ['contracts', contractId] });
    },
  });
}
