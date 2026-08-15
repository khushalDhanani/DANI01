import React, { useState, useEffect, useMemo } from "react";
import {
  FlatList,
  Pressable,
  Text,
  TextInput,
  View,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import type { Href } from "expo-router";
import {
  AlertCircle,
  ArrowLeft,
  Building2,
  CalendarOff,
  CalendarX,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  Clock,
  Compass,
  Copy,
  FileSpreadsheet,
  FileText,
  FileWarning,
  Globe,
  Layers,
  Mail,
  MailWarning,
  MapPinOff,
  NavigationOff,
  Phone,
  PhoneOff,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldX,
  Sliders,
  SortAsc,
  SortDesc,
  User,
  UserCheck,
  UserX,
  X,
} from "lucide-react-native";
import { useContactQualityIssues } from "@/hooks/useModules";
import { exportContactQualityIssues } from "@/api/modules.api";
import { PaginationControls } from "@/components/tables/PaginationControls";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { THEME_COLORS } from "@/constants/theme";
import type { ContactQualityIssueItem } from "@/types/modules.types";

type QualityDimension = "ALL" | "CONTACTS" | "ADDRESSES" | "INTEGRITY" | "GOVERNANCE";

interface IssueTabConfig {
  id: string;
  label: string;
  category: "CRITICAL" | "WARNING" | "INFO";
  dimension: "CONTACTS" | "ADDRESSES" | "INTEGRITY" | "GOVERNANCE";
  icon: React.ReactNode;
  description: string;
}

export const ALL_ISSUE_TABS: IssueTabConfig[] = [
  // ── Dimension 1: Contacts & Duplicates ─────────────
  {
    id: "MISSING_EMAIL",
    label: "Missing Email",
    category: "WARNING",
    dimension: "CONTACTS",
    icon: <MailWarning size={13} color={THEME_COLORS.warningIcon} />,
    description: "Persons without any registered email address in DLPersonPhoneEmailURLDet",
  },
  {
    id: "MISSING_PHONE",
    label: "Missing Phone",
    category: "WARNING",
    dimension: "CONTACTS",
    icon: <PhoneOff size={13} color={THEME_COLORS.warningIcon} />,
    description: "Persons without any registered phone number in DLPersonPhoneEmailURLDet",
  },
  {
    id: "INVALID_EMAIL",
    label: "Invalid Email",
    category: "CRITICAL",
    dimension: "CONTACTS",
    icon: <Mail size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Malformed email addresses with illegal syntax, spaces, or bad domains",
  },
  {
    id: "INVALID_PHONE",
    label: "Invalid Phone / Extension",
    category: "CRITICAL",
    dimension: "CONTACTS",
    icon: <Phone size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Phone numbers must be 7-15 digits; Extension numbers must be exactly 4 numeric digits",
  },
  {
    id: "DUPLICATE_EMAIL_CROSS",
    label: "Shared Email",
    category: "WARNING",
    dimension: "CONTACTS",
    icon: <Copy size={13} color={THEME_COLORS.companyIcon} />,
    description: "Identical email address registered across multiple distinct Person entities",
  },
  {
    id: "DUPLICATE_PHONE_CROSS",
    label: "Shared Phone",
    category: "WARNING",
    dimension: "CONTACTS",
    icon: <Copy size={13} color={THEME_COLORS.companyIcon} />,
    description: "Identical phone number registered across multiple distinct Person entities",
  },
  {
    id: "DUPLICATE_EMAIL_SAME",
    label: "Duplicate Email (Self)",
    category: "WARNING",
    dimension: "CONTACTS",
    icon: <UserCheck size={13} color={THEME_COLORS.primaryIcon} />,
    description: "Duplicate identical email records entered more than once for the same Person",
  },
  {
    id: "DUPLICATE_PHONE_SAME",
    label: "Duplicate Phone (Self)",
    category: "WARNING",
    dimension: "CONTACTS",
    icon: <UserCheck size={13} color={THEME_COLORS.primaryIcon} />,
    description: "Duplicate identical phone records entered more than once for the same Person",
  },
  {
    id: "UNVERIFIED_CONTACT",
    label: "Unverified Contacts",
    category: "INFO",
    dimension: "CONTACTS",
    icon: <ShieldAlert size={13} color={THEME_COLORS.imIcon} />,
    description: "Contact channels lacking verified flag status (IsVerified = 0 or NULL)",
  },
  {
    id: "INVALID_URL",
    label: "Invalid URLs",
    category: "WARNING",
    dimension: "CONTACTS",
    icon: <Globe size={13} color={THEME_COLORS.warningIcon} />,
    description: "Web URLs lacking proper URI scheme (http://, https://, or www.)",
  },
  {
    id: "MULTIPLE_PRIMARY",
    label: "Multiple Primary Contacts",
    category: "CRITICAL",
    dimension: "CONTACTS",
    icon: <Layers size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Persons with conflicting primary contact flags (more than 1 primary contact)",
  },
  {
    id: "PRIMARY_INACTIVE",
    label: "Primary Inactive",
    category: "CRITICAL",
    dimension: "CONTACTS",
    icon: <ShieldX size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Designated Primary contact record is disabled or marked inactive",
  },

  // ── Dimension 2: Address & Locations ──────────────
  {
    id: "MISSING_POSTAL_CODE",
    label: "Missing Postal Code",
    category: "WARNING",
    dimension: "ADDRESSES",
    icon: <MapPinOff size={13} color={THEME_COLORS.warningIcon} />,
    description: "Address records without a postal / PIN code",
  },
  {
    id: "INVALID_PIN_CODE_FORMAT",
    label: "Invalid PIN Format",
    category: "CRITICAL",
    dimension: "ADDRESSES",
    icon: <MapPinOff size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Postal codes containing non-numeric characters or non-standard length",
  },
  {
    id: "STREET_WITHOUT_CITY",
    label: "Street Without City",
    category: "WARNING",
    dimension: "ADDRESSES",
    icon: <Compass size={13} color={THEME_COLORS.warningIcon} />,
    description: "Street address is populated but city name is blank or missing",
  },
  {
    id: "CITY_WITHOUT_STATE",
    label: "City Without State",
    category: "WARNING",
    dimension: "ADDRESSES",
    icon: <Compass size={13} color={THEME_COLORS.warningIcon} />,
    description: "City address is populated but state region name is missing",
  },
  {
    id: "MISSING_GEOCODES",
    label: "Missing Geocodes",
    category: "INFO",
    dimension: "ADDRESSES",
    icon: <NavigationOff size={13} color={THEME_COLORS.imIcon} />,
    description: "Address records lacking Latitude / Longitude coordinate telemetry",
  },
  {
    id: "DUPLICATE_ADDRESSES_SAME_PERSON",
    label: "Duplicate Address (Self)",
    category: "WARNING",
    dimension: "ADDRESSES",
    icon: <Copy size={13} color={THEME_COLORS.warningIcon} />,
    description: "Identical street and city address entered multiple times for one Person",
  },

  // ── Dimension 3: Profile & Chronological Integrity ─
  {
    id: "ANNIVERSARY_BEFORE_BIRTH",
    label: "Anniversary Before Birth",
    category: "CRITICAL",
    dimension: "INTEGRITY",
    icon: <CalendarX size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Anniversary date is earlier than birth date (chronological corruption)",
  },
  {
    id: "INVALID_BIRTH_DATE",
    label: "Invalid Birth Date",
    category: "CRITICAL",
    dimension: "INTEGRITY",
    icon: <CalendarOff size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Birth date is set in the future or before 1900-01-01",
  },
  {
    id: "BIRTH_DATE_DEFAULT_OR_ANCIENT",
    label: "Dummy / Ancient DOB",
    category: "WARNING",
    dimension: "INTEGRITY",
    icon: <CalendarOff size={13} color={THEME_COLORS.warningIcon} />,
    description: "Birth date is set to dummy 1900-01-01 or age exceeds 100 years",
  },
  {
    id: "SUSPICIOUS_DUMMY_NAMES",
    label: "Suspicious Test Names",
    category: "WARNING",
    dimension: "INTEGRITY",
    icon: <UserX size={13} color={THEME_COLORS.warningIcon} />,
    description: "Placeholder test names detected (e.g. test, admin, dummy, asdf, xyz)",
  },
  {
    id: "MISSING_LAST_NAME",
    label: "Missing Last Name",
    category: "WARNING",
    dimension: "INTEGRITY",
    icon: <FileWarning size={13} color={THEME_COLORS.warningIcon} />,
    description: "Person record has first name populated but missing surname / last name",
  },

  // ── Dimension 4: Governance, Employment & Links ───
  {
    id: "STATUS_ACTIVE_AND_DELETED",
    label: "Active & Deleted Conflict",
    category: "CRITICAL",
    dimension: "GOVERNANCE",
    icon: <ShieldAlert size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Conflicting record status: marked both Active=1 and Deleted=1 simultaneously",
  },
  {
    id: "ACTIVE_EMP_MISSING_TITLE",
    label: "Employee Missing Title",
    category: "WARNING",
    dimension: "GOVERNANCE",
    icon: <FileWarning size={13} color={THEME_COLORS.warningIcon} />,
    description: "Active employee (EmpID present) has no job title designation defined",
  },
  {
    id: "INACTIVE_WITH_ACTIVE_EMPID",
    label: "Inactive with EmpID",
    category: "INFO",
    dimension: "GOVERNANCE",
    icon: <AlertCircle size={13} color={THEME_COLORS.textMuted} />,
    description: "Inactive person records still retaining an active employee ID",
  },
  {
    id: "STALE_TEMP_PERSONS",
    label: "Stale Temp Persons (>90d)",
    category: "WARNING",
    dimension: "GOVERNANCE",
    icon: <Clock size={13} color={THEME_COLORS.warningIcon} />,
    description: "Temporary person records created more than 90 days ago without finalization",
  },
  {
    id: "BLACKLIST_UNAPPROVED",
    label: "Unapproved Blacklist",
    category: "CRITICAL",
    dimension: "GOVERNANCE",
    icon: <ShieldAlert size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Blacklist flag is active without mandatory HOD authorization approval",
  },
  {
    id: "BLACKLIST_MISSING_DETAILS",
    label: "Blacklist Missing Details",
    category: "CRITICAL",
    dimension: "GOVERNANCE",
    icon: <FileWarning size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Blacklisted person record is missing blacklist timestamp or reason category",
  },
  {
    id: "ORPHAN_COMPANY_LINK",
    label: "Orphan Company Link",
    category: "CRITICAL",
    dimension: "GOVERNANCE",
    icon: <Building2 size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Company affiliation link references a non-existent company ID in DLCompanyMst",
  },
  {
    id: "DUPLICATE_COMPANY_LINKS",
    label: "Duplicate Company Links",
    category: "WARNING",
    dimension: "GOVERNANCE",
    icon: <Copy size={13} color={THEME_COLORS.warningIcon} />,
    description: "Same company entity is linked multiple times to the same Person",
  },
  {
    id: "COMPANY_MISSING_ROLE",
    label: "Company Missing Role",
    category: "WARNING",
    dimension: "GOVERNANCE",
    icon: <Building2 size={13} color={THEME_COLORS.warningIcon} />,
    description: "Company affiliation link is missing designation role (CompPersonRoleID = 0/NULL)",
  },
  {
    id: "EXTRA_FIELD_ORPHAN_ID",
    label: "Orphan Extra Field",
    category: "CRITICAL",
    dimension: "GOVERNANCE",
    icon: <Sliders size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Custom field value references an invalid or deleted ExtraField schema ID",
  },
  {
    id: "DUPLICATE_EXTRA_FIELDS",
    label: "Duplicate Extra Fields",
    category: "WARNING",
    dimension: "GOVERNANCE",
    icon: <Sliders size={13} color={THEME_COLORS.warningIcon} />,
    description: "Duplicate custom field value entries recorded under the same Person",
  },
  {
    id: "DELETED_MISSING_TIMESTAMP",
    label: "Deleted Without Timestamp",
    category: "WARNING",
    dimension: "GOVERNANCE",
    icon: <Clock size={13} color={THEME_COLORS.warningIcon} />,
    description: "Record is flagged as deleted but has no deletion timestamp (PersonDelDt is NULL)",
  },
  {
    id: "AUDIT_DEL_BEFORE_ENT",
    label: "Deletion Before Creation",
    category: "CRITICAL",
    dimension: "GOVERNANCE",
    icon: <Clock size={13} color={THEME_COLORS.dangerIcon} />,
    description: "Deletion timestamp is earlier than creation timestamp (audit log corruption)",
  },
  {
    id: "SYNC_ZIMBRA_MISSING_ID",
    label: "Broken Zimbra Sync",
    category: "WARNING",
    dimension: "GOVERNANCE",
    icon: <RefreshCw size={13} color={THEME_COLORS.warningIcon} />,
    description: "Sync is enabled on record but Zimbra Contact ID is missing or null",
  },
];

export const ContactQualityIssuesView: React.FC = () => {
  const router = useRouter();
  const params = useLocalSearchParams<{ issue?: string }>();

  const [activeIssue, setActiveIssue] = useState<string>(
    params.issue?.toUpperCase() || "INVALID_EMAIL"
  );
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [activeDimension, setActiveDimension] = useState<QualityDimension>("ALL");
  const [sortBy, setSortBy] = useState<string>("PersonID");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState<number>(0);
  const [isExporting, setIsExporting] = useState<"xlsx" | "csv" | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});

  const toggleGroup = (key: string) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const limit = 25;

  // Debounce search by 350ms and enforce min 2 chars (or empty string to reset)
  useEffect(() => {
    const handler = setTimeout(() => {
      const trimmed = search.trim();
      if (trimmed.length === 0 || trimmed.length >= 2) {
        setDebouncedSearch(trimmed);
      }
    }, 350);

    return () => clearTimeout(handler);
  }, [search]);

  // Synchronize when route issue parameter changes
  useEffect(() => {
    if (params.issue) {
      const paramIssue = params.issue.toUpperCase();
      setActiveIssue(paramIssue);
      setPage(0);
      setExpandedGroups({});

      const found = ALL_ISSUE_TABS.find((t) => t.id === paramIssue);
      if (found) {
        setActiveDimension(found.dimension);
      }
    }
  }, [params.issue]);

  const { data, isLoading, isError, error, refetch, isFetching } = useContactQualityIssues({
    issue: activeIssue,
    search: debouncedSearch || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
    limit,
    offset: page * limit,
  });

  const activeTabConfig =
    ALL_ISSUE_TABS.find((t) => t.id === activeIssue) || ALL_ISSUE_TABS[0];

  const filteredTabs = useMemo(() => {
    if (activeDimension === "ALL") return ALL_ISSUE_TABS;
    return ALL_ISSUE_TABS.filter((t) => t.dimension === activeDimension);
  }, [activeDimension]);

  const handleDimensionChange = (dim: QualityDimension) => {
    setActiveDimension(dim);
    setPage(0);
    setExpandedGroups({});

    if (dim !== "ALL") {
      const matchingIssues = ALL_ISSUE_TABS.filter((t) => t.dimension === dim);
      const isCurrentInDim = matchingIssues.some((t) => t.id === activeIssue);
      if (!isCurrentInDim && matchingIssues.length > 0) {
        const firstIssue = matchingIssues[0].id;
        setActiveIssue(firstIssue);
        router.setParams({ issue: firstIssue });
      }
    }
  };

  const handleTabChange = (issueId: string) => {
    setActiveIssue(issueId);
    setPage(0);
    setExpandedGroups({});
    router.setParams({ issue: issueId });
  };

  const handleSearchChange = (text: string) => {
    setSearch(text);
    setPage(0);
    setExpandedGroups({});
  };

  const toggleSortOrder = () => {
    setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    setPage(0);
  };

  const handleExport = async (format: "xlsx" | "csv") => {
    try {
      setIsExporting(format);
      setExportError(null);
      await exportContactQualityIssues({
        issue: activeIssue,
        format,
        search: debouncedSearch || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to download export file.";
      setExportError(msg);
    } finally {
      setIsExporting(null);
    }
  };

  const severityHeaderStyle = {
    CRITICAL: "bg-rose-950/70 border-rose-800/80 text-rose-300",
    WARNING: "bg-amber-950/70 border-amber-800/80 text-amber-300",
    INFO: "bg-blue-950/70 border-blue-800/80 text-blue-300",
  }[activeTabConfig.category];

  const isGroupRule = data?.count_unit === "DUPLICATE_GROUP";
  const hasData = isGroupRule
    ? (data?.groups && data.groups.length > 0)
    : (data?.items && data.items.length > 0);

  return (
    <View style={{ flex: 1, height: "100%", minHeight: 0 }} className="gap-3.5">
      {/* ── Breadcrumbs & Back Navigation ─────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2">
        <View className="flex-row items-center gap-2">
          <Pressable
            onPress={() => router.push("/daylite" as Href)}
            className="py-0.5 cursor-pointer"
            accessibilityRole="button"
          >
            <Text className="text-xs font-semibold text-blue-400 hover:underline">Daylite</Text>
          </Pressable>
          <Text className="text-xs text-slate-600">/</Text>
          <Pressable
            onPress={() => router.push("/daylite" as Href)}
            className="py-0.5 cursor-pointer"
          >
            <Text className="text-xs font-semibold text-slate-400 hover:text-slate-200">
              Quality Suite
            </Text>
          </Pressable>
          <Text className="text-xs text-slate-600">/</Text>
          <Text className="text-xs font-bold text-white tracking-tight">
            {activeTabConfig.label}
          </Text>
        </View>

        <Pressable
          onPress={() => router.push("/daylite" as Href)}
          className="flex-row items-center gap-1.5 bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors cursor-pointer"
          accessibilityRole="button"
        >
          <ArrowLeft size={12} color={THEME_COLORS.textMuted} />
          <Text className="text-xs font-semibold text-slate-300">Back to Dashboard</Text>
        </Pressable>
      </View>

      {/* ── Title Hero Bar ───────────────────────────────────── */}
      <View className="bg-dark-card border border-dark-border p-4 rounded-xl gap-3 shadow-sm">
        <View className="flex-row items-start justify-between flex-wrap gap-3">
          <View className="flex-row items-center gap-3 flex-1 min-w-[280px]">
            <View className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 items-center justify-center">
              {activeTabConfig.icon}
            </View>
            <View className="flex-1">
              <View className="flex-row items-center gap-2 flex-wrap">
                <Text className="text-base sm:text-lg font-black text-white tracking-tight">
                  {activeTabConfig.label}
                </Text>
                <View className={`px-2 py-0.5 rounded border ${severityHeaderStyle}`}>
                  <Text className={`text-[10px] font-bold ${severityHeaderStyle.split(" ").pop()}`}>
                    {activeTabConfig.category}
                  </Text>
                </View>
                <View className="bg-blue-950/80 border border-blue-800/80 px-2 py-0.5 rounded">
                  <Text className="text-[10px] font-mono font-bold text-blue-300">
                    {data?.total !== undefined
                      ? `${data.total.toLocaleString()} ${data.unit_label_plural || "Affected Records"}`
                      : "Loading…"}
                  </Text>
                </View>
                {data?.calculated_at && (
                  <View className="bg-slate-900 border border-slate-700/60 px-2 py-0.5 rounded flex-row items-center gap-1">
                    <Text className="text-[10px] font-mono text-slate-400">
                      Snapshot: {new Date(data.calculated_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </Text>
                  </View>
                )}
              </View>
              <Text className="text-xs text-slate-400 mt-1">
                {activeTabConfig.description}
              </Text>
            </View>
          </View>

          {/* Action Bar: Export Buttons & Refresh */}
          <View className="flex-row items-center gap-2 flex-wrap">
            {/* Export as Excel */}
            <Pressable
              onPress={() => handleExport("xlsx")}
              disabled={isExporting !== null || (data?.total === 0)}
              className={`flex-row items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
                isExporting === "xlsx"
                  ? "bg-emerald-950/80 border-emerald-700 text-emerald-300"
                  : "bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border-slate-700 text-slate-200"
              }`}
              accessibilityRole="button"
              accessibilityLabel="Export as Excel .xlsx"
            >
              {isExporting === "xlsx" ? (
                <RefreshCw size={12} color={THEME_COLORS.successIcon} className="animate-spin" />
              ) : (
                <FileSpreadsheet size={12} color={THEME_COLORS.successIcon} />
              )}
              <Text className="text-xs font-semibold text-slate-200">
                {isExporting === "xlsx" ? "Exporting…" : "Excel (.xlsx)"}
              </Text>
            </Pressable>

            {/* Export as CSV */}
            <Pressable
              onPress={() => handleExport("csv")}
              disabled={isExporting !== null || (data?.total === 0)}
              className={`flex-row items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
                isExporting === "csv"
                  ? "bg-blue-950/80 border-blue-700 text-blue-300"
                  : "bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border-slate-700 text-slate-200"
              }`}
              accessibilityRole="button"
              accessibilityLabel="Export as CSV"
            >
              {isExporting === "csv" ? (
                <RefreshCw size={12} color={THEME_COLORS.primaryIcon} className="animate-spin" />
              ) : (
                <FileText size={12} color={THEME_COLORS.primaryIcon} />
              )}
              <Text className="text-xs font-semibold text-slate-200">
                {isExporting === "csv" ? "Exporting…" : "CSV"}
              </Text>
            </Pressable>

            {/* Quick Refresh */}
            <Pressable
              onPress={() => refetch()}
              disabled={isLoading || isFetching}
              className="flex-row items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700 transition-colors cursor-pointer"
            >
              <RefreshCw
                size={12}
                color={THEME_COLORS.textMuted}
                className={isFetching ? "animate-spin" : ""}
              />
              <Text className="text-xs text-slate-300 font-medium">
                {isFetching ? "Refreshing…" : "Refresh"}
              </Text>
            </Pressable>
          </View>
        </View>

        {exportError ? (
          <View className="bg-rose-950/60 border border-rose-800/80 p-2 rounded-lg flex-row items-center justify-between">
            <Text className="text-xs text-rose-300">{exportError}</Text>
            <Pressable onPress={() => setExportError(null)}>
              <X size={12} color={THEME_COLORS.dangerIcon} />
            </Pressable>
          </View>
        ) : null}

        {/* ── Dimension Filter Tabs ───────────────────────────── */}
        <View className="flex-row items-center gap-1.5 border-t border-dark-border/60 pt-2.5 overflow-x-auto flex-nowrap">
          <Text className="text-[11px] font-bold text-slate-400 uppercase mr-1">Dimension:</Text>
          {(
            [
              { key: "ALL", label: "All (37)" },
              { key: "CONTACTS", label: "Contacts (12)" },
              { key: "ADDRESSES", label: "Addresses (6)" },
              { key: "INTEGRITY", label: "Chronology (5)" },
              { key: "GOVERNANCE", label: "Governance (14)" },
            ] as { key: QualityDimension; label: string }[]
          ).map((dim) => {
            const isSel = activeDimension === dim.key;
            return (
              <Pressable
                key={dim.key}
                onPress={() => handleDimensionChange(dim.key)}
                className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                  isSel
                    ? "bg-blue-600 text-white font-bold"
                    : "bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400"
                }`}
              >
                <Text
                  className={`text-[11px] ${
                    isSel ? "text-white font-bold" : "text-slate-400"
                  }`}
                >
                  {dim.label}
                </Text>
              </Pressable>
            );
          })}
        </View>

        {/* ── Horizontal Issue Tabs Switcher ─────────────────── */}
        <View className="flex-row items-center overflow-x-auto flex-nowrap gap-1.5 pb-1">
          {filteredTabs.map((t) => {
            const active = activeIssue === t.id;
            return (
              <Pressable
                key={t.id}
                onPress={() => handleTabChange(t.id)}
                accessibilityRole="tab"
                accessibilityState={{ selected: active }}
                className={`flex-row items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
                  active
                    ? "bg-blue-600 border-blue-500 shadow-sm"
                    : "bg-slate-900/90 hover:bg-slate-800 border-slate-800"
                }`}
              >
                {t.icon}
                <Text
                  className={`text-[11px] font-semibold whitespace-nowrap ${
                    active ? "text-white font-bold" : "text-slate-300"
                  }`}
                >
                  {t.label}
                </Text>
              </Pressable>
            );
          })}
        </View>

        {/* ── Search, Sorting & Filter Toolbar ────────────────── */}
        <View className="flex-row items-center justify-between flex-wrap gap-2 pt-2 border-t border-dark-border/60">
          {/* Search Box */}
          <View className="flex-row items-center bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 gap-2 flex-1 min-w-[220px] max-w-md">
            <Search size={13} color={THEME_COLORS.textMuted} />
            <TextInput
              value={search}
              onChangeText={handleSearchChange}
              placeholder={`Search ${activeTabConfig.label} by Name, Person ID, or Value…`}
              placeholderTextColor={THEME_COLORS.textMuted}
              className="flex-1 text-xs text-white"
              autoCapitalize="none"
              autoCorrect={false}
            />
            {search ? (
              <Pressable onPress={() => handleSearchChange("")} className="cursor-pointer">
                <X size={12} color={THEME_COLORS.textMuted} />
              </Pressable>
            ) : null}
          </View>

          {/* Sort Controls */}
          <View className="flex-row items-center gap-2 flex-wrap">
            <View className="flex-row items-center gap-1 bg-slate-900 border border-slate-800 rounded-lg p-0.5">
              <Text className="text-[10px] font-bold text-slate-400 uppercase px-2">Sort:</Text>
              {(
                [
                  { id: "PersonID", label: "Person ID" },
                  { id: "PersonName", label: "Name" },
                  { id: "CurrentValue", label: "Value" },
                ] as { id: string; label: string }[]
              ).map((s) => {
                const isSelected = sortBy === s.id;
                return (
                  <Pressable
                    key={s.id}
                    onPress={() => {
                      setSortBy(s.id);
                      setPage(0);
                    }}
                    className={`px-2 py-1 rounded text-xs font-semibold transition-all cursor-pointer ${
                      isSelected
                        ? "bg-slate-800 text-white font-bold"
                        : "hover:bg-slate-800/40 text-slate-400"
                    }`}
                  >
                    <Text className={`text-[11px] ${isSelected ? "text-white font-bold" : "text-slate-400"}`}>
                      {s.label}
                    </Text>
                  </Pressable>
                );
              })}
            </View>

            {/* Sort Order Direction Toggle */}
            <Pressable
              onPress={toggleSortOrder}
              accessibilityRole="button"
              accessibilityLabel={`Sort direction: ${sortOrder.toUpperCase()}`}
              className="flex-row items-center gap-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer"
            >
              {sortOrder === "asc" ? (
                <>
                  <SortAsc size={13} color={THEME_COLORS.primaryIcon} />
                  <Text className="text-xs text-blue-400 font-bold">ASC</Text>
                </>
              ) : (
                <>
                  <SortDesc size={13} color={THEME_COLORS.primaryIcon} />
                  <Text className="text-xs text-blue-400 font-bold">DESC</Text>
                </>
              )}
            </Pressable>
          </View>
        </View>
      </View>

      {/* ── Main Issues Table ─────────────────────────────────── */}
      {isLoading && !data ? (
        <LoadingState message={`Evaluating live quality rule for ${activeTabConfig.label}…`} />
      ) : isError ? (
        <ErrorState
          message={error?.message || "Failed to load quality issues from MSSQL."}
          onRetry={refetch}
        />
      ) : !hasData ? (
        <EmptyState
          title="No affected records detected"
          message={
            search
              ? `No ${activeTabConfig.label} records matched your search query "${search}".`
              : `All active records strictly pass the validation rule for ${activeTabConfig.label}.`
          }
        />
      ) : isGroupRule && data?.groups ? (
        <View className="bg-dark-card border border-dark-border rounded-xl overflow-hidden shadow-sm flex-1">
          <View className="flex-row items-center bg-slate-900/90 border-b border-dark-border px-4 py-3 gap-3">
            <View className="flex-1"><Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Duplicate Anomaly Cluster</Text></View>
            <View className="w-32 items-center"><Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Affected Entities</Text></View>
            <View className="w-32 items-center"><Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Records</Text></View>
            <View className="w-20 items-end"><Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Details</Text></View>
          </View>
          <FlatList
            data={data.groups}
            renderItem={({ item: group, index }) => {
              const isExpanded = !!expandedGroups[group.GroupKey];
              const isEven = index % 2 === 0;
              return (
                <View className="border-b border-dark-border/40">
                  <Pressable onPress={() => toggleGroup(group.GroupKey)} className={`flex-row items-center px-4 py-3.5 hover:bg-slate-800/60 active:bg-slate-900/90 transition-colors gap-3 cursor-pointer ${isEven ? "bg-dark-card" : "bg-slate-900/20"}`}>
                    <View className="flex-1 flex-row items-center gap-2.5">
                      <View className="w-7 h-7 rounded-lg bg-amber-600/20 border border-amber-500/30 items-center justify-center"><Copy size={13} color={THEME_COLORS.companyIcon} /></View>
                      <View className="flex-1"><Text className="text-xs font-mono font-bold text-white tracking-tight" numberOfLines={1}>{group.GroupLabel}</Text><Text className="text-[10px] text-slate-400 font-semibold">Cluster: {group.GroupKey}</Text></View>
                    </View>
                    <View className="w-32 items-center"><View className="bg-blue-950/60 border border-blue-800/60 px-2 py-0.5 rounded"><Text className="text-[10px] font-mono font-bold text-blue-300">{group.AffectedPersonsCount} Persons</Text></View></View>
                    <View className="w-32 items-center"><View className="bg-amber-950/60 border border-amber-800/60 px-2 py-0.5 rounded"><Text className="text-[10px] font-mono font-bold text-amber-300">{group.AffectedRecordsCount} Records</Text></View></View>
                    <View className="w-20 items-end flex-row justify-end items-center gap-1"><Text className="text-[11px] font-semibold text-blue-400">{isExpanded ? "Hide" : "Expand"}</Text>{isExpanded ? <ChevronUp size={12} color={THEME_COLORS.primaryIcon} /> : <ChevronDown size={12} color={THEME_COLORS.primaryIcon} />}</View>
                  </Pressable>
                  {isExpanded && group.Members && group.Members.length > 0 ? (
                    <View className="bg-slate-950/70 border-t border-slate-800/80 px-6 py-2 gap-1.5">
                      <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Participating Records ({group.Members.length}):</Text>
                      {group.Members.map((member, mIdx) => (
                        <Pressable key={`${member.PersonID}-${member.ContactID || mIdx}`} onPress={() => router.push(`/daylite/person/${member.PersonID}` as Href)} className="flex-row items-center justify-between bg-slate-900/80 hover:bg-slate-800/80 border border-slate-800 p-2.5 rounded-lg transition-colors cursor-pointer group">
                          <View className="flex-row items-center gap-2.5 flex-1">
                            <View className="w-6 h-6 rounded-full bg-blue-600/20 border border-blue-500/30 items-center justify-center"><User size={11} color={THEME_COLORS.primaryIcon} /></View>
                            <View><Text className="text-xs font-bold text-white group-hover:text-blue-300 transition-colors">{member.PersonName}</Text><Text className="text-[10px] font-mono text-blue-400 font-semibold">Person #{member.PersonID} {member.LabelName ? `• ${member.LabelName}` : ""}</Text></View>
                          </View>
                          <View className="flex-row items-center gap-2">
                            {member.IsPrimary ? <View className="bg-emerald-950/60 border border-emerald-800/60 px-1.5 py-0.5 rounded"><Text className="text-[9px] font-bold text-emerald-300">PRIMARY</Text></View> : null}
                            <View className="flex-row items-center gap-0.5"><Text className="text-[11px] font-semibold text-blue-400 group-hover:underline">Inspect</Text><ChevronRight size={11} color={THEME_COLORS.primaryIcon} /></View>
                          </View>
                        </Pressable>
                      ))}
                    </View>
                  ) : null}
                </View>
              );
            }}
            keyExtractor={(item) => item.GroupKey}
            ListFooterComponent={<View className="p-3 border-t border-dark-border/60"><PaginationControls page={page} limit={limit} total={data?.total ?? 0} onPageChange={setPage} isFetching={isFetching} /></View>}
            contentContainerStyle={{ paddingBottom: 16 }}
          />
        </View>
      ) : (
        <View className="bg-dark-card border border-dark-border rounded-xl overflow-hidden shadow-sm flex-1">
          <View className="flex-row items-center bg-slate-900/90 border-b border-dark-border px-4 py-3 gap-3">
            <View className="w-[200px]"><Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Person Record</Text></View>
            <View className="w-[180px]"><Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Offending Value</Text></View>
            <View className="flex-1 min-w-[200px]"><Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Issue & Context</Text></View>
            <View className="w-24 items-center"><Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Severity</Text></View>
            <View className="w-20 items-end"><Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Action</Text></View>
          </View>
          <FlatList<ContactQualityIssueItem>
            data={data?.items || []}
            renderItem={({ item, index }) => {
              const isEven = index % 2 === 0;
              const severityStyles = {
                CRITICAL: "bg-rose-950/60 border-rose-800/60 text-rose-300",
                WARNING: "bg-amber-950/60 border-amber-800/60 text-amber-300",
                INFO: "bg-blue-950/60 border-blue-800/60 text-blue-300",
              }[item.Severity] || "bg-slate-900 border-slate-800 text-slate-300";
              return (
                <Pressable
                  onPress={() => router.push(`/daylite/person/${item.PersonID}` as Href)}
                  accessibilityRole="button"
                  className={`flex-row items-center px-4 py-3 border-b border-dark-border/40 hover:bg-slate-800/60 active:bg-slate-900/90 transition-colors gap-3 cursor-pointer group ${isEven ? "bg-dark-card" : "bg-slate-900/20"}`}
                >
                  <View className="w-[200px] flex-row items-center gap-2.5">
                    <View className="w-7 h-7 rounded-full bg-blue-600/20 border border-blue-500/30 items-center justify-center"><User size={13} color={THEME_COLORS.primaryIcon} /></View>
                    <View className="flex-1"><Text className="text-xs font-bold text-white group-hover:text-blue-300 transition-colors" numberOfLines={1}>{item.PersonName}</Text><Text className="text-[10px] font-mono text-blue-400 font-semibold">#{item.PersonID}</Text></View>
                  </View>
                  <View className="w-[180px] flex-row items-center gap-2">
                    {item.ContactType === "EMAIL" ? <Mail size={12} color={THEME_COLORS.primaryIcon} /> : item.ContactType === "PHONE" ? <Phone size={12} color={THEME_COLORS.successIcon} /> : item.ContactType === "ADDRESS" ? <MapPinOff size={12} color={THEME_COLORS.warningIcon} /> : item.ContactType === "PROFILE" ? <CalendarX size={12} color={THEME_COLORS.dangerIcon} /> : item.ContactType === "COMPANY" ? <Building2 size={12} color={THEME_COLORS.companyIcon} /> : item.ContactType === "CUSTOM_FIELD" ? <Sliders size={12} color={THEME_COLORS.dangerIcon} /> : item.ContactType === "EMPLOYMENT" ? <FileWarning size={12} color={THEME_COLORS.warningIcon} /> : <Globe size={12} color={THEME_COLORS.warningIcon} />}
                    <View className="flex-1"><Text className="text-xs font-mono font-bold text-white" numberOfLines={1}>{item.CurrentValue || item.MaskedValue || "—"}</Text>{item.LabelName ? <Text className="text-[10px] text-slate-400" numberOfLines={1}>{item.LabelName}</Text> : null}</View>
                  </View>
                  <View className="flex-1 min-w-[200px]"><Text className="text-xs text-slate-300" numberOfLines={2}>{item.IssueDescription}</Text></View>
                  <View className="w-24 items-center"><View className={`px-2 py-0.5 rounded border ${severityStyles}`}><Text className={`text-[9px] font-bold ${severityStyles.split(" ").pop()}`}>{item.Severity}</Text></View></View>
                  <View className="w-20 items-end flex-row justify-end items-center gap-0.5"><Text className="text-[11px] font-semibold text-blue-400 group-hover:underline">Inspect</Text><ChevronRight size={12} color={THEME_COLORS.primaryIcon} /></View>
                </Pressable>
              );
            }}
            keyExtractor={(item, index) => `${item.PersonID}-${item.ContactID || index}-${item.IssueCode}`}
            showsVerticalScrollIndicator={false}
            ListFooterComponent={<View className="p-3 border-t border-dark-border/60"><PaginationControls page={page} limit={limit} total={data?.total ?? 0} onPageChange={setPage} isFetching={isFetching} /></View>}
            contentContainerStyle={{ paddingBottom: 16 }}
          />
        </View>
      )}
    </View>
  );
};
