import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  FileText,
  BookOpen,
  GitBranch,
  ShieldCheck,
  Bell,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/contracts', icon: FileText, label: 'Contracts' },
  { to: '/dictionary', icon: BookOpen, label: 'Dictionary' },
  { to: '/erd', icon: GitBranch, label: 'ERD' },
  { to: '/compliance', icon: ShieldCheck, label: 'Compliance' },
  { to: '/notifications', icon: Bell, label: 'Notifications' },
];

export function Sidebar() {
  return (
    <aside className="flex w-64 flex-col border-r bg-card">
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold text-primary">DataPact</h1>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t p-4">
        <p className="text-xs text-muted-foreground">
          DataPact v1.0.0
        </p>
      </div>
    </aside>
  );
}
