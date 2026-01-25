import { useLocation } from 'react-router-dom';
import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNotifications } from '@/hooks/useNotifications';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/contracts': 'Contracts',
  '/dictionary': 'Data Dictionary',
  '/erd': 'Entity Relationship Diagram',
  '/compliance': 'Compliance Dashboard',
  '/notifications': 'Notifications',
};

export function Header() {
  const location = useLocation();
  const basePath = '/' + location.pathname.split('/')[1];
  const title = pageTitles[basePath] || 'DataPact';

  // TODO: Replace with actual user email from auth context
  const userEmail = 'user@example.com';
  const { data: notifications } = useNotifications({
    email: userEmail,
    is_read: false,
    limit: 10,
  });

  const unreadCount = notifications?.items?.length || 0;

  return (
    <header className="flex h-16 items-center justify-between border-b bg-card px-6">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-xs text-destructive-foreground">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </Button>
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
            <span className="text-sm font-medium text-primary">U</span>
          </div>
          <span className="text-sm font-medium">User</span>
        </div>
      </div>
    </header>
  );
}
