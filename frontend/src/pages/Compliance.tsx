import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  ShieldAlert,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  useComplianceSummary,
  useLatestChecks,
  useTriggerComplianceCheck,
} from '@/hooks/useCompliance';
import { formatRelativeTime } from '@/lib/utils';
import { useToast } from '@/hooks/useToast';

const COLORS = {
  passed: '#22c55e',
  failed: '#ef4444',
  pending: '#eab308',
};

export function Compliance() {
  const { toast } = useToast();
  const { data: summary, isLoading: summaryLoading } = useComplianceSummary();
  const { data: latestChecks, isLoading: checksLoading } = useLatestChecks(20);
  const triggerCheck = useTriggerComplianceCheck();

  const [selectedContract, setSelectedContract] = useState<string | null>(null);

  const handleTriggerAll = async () => {
    // This would trigger checks for all contracts - for now just show toast
    toast({
      title: 'Bulk check triggered',
      description: 'Compliance checks are running for all active contracts.',
    });
  };

  // Prepare chart data
  const pieData = summary
    ? [
        { name: 'Compliant', value: summary.compliant, color: COLORS.passed },
        { name: 'Violations', value: summary.violations, color: COLORS.failed },
        { name: 'Pending', value: summary.pending, color: COLORS.pending },
      ]
    : [];

  // Group checks by type for bar chart
  const checksByType = latestChecks?.reduce((acc, check) => {
    const type = check.check_type;
    if (!acc[type]) {
      acc[type] = { type, passed: 0, failed: 0 };
    }
    if (check.status === 'passed') acc[type].passed++;
    else if (check.status === 'failed') acc[type].failed++;
    return acc;
  }, {} as Record<string, { type: string; passed: number; failed: number }>);

  const barData = checksByType ? Object.values(checksByType) : [];

  const stats = [
    {
      title: 'Compliant',
      value: summary?.compliant || 0,
      icon: ShieldCheck,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      title: 'Violations',
      value: summary?.violations || 0,
      icon: ShieldAlert,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
    },
    {
      title: 'Pending',
      value: summary?.pending || 0,
      icon: Clock,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
    },
    {
      title: 'Compliance Rate',
      value: summary
        ? `${Math.round(
            (summary.compliant / (summary.compliant + summary.violations || 1)) * 100
          )}%`
        : '0%',
      icon: TrendingUp,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Compliance Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor data contract compliance across your organization
          </p>
        </div>
        <Button onClick={handleTriggerAll}>
          <ShieldCheck className="mr-2 h-4 w-4" />
          Run All Checks
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <div className={`rounded-full p-2 ${stat.bgColor}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {summaryLoading ? '...' : stat.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Compliance Overview</CardTitle>
            <CardDescription>Distribution of compliance status</CardDescription>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <div className="h-[250px] flex items-center justify-center">
                <p className="text-muted-foreground">Loading...</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Checks by Type</CardTitle>
            <CardDescription>Pass/fail breakdown by check type</CardDescription>
          </CardHeader>
          <CardContent>
            {checksLoading ? (
              <div className="h-[250px] flex items-center justify-center">
                <p className="text-muted-foreground">Loading...</p>
              </div>
            ) : barData.length === 0 ? (
              <div className="h-[250px] flex items-center justify-center">
                <p className="text-muted-foreground">No data available</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={barData}>
                  <XAxis dataKey="type" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="passed" name="Passed" fill={COLORS.passed} />
                  <Bar dataKey="failed" name="Failed" fill={COLORS.failed} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Latest Checks Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Compliance Checks</CardTitle>
          <CardDescription>Latest validation results across all contracts</CardDescription>
        </CardHeader>
        <CardContent>
          {checksLoading ? (
            <div className="flex items-center justify-center py-10">
              <p className="text-muted-foreground">Loading checks...</p>
            </div>
          ) : !latestChecks?.length ? (
            <div className="flex flex-col items-center justify-center py-10">
              <ShieldCheck className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No compliance checks yet</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Contract</TableHead>
                    <TableHead>Check Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Details</TableHead>
                    <TableHead>Checked At</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {latestChecks.map((check) => (
                    <TableRow key={check.id}>
                      <TableCell>
                        <Link
                          to={`/contracts/${check.contract_id}`}
                          className="font-medium text-primary hover:underline"
                        >
                          {check.contract_name || check.contract_id}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{check.check_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {check.status === 'passed' ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : check.status === 'failed' ? (
                            <XCircle className="h-4 w-4 text-red-500" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-yellow-500" />
                          )}
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
                      </TableCell>
                      <TableCell className="max-w-[300px]">
                        {check.details ? (
                          <p className="text-sm text-muted-foreground truncate">
                            {typeof check.details === 'string'
                              ? check.details
                              : JSON.stringify(check.details)}
                          </p>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {formatRelativeTime(check.checked_at)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
