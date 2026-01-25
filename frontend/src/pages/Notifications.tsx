import { useState } from 'react';
import {
  Bell,
  Check,
  CheckCheck,
  Settings,
  AlertTriangle,
  Info,
  AlertCircle,
  Filter,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  useNotifications,
  useNotificationStats,
  useMarkNotificationRead,
  useMarkAllNotificationsRead,
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from '@/hooks/useNotifications';
import { formatRelativeTime } from '@/lib/utils';
import { useToast } from '@/hooks/useToast';

// TODO: Replace with actual user email from auth context
const USER_EMAIL = 'user@example.com';

const severityIcons = {
  info: Info,
  warning: AlertTriangle,
  critical: AlertCircle,
};

const severityColors = {
  info: 'text-blue-500',
  warning: 'text-yellow-500',
  critical: 'text-red-500',
};

export function Notifications() {
  const { toast } = useToast();
  const [filter, setFilter] = useState<string>('all');
  const [showSettings, setShowSettings] = useState(false);

  const { data: notifications, isLoading } = useNotifications({
    email: USER_EMAIL,
    is_read: filter === 'unread' ? false : filter === 'read' ? true : undefined,
    limit: 50,
  });

  const { data: stats } = useNotificationStats(USER_EMAIL, 7);
  const { data: preferences } = useNotificationPreferences(USER_EMAIL);

  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();
  const updatePreferences = useUpdateNotificationPreferences();

  const handleMarkRead = async (id: string) => {
    try {
      await markRead.mutateAsync(id);
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to mark notification as read.',
        variant: 'destructive',
      });
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllRead.mutateAsync(USER_EMAIL);
      toast({
        title: 'Success',
        description: 'All notifications marked as read.',
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to mark all notifications as read.',
        variant: 'destructive',
      });
    }
  };

  const handleTogglePreference = async (key: string, value: boolean) => {
    try {
      await updatePreferences.mutateAsync({
        email: USER_EMAIL,
        preferences: { [key]: value },
      });
      toast({
        title: 'Preferences updated',
        description: 'Your notification preferences have been saved.',
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to update preferences.',
        variant: 'destructive',
      });
    }
  };

  const unreadCount = notifications?.items?.filter((n) => !n.is_read).length || 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-muted-foreground">
            Stay updated on your data contract activity
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
          {unreadCount > 0 && (
            <Button onClick={handleMarkAllRead} disabled={markAllRead.isPending}>
              <CheckCheck className="mr-2 h-4 w-4" />
              Mark All Read
            </Button>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total (7 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.total || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unread</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{unreadCount}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Critical</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-red-500">
              {stats?.by_severity?.critical || 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Warnings</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-yellow-500">
              {stats?.by_severity?.warning || 0}
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="notifications">
        <TabsList>
          <TabsTrigger value="notifications">
            <Bell className="mr-2 h-4 w-4" />
            Notifications
          </TabsTrigger>
          {showSettings && (
            <TabsTrigger value="settings">
              <Settings className="mr-2 h-4 w-4" />
              Preferences
            </TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="notifications" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Notifications</CardTitle>
                  <CardDescription>
                    {notifications?.items?.length || 0} notifications
                  </CardDescription>
                </div>
                <Select value={filter} onValueChange={setFilter}>
                  <SelectTrigger className="w-[150px]">
                    <Filter className="mr-2 h-4 w-4" />
                    <SelectValue placeholder="Filter" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="unread">Unread</SelectItem>
                    <SelectItem value="read">Read</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-10">
                  <p className="text-muted-foreground">Loading notifications...</p>
                </div>
              ) : !notifications?.items?.length ? (
                <div className="flex flex-col items-center justify-center py-10">
                  <Bell className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No notifications</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {notifications.items.map((notification) => {
                    const SeverityIcon =
                      severityIcons[notification.severity as keyof typeof severityIcons] || Info;
                    const severityColor =
                      severityColors[notification.severity as keyof typeof severityColors] ||
                      'text-muted-foreground';

                    return (
                      <div
                        key={notification.id}
                        className={`flex items-start gap-4 rounded-lg border p-4 transition-colors ${
                          notification.is_read ? 'bg-background' : 'bg-accent/50'
                        }`}
                      >
                        <div className={`mt-1 ${severityColor}`}>
                          <SeverityIcon className="h-5 w-5" />
                        </div>
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{notification.title}</p>
                            {!notification.is_read && (
                              <Badge variant="default" className="text-xs">
                                New
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {notification.message}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span>{formatRelativeTime(notification.created_at)}</span>
                            {notification.contract_id && (
                              <Badge variant="outline">
                                Contract: {notification.contract_name || notification.contract_id}
                              </Badge>
                            )}
                            <Badge variant="outline">{notification.channel}</Badge>
                          </div>
                        </div>
                        {!notification.is_read && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleMarkRead(notification.id)}
                            disabled={markRead.isPending}
                          >
                            <Check className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {showSettings && (
          <TabsContent value="settings" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>
                  Configure how and when you receive notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <h3 className="font-medium">Channels</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="email_enabled">Email Notifications</Label>
                        <p className="text-sm text-muted-foreground">
                          Receive notifications via email
                        </p>
                      </div>
                      <Switch
                        id="email_enabled"
                        checked={preferences?.email_enabled ?? true}
                        onCheckedChange={(checked) =>
                          handleTogglePreference('email_enabled', checked)
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="slack_enabled">Slack Notifications</Label>
                        <p className="text-sm text-muted-foreground">
                          Receive notifications in Slack
                        </p>
                      </div>
                      <Switch
                        id="slack_enabled"
                        checked={preferences?.slack_enabled ?? false}
                        onCheckedChange={(checked) =>
                          handleTogglePreference('slack_enabled', checked)
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="webhook_enabled">Webhook Notifications</Label>
                        <p className="text-sm text-muted-foreground">
                          Send notifications to a webhook URL
                        </p>
                      </div>
                      <Switch
                        id="webhook_enabled"
                        checked={preferences?.webhook_enabled ?? false}
                        onCheckedChange={(checked) =>
                          handleTogglePreference('webhook_enabled', checked)
                        }
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-medium">Event Types</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="compliance_alerts">Compliance Alerts</Label>
                        <p className="text-sm text-muted-foreground">
                          Notifications for compliance check results
                        </p>
                      </div>
                      <Switch
                        id="compliance_alerts"
                        checked={preferences?.compliance_alerts ?? true}
                        onCheckedChange={(checked) =>
                          handleTogglePreference('compliance_alerts', checked)
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="contract_updates">Contract Updates</Label>
                        <p className="text-sm text-muted-foreground">
                          Notifications when contracts are modified
                        </p>
                      </div>
                      <Switch
                        id="contract_updates"
                        checked={preferences?.contract_updates ?? true}
                        onCheckedChange={(checked) =>
                          handleTogglePreference('contract_updates', checked)
                        }
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="subscriber_changes">Subscriber Changes</Label>
                        <p className="text-sm text-muted-foreground">
                          Notifications for subscription activity
                        </p>
                      </div>
                      <Switch
                        id="subscriber_changes"
                        checked={preferences?.subscriber_changes ?? true}
                        onCheckedChange={(checked) =>
                          handleTogglePreference('subscriber_changes', checked)
                        }
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
}
