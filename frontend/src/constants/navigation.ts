/**
 * Centralized navigation items and hierarchical sections for the application shell.
 * Used by Sidebar and MobileHeader.
 */
import {
  Activity,
  Database,
  LayoutDashboard,
  Sparkles,
  Users,
} from "lucide-react-native";
import type { LucideIcon } from "lucide-react-native";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  description: string;
  badge?: string;
}

export interface NavGroup {
  label: string;
  icon: LucideIcon;
  href?: string;
  defaultExpanded?: boolean;
  children: NavItem[];
}

export const PLATFORM_NAV_ITEMS: NavItem[] = [
  {
    label: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
    description: "Overview & scale metrics",
  },
  {
    label: "Database Explorer",
    href: "/database",
    icon: Database,
    description: "Browse 970+ tables",
  },
  {
    label: "Analysis",
    href: "/analysis",
    icon: Activity,
    description: "Profiling & classification runs",
  },
];

export const DAYLITE_NAV_GROUP: NavGroup = {
  label: "Day Lite",
  icon: Sparkles,
  href: "/daylite",
  defaultExpanded: true,
  children: [
    {
      label: "Dashboard",
      href: "/daylite",
      icon: LayoutDashboard,
      description: "KPI & Domain Metrics Hub",
    },
    {
      label: "DL Person",
      href: "/daylite/person",
      icon: Users,
      description: "Person Directory & Profiles",
      badge: "LIVE",
    },
  ],
};

/** Flat array for backward compatibility */
export const NAV_ITEMS: NavItem[] = [
  ...PLATFORM_NAV_ITEMS,
  ...DAYLITE_NAV_GROUP.children,
];
