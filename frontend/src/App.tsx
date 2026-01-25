import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Layout } from '@/components/layout';
import { Toaster } from '@/components/ui/toaster';
import { Dashboard } from '@/pages/Dashboard';
import { Contracts } from '@/pages/Contracts';
import { ContractDetail } from '@/pages/ContractDetail';
import { ContractCreate } from '@/pages/ContractCreate';
import { Dictionary } from '@/pages/Dictionary';
import { ERD } from '@/pages/ERD';
import { Compliance } from '@/pages/Compliance';
import { Notifications } from '@/pages/Notifications';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="contracts" element={<Contracts />} />
            <Route path="contracts/new" element={<ContractCreate />} />
            <Route path="contracts/:id" element={<ContractDetail />} />
            <Route path="dictionary" element={<Dictionary />} />
            <Route path="erd" element={<ERD />} />
            <Route path="compliance" element={<Compliance />} />
            <Route path="notifications" element={<Notifications />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
