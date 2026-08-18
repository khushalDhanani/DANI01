/**
 * Centralized navigation items and hierarchical sections for the application shell.
 * Used by Sidebar and MobileHeader.
 */
import {
  Activity,
  Banknote,
  Building2,
  CalendarCheck,
  Code2,
  Database,
  LayoutDashboard,
  Mail,
  ShieldAlert,
  ShieldCheck,
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
  id: string;
  label: string;
  icon: LucideIcon;
  href?: string;
  defaultExpanded?: boolean;
  children: NavItem[];
}

export interface NavSection {
  id: string;
  title: string;
  items?: NavItem[];
  groups?: NavGroup[];
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
  id: "daylite",
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
    {
      label: "PR Campaign",
      href: "/daylite/campaign",
      icon: Users,
      description: "PR Campaign",
    },
  ],
};

export const ENTERPRISE_NAV_GROUP: NavGroup = {
  id: "workforce",
  label: "Workforce",
  icon: Users,
  href: "/modules/employee",
  defaultExpanded: true,
  children: [
    {
      label: "Employee Intelligence",
      href: "/modules/employee",
      icon: Users,
      description: "Workforce, Hierarchy & Data Quality",
      badge: "LIVE",
    },
    {
      label: "Organization Structure",
      href: "/modules/organization",
      icon: Building2,
      description: "Companies, Sites, Depts & Hierarchy",
      badge: "LIVE",
    },
    {
      label: "Contact & Communication",
      href: "/modules/contact",
      icon: Mail,
      description: "Emails, Phones, ICE & Multi-channel Contacts",
      badge: "LIVE",
    },
    {
      label: "User & Security",
      href: "/modules/security",
      icon: ShieldCheck,
      description: "Logins, Roles, RBAC Rights & Security Audit",
      badge: "LIVE",
    },
    {
      label: "Payroll & Salary",
      href: "/modules/payroll",
      icon: Banknote,
      description: "Monthly Registers, Earnings, Deductions & Bank Payslips",
      badge: "LIVE",
    },
    {
      label: "Cross-Domain Data Quality",
      href: "/modules/cross_domain_dq",
      icon: ShieldAlert,
      description: "Multi-table consistency validation across all 8 employee domains",
      badge: "15 Rules",
    },
    {
      label: "SQL & SP Logic Analyzer",
      href: "/modules/procedure_logic",
      icon: Code2,
      description: "Stored procedure logic predicate auditor & conflict detector",
      badge: "SP Audit",
    },
  ],
};

export const EMPLOYEE_ANALYTICS_NAV_GROUP: NavGroup = {
  id: "employee_analytics",
  label: "Employee Analytics",
  icon: CalendarCheck,
  href: "/modules/attendance",
  defaultExpanded: true,
  children: [
    {
      label: "Attendance & Leave Analysis",
      href: "/modules/attendance",
      icon: CalendarCheck,
      description: "Punches, Shifts, Overtime, Leave Applications & 14 Audit Rules",
      badge: "LIVE",
    },
    {
      label: "Department Summary",
      href: "/modules/attendance/department-summary",
      icon: Building2,
      description: "Department-wise headcount, attendance volume, late ratio & OT hours",
      badge: "Master",
    },
  ],
};

export const NAV_SECTIONS: NavSection[] = [
  {
    id: "platform",
    title: "Database Platform",
    items: PLATFORM_NAV_ITEMS,
  },
  {
    id: "enterprise",
    title: "Enterprise Modules",
    groups: [ENTERPRISE_NAV_GROUP, EMPLOYEE_ANALYTICS_NAV_GROUP, DAYLITE_NAV_GROUP],
  },
];

/** Flat array for backward compatibility */
export const NAV_ITEMS: NavItem[] = [
  ...PLATFORM_NAV_ITEMS,
  ...ENTERPRISE_NAV_GROUP.children,
  ...EMPLOYEE_ANALYTICS_NAV_GROUP.children,
  ...DAYLITE_NAV_GROUP.children,
];
