import { useQuery } from '@tanstack/react-query';
import { dictionaryApi, type SearchParams } from '@/api/dictionary';

export function useDictionary() {
  return useQuery({
    queryKey: ['dictionary'],
    queryFn: () => dictionaryApi.getFull(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useDictionarySearch(
  query: string,
  filters?: Omit<SearchParams, 'q'>
) {
  return useQuery({
    queryKey: ['dictionary', 'search', query, filters],
    queryFn: () => dictionaryApi.search({ q: query, ...filters }),
    enabled: query.length > 0,
  });
}

export function useSuggestions(prefix: string, limit?: number) {
  return useQuery({
    queryKey: ['dictionary', 'suggest', prefix, limit],
    queryFn: () => dictionaryApi.suggest(prefix, limit),
    enabled: prefix.length >= 2,
  });
}

export function useFieldLineage(dataset: string, field: string) {
  return useQuery({
    queryKey: ['dictionary', 'lineage', dataset, field],
    queryFn: () => dictionaryApi.getFieldLineage(dataset, field),
    enabled: !!dataset && !!field,
  });
}

export function useERD(team?: string) {
  return useQuery({
    queryKey: ['erd', team],
    queryFn: () => dictionaryApi.getERD({ team }),
    staleTime: 5 * 60 * 1000,
  });
}

export function useERDMermaid(team?: string) {
  return useQuery({
    queryKey: ['erd', 'mermaid', team],
    queryFn: () => dictionaryApi.getERDMermaid(team),
    staleTime: 5 * 60 * 1000,
  });
}
