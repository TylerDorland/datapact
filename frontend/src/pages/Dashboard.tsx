import { Link } from 'react-router-dom';
import { FileText, ShieldCheck, AlertTriangle, Clock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useContracts } from '@/hooks/useContracts';
import { useComplianceSummary, useLatestChecks } from '@/hooks/useCompliance';
import { formatRelativeTime } from '@/lib/utils';

export function Dashboard() {
  const { data: contracts, isLoading: contractsLoading } = useContracts({ limit: 5 });
  const { data: compliance, isLoading: complianceLoading } = useComplianceSummary();
  const { data: latestChecks, isLoading: checksLoading } = useLatestChecks(5);

  const isLoading = contractsLoading || complianceLoading || checksLoading;

  const stats = [
    {
      title: 'Total Contracts',
      value: contracts?.total || 0,
      icon: FileText,
      color: 'text-blue-500',
    },
    {
      title: 'Compliant',
      value: compliance?.compliant || 0,
      icon: ShieldCheck,
      color: 'text-green-500',
    },
    {
      title: 'Violations',
      value: compliance?.violations || 0,
      icon: AlertTriangle,
      color: 'text-red-500',
    },
    {
      title: 'Pending Checks',
      value: compliance?.pending || 0,
      icon: Clock,
      color: 'text-yellow-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your data contracts and compliance status
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '...' : stat.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Contracts */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Contracts</CardTitle>
            <CardDescription>Latest contract updates</CardDescription>
          </CardHeader>
          <CardContent>
            {contractsLoading ? (
              <p className="text-muted-foreground">Loading...</p>
            ) : contracts?.items?.length ? (
              <div className="space-y-4">
                {contracts.items.map((contract) => (
                  <Link
                    key={contract.id}
                    to={`/contracts/${contract.id}`}
                    className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-accent"
                  >
                    <div>
                      <p className="font-medium">{contract.name}</p>
                      <p className="text-sm text-muted-foreground">
                        v{contract.version} • {contract.publisher?.team}
                      </p>
                    </div>
                    <Badge variant={contract.status === 'active' ? 'default' : 'secondary'}>
                      {contract.status}
                    </Badge>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No contracts found</p>
            )}
          </CardContent>
        </Card>

        {/* Latest Compliance Checks */}
        <Card>
          <CardHeader>
            <CardTitle>Latest Compliance Checks</CardTitle>
            <CardDescription>Recent validation results</CardDescription>
          </CardHeader>
          <CardContent>
            {checksLoading ? (
              <p className="text-muted-foreground">Loading...</p>
            ) : latestChecks?.length ? (
              <div className="space-y-4">
                {latestChecks.map((check) => (
                  <div
                    key={check.id}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div>
                      <p className="font-medium">{check.contract_name || check.contract_id}</p>
                      <p className="text-sm text-muted-foreground">
                        {check.check_type} • {formatRelativeTime(check.checked_at)}
                      </p>
                    </div>
                    <Badge
                      variant={
                        check.status === 'passed'
                          ? 'default'
                          : check.status === 'failed'
                          ? 'destructive'
                          : 'secondary'
                      }
                    >
                      {check.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No compliance checks yet</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
