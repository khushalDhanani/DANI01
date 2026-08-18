import React, { useState } from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import {
  AlertCircle,
  AlertTriangle,
  Building2,
  CalendarOff,
  CalendarX,
  CheckCircle2,
  Clock,
  Compass,
  Copy,
  ExternalLink,
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
  ShieldAlert,
  ShieldCheck,
  ShieldX,
  Sliders,
  UserCheck,
  UserX,
  X,
} from "lucide-react-native";
import { useContactQualitySummary } from "@/hooks/useModules";
import { exportContactQualitySummary } from "@/api/modules.api";
import { ContactQualityCard } from "./components/ContactQualityCard";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ErrorState } from "@/components/ui/ErrorState";
import { THEME_COLORS } from "@/constants/theme";

type QualityCategoryKey = "ALL" | "CONTACTS" | "ADDRESSES" | "INTEGRITY" | "GOVERNANCE";

export const ContactQualitySection: React.FC = () => {
  const router = useRouter();
  const { data: summary, isLoading, isError, error, refetch } = useContactQualitySummary();
  const [activeCategory, setActiveCategory] = useState<QualityCategoryKey>("ALL");
  const [isExporting, setIsExporting] = useState<"xlsx" | "csv" | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  const handleExport = async (format: "xlsx" | "csv") => {
    try {
      setIsExporting(format);
      setExportError(null);
      await exportContactQualitySummary(format);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to download summary report.";
      setExportError(msg);
    } finally {
      setIsExporting(null);
    }
  };

  if (isLoading) {
    return (
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3">
        <View className="flex-row items-center gap-2">
          <LoadingSkeleton width={140} height={18} borderRadius={4} />
        </View>
        <View className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
          <LoadingSkeleton height={85} borderRadius={8} />
          <LoadingSkeleton height={85} borderRadius={8} />
          <LoadingSkeleton height={85} borderRadius={8} />
          <LoadingSkeleton height={85} borderRadius={8} />
        </View>
      </View>
    );
  }

  if (isError || !summary) {
    return (
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-2">
        <ErrorState
          title="Quality Telemetry Unavailable"
          message={error?.message || "Failed to calculate quality telemetry from MSSQL."}
          onRetry={() => refetch()}
        />
      </View>
    );
  }

  const totalCriticalFindings = summary.total_critical_findings ?? (
    summary.invalid_emails +
    summary.invalid_phones +
    summary.persons_multiple_primary +
    summary.primary_contact_inactive +
    summary.addr_invalid_pin_format +
    summary.person_anniversary_before_birth +
    summary.person_invalid_birth_date +
    summary.status_active_and_deleted +
    summary.blacklist_unapproved +
    summary.blacklist_missing_details +
    summary.company_orphan_links +
    summary.extra_field_orphan_id +
    summary.audit_del_before_ent
  );

  const totalWarningFindings = summary.total_warning_findings ?? (
    summary.persons_without_email +
    summary.persons_without_phone +
    summary.duplicate_email_cross_persons +
    summary.duplicate_phone_cross_persons +
    summary.duplicate_email_same_person +
    summary.duplicate_phone_same_person +
    summary.invalid_urls +
    summary.addr_missing_postal_code +
    summary.addr_street_without_city +
    summary.addr_city_without_state +
    summary.addr_duplicate_same_person +
    summary.person_birth_date_ancient +
    summary.person_suspicious_dummy_names +
    summary.person_missing_lastname_only +
    summary.active_emp_missing_title +
    summary.stale_temp_persons +
    summary.inactive_with_empid +
    summary.company_duplicate_links +
    summary.company_missing_role +
    summary.extra_field_duplicate_entries +
    summary.deleted_missing_del_date +
    summary.sync_zimbra_missing_id
  );

  const totalCleanPersons = summary.total_clean_persons ?? Math.max(0, summary.total_persons_evaluated - (summary.persons_with_any_issue || 0));
  const healthScore = summary.health_score_pct ?? 100.0;

  const ALL_CARDS = [
    // Contacts
    { title: "Missing Email", count: summary.persons_without_email, issueCode: "MISSING_EMAIL", description: "Persons without any registered email", severity: "WARNING" as const, unitLabel: "Person", icon: <MailWarning size={13} color={THEME_COLORS.warningIcon} />, category: "CONTACTS" },
    { title: "Missing Phone", count: summary.persons_without_phone, issueCode: "MISSING_PHONE", description: "Persons without any registered phone", severity: "WARNING" as const, unitLabel: "Person", icon: <PhoneOff size={13} color={THEME_COLORS.warningIcon} />, category: "CONTACTS" },
    { title: "Invalid Email", count: summary.invalid_emails, issueCode: "INVALID_EMAIL", description: "Malformed format or invalid characters", severity: "CRITICAL" as const, unitLabel: "Contact", icon: <Mail size={13} color={THEME_COLORS.dangerIcon} />, category: "CONTACTS" },
    { title: "Invalid Phone", count: summary.invalid_phones, issueCode: "INVALID_PHONE", description: "Invalid phone (7-15 digits) or extension (!= 4 digits)", severity: "CRITICAL" as const, unitLabel: "Contact", icon: <Phone size={13} color={THEME_COLORS.dangerIcon} />, category: "CONTACTS" },
    { title: "Shared Email", count: summary.duplicate_email_cross_persons, issueCode: "DUPLICATE_EMAIL_CROSS", description: "Identical email linked to multiple Persons", severity: "WARNING" as const, unitLabel: "Group", icon: <Copy size={13} color={THEME_COLORS.companyIcon} />, category: "CONTACTS" },
    { title: "Shared Phone", count: summary.duplicate_phone_cross_persons, issueCode: "DUPLICATE_PHONE_CROSS", description: "Identical phone linked to multiple Persons", severity: "WARNING" as const, unitLabel: "Group", icon: <Copy size={13} color={THEME_COLORS.companyIcon} />, category: "CONTACTS" },
    { title: "Duplicate Email (Self)", count: summary.duplicate_email_same_person, issueCode: "DUPLICATE_EMAIL_SAME", description: "Same email added multiple times for 1 Person", severity: "WARNING" as const, unitLabel: "Group", icon: <UserCheck size={13} color={THEME_COLORS.primaryIcon} />, category: "CONTACTS" },
    { title: "Duplicate Phone (Self)", count: summary.duplicate_phone_same_person, issueCode: "DUPLICATE_PHONE_SAME", description: "Same phone added multiple times for 1 Person", severity: "WARNING" as const, unitLabel: "Group", icon: <UserCheck size={13} color={THEME_COLORS.primaryIcon} />, category: "CONTACTS" },
    { title: "Unverified Contacts", count: summary.unverified_contacts, issueCode: "UNVERIFIED_CONTACT", description: "Channels without verified flag status", severity: "INFO" as const, unitLabel: "Contact", icon: <ShieldAlert size={13} color={THEME_COLORS.imIcon} />, category: "CONTACTS" },
    { title: "Invalid URLs", count: summary.invalid_urls, issueCode: "INVALID_URL", description: "URLs missing http/https/www scheme", severity: "WARNING" as const, unitLabel: "Contact", icon: <Globe size={13} color={THEME_COLORS.warningIcon} />, category: "CONTACTS" },
    { title: "Multiple Primary", count: summary.persons_multiple_primary, issueCode: "MULTIPLE_PRIMARY", description: "Persons with conflicting primary contacts", severity: "CRITICAL" as const, unitLabel: "Person", icon: <Layers size={13} color={THEME_COLORS.dangerIcon} />, category: "CONTACTS" },
    { title: "Primary Inactive", count: summary.primary_contact_inactive, issueCode: "PRIMARY_INACTIVE", description: "Primary contact flagged inactive", severity: "CRITICAL" as const, unitLabel: "Contact", icon: <ShieldX size={13} color={THEME_COLORS.dangerIcon} />, category: "CONTACTS" },

    // Addresses
    { title: "Missing Postal Code", count: summary.addr_missing_postal_code, issueCode: "MISSING_POSTAL_CODE", description: "Address records without a postal / PIN code", severity: "WARNING" as const, unitLabel: "Address", icon: <MapPinOff size={13} color={THEME_COLORS.warningIcon} />, category: "ADDRESSES" },
    { title: "Invalid PIN Format", count: summary.addr_invalid_pin_format, issueCode: "INVALID_PIN_CODE_FORMAT", description: "Postal code with non-numeric or bad length", severity: "CRITICAL" as const, unitLabel: "Address", icon: <MapPinOff size={13} color={THEME_COLORS.dangerIcon} />, category: "ADDRESSES" },
    { title: "Street Without City", count: summary.addr_street_without_city, issueCode: "STREET_WITHOUT_CITY", description: "Street address present but city name is blank", severity: "WARNING" as const, unitLabel: "Address", icon: <Compass size={13} color={THEME_COLORS.warningIcon} />, category: "ADDRESSES" },
    { title: "City Without State", count: summary.addr_city_without_state, issueCode: "CITY_WITHOUT_STATE", description: "City address without state region specified", severity: "WARNING" as const, unitLabel: "Address", icon: <Compass size={13} color={THEME_COLORS.warningIcon} />, category: "ADDRESSES" },
    { title: "Missing Geocodes", count: summary.addr_missing_geocodes, issueCode: "MISSING_GEOCODES", description: "Addresses lacking Latitude/Longitude coordinates", severity: "INFO" as const, unitLabel: "Address", icon: <NavigationOff size={13} color={THEME_COLORS.imIcon} />, category: "ADDRESSES" },
    { title: "Duplicate Address", count: summary.addr_duplicate_same_person, issueCode: "DUPLICATE_ADDRESSES_SAME_PERSON", description: "Identical address entered twice for 1 Person", severity: "WARNING" as const, unitLabel: "Group", icon: <Copy size={13} color={THEME_COLORS.warningIcon} />, category: "ADDRESSES" },

    // Integrity
    { title: "Anniversary Before Birth", count: summary.person_anniversary_before_birth, issueCode: "ANNIVERSARY_BEFORE_BIRTH", description: "Anniversary date earlier than birth date", severity: "CRITICAL" as const, unitLabel: "Person", icon: <CalendarX size={13} color={THEME_COLORS.dangerIcon} />, category: "INTEGRITY" },
    { title: "Invalid Birth Date", count: summary.person_invalid_birth_date, issueCode: "INVALID_BIRTH_DATE", description: "Birth date in the future or before 1900", severity: "CRITICAL" as const, unitLabel: "Person", icon: <CalendarOff size={13} color={THEME_COLORS.dangerIcon} />, category: "INTEGRITY" },
    { title: "Dummy/Ancient DOB", count: summary.person_birth_date_ancient, issueCode: "BIRTH_DATE_DEFAULT_OR_ANCIENT", description: "Birth date is dummy 1900-01-01 or age > 100", severity: "WARNING" as const, unitLabel: "Person", icon: <CalendarOff size={13} color={THEME_COLORS.warningIcon} />, category: "INTEGRITY" },
    { title: "Suspicious Test Names", count: summary.person_suspicious_dummy_names, issueCode: "SUSPICIOUS_DUMMY_NAMES", description: "Placeholder names (test, admin, dummy, etc.)", severity: "WARNING" as const, unitLabel: "Person", icon: <UserX size={13} color={THEME_COLORS.warningIcon} />, category: "INTEGRITY" },
    { title: "Missing Last Name", count: summary.person_missing_lastname_only, issueCode: "MISSING_LAST_NAME", description: "Person has first name but missing surname", severity: "WARNING" as const, unitLabel: "Person", icon: <FileWarning size={13} color={THEME_COLORS.warningIcon} />, category: "INTEGRITY" },

    // Governance
    { title: "Active & Deleted Conflict", count: summary.status_active_and_deleted, issueCode: "STATUS_ACTIVE_AND_DELETED", description: "Record marked both Active and Deleted", severity: "CRITICAL" as const, unitLabel: "Person", icon: <ShieldAlert size={13} color={THEME_COLORS.dangerIcon} />, category: "GOVERNANCE" },
    { title: "Employee Missing Title", count: summary.active_emp_missing_title, issueCode: "ACTIVE_EMP_MISSING_TITLE", description: "Active employee has no job title designation", severity: "WARNING" as const, unitLabel: "Person", icon: <FileWarning size={13} color={THEME_COLORS.warningIcon} />, category: "GOVERNANCE" },
    { title: "Inactive with EmpID (Info)", count: summary.inactive_with_empid, issueCode: "INACTIVE_WITH_ACTIVE_EMPID", description: "Informational: Inactive records retaining employee ID (excluded from active score)", severity: "INFO" as const, unitLabel: "Person", icon: <AlertCircle size={13} color={THEME_COLORS.textMuted} />, category: "GOVERNANCE" },
    { title: "Stale Temp Persons", count: summary.stale_temp_persons, issueCode: "STALE_TEMP_PERSONS", description: "Temporary person record older than 90 days", severity: "WARNING" as const, unitLabel: "Person", icon: <Clock size={13} color={THEME_COLORS.warningIcon} />, category: "GOVERNANCE" },
    { title: "Unapproved Blacklist", count: summary.blacklist_unapproved, issueCode: "BLACKLIST_UNAPPROVED", description: "Blacklist flag active without HOD approval", severity: "CRITICAL" as const, unitLabel: "Person", icon: <ShieldAlert size={13} color={THEME_COLORS.dangerIcon} />, category: "GOVERNANCE" },
    { title: "Missing Blacklist Details", count: summary.blacklist_missing_details, issueCode: "BLACKLIST_MISSING_DETAILS", description: "Blacklist record missing date or type", severity: "CRITICAL" as const, unitLabel: "Person", icon: <FileWarning size={13} color={THEME_COLORS.dangerIcon} />, category: "GOVERNANCE" },
    { title: "Orphan Company Link", count: summary.company_orphan_links, issueCode: "ORPHAN_COMPANY_LINK", description: "Link references non-existent company ID", severity: "CRITICAL" as const, unitLabel: "Link", icon: <Building2 size={13} color={THEME_COLORS.dangerIcon} />, category: "GOVERNANCE" },
    { title: "Duplicate Company Link", count: summary.company_duplicate_links, issueCode: "DUPLICATE_COMPANY_LINKS", description: "Same company linked >1 times to Person", severity: "WARNING" as const, unitLabel: "Group", icon: <Copy size={13} color={THEME_COLORS.warningIcon} />, category: "GOVERNANCE" },
    { title: "Company Missing Role", count: summary.company_missing_role, issueCode: "COMPANY_MISSING_ROLE", description: "Company affiliation without role definition", severity: "WARNING" as const, unitLabel: "Link", icon: <Building2 size={13} color={THEME_COLORS.warningIcon} />, category: "GOVERNANCE" },
    { title: "Orphan Extra Field", count: summary.extra_field_orphan_id, issueCode: "EXTRA_FIELD_ORPHAN_ID", description: "Custom field with invalid schema definition", severity: "CRITICAL" as const, unitLabel: "Field", icon: <Sliders size={13} color={THEME_COLORS.dangerIcon} />, category: "GOVERNANCE" },
    { title: "Duplicate Extra Fields", count: summary.extra_field_duplicate_entries, issueCode: "DUPLICATE_EXTRA_FIELDS", description: "Duplicate custom field entries for 1 Person", severity: "WARNING" as const, unitLabel: "Group", icon: <Sliders size={13} color={THEME_COLORS.warningIcon} />, category: "GOVERNANCE" },
    { title: "Missing Deletion Date", count: summary.deleted_missing_del_date, issueCode: "DELETED_MISSING_TIMESTAMP", description: "Deleted person missing deletion timestamp", severity: "WARNING" as const, unitLabel: "Person", icon: <Clock size={13} color={THEME_COLORS.warningIcon} />, category: "GOVERNANCE" },
    { title: "Deletion Before Creation", count: summary.audit_del_before_ent, issueCode: "AUDIT_DEL_BEFORE_ENT", description: "Deletion date is earlier than creation date", severity: "CRITICAL" as const, unitLabel: "Person", icon: <Clock size={13} color={THEME_COLORS.dangerIcon} />, category: "GOVERNANCE" },
    { title: "Broken Zimbra Sync", count: summary.sync_zimbra_missing_id, issueCode: "SYNC_ZIMBRA_MISSING_ID", description: "Sync enabled but missing Zimbra ID", severity: "WARNING" as const, unitLabel: "Person", icon: <RefreshCw size={13} color={THEME_COLORS.warningIcon} />, category: "GOVERNANCE" }
  ];

  const filteredCards = ALL_CARDS.filter(
    (card) =>
      (activeCategory === "ALL" || card.category === activeCategory) &&
      (card.count ?? 0) > 0
  );

  const criticalCards = filteredCards.filter(c => c.severity === "CRITICAL");
  const warningCards = filteredCards.filter(c => c.severity === "WARNING");
  const infoCards = filteredCards.filter(c => c.severity === "INFO");

  return (
    <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3.5 shadow-sm">
      {/* ── Section Header ────────────────────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-3 pb-3 border-b border-dark-border">
        {/* Title & Core Health Indicator */}
        <View className="flex-row items-center gap-3">
          <View className="w-9 h-9 rounded-lg bg-blue-600/20 border border-blue-500/30 items-center justify-center">
            <ShieldCheck size={18} color={THEME_COLORS.primaryIcon} />
          </View>
          <View>
            <View className="flex-row items-center gap-2 flex-wrap">
              <Text className="text-sm font-black text-white uppercase tracking-wider">
                Data Quality & Integrity Analyzer
              </Text>
              <View className="bg-emerald-950/80 border border-emerald-700/80 px-2 py-0.5 rounded-full flex-row items-center gap-1">
                <CheckCircle2 size={10} color={THEME_COLORS.successIcon} />
                <Text className="text-[10px] font-mono font-bold text-emerald-300">
                  {healthScore.toFixed(1)}% Clean ({totalCleanPersons.toLocaleString()})
                </Text>
              </View>
            </View>
            <View className="flex-row items-center gap-1.5 mt-0.5">
              <Text className="text-[11px] text-slate-400 font-medium">
                {(summary.total_persons_evaluated ?? 0).toLocaleString()} Active Evaluated
              </Text>
              <Text className="text-[11px] text-slate-600">•</Text>
              <Text className="text-[11px] text-slate-400 font-medium">
                {summary.related_tables_checked ?? 0} Tables Checked
              </Text>
            </View>
          </View>
        </View>

        {/* Clean Action Buttons */}
        <View className="flex-row items-center gap-2">
          <View className="flex-row items-center gap-1 bg-slate-900 border border-slate-800 p-0.5 rounded-lg">
            <Pressable
              onPress={() => handleExport("xlsx")}
              disabled={isExporting !== null}
              className={`flex-row items-center gap-1 px-2.5 py-1 rounded transition-all cursor-pointer ${
                isExporting === "xlsx" ? "bg-emerald-950/80 text-emerald-300" : "hover:bg-slate-800"
              }`}
              accessibilityRole="button"
              accessibilityLabel="Export Quality Suite as Excel"
            >
              {isExporting === "xlsx" ? (
                <RefreshCw size={11} color={THEME_COLORS.successIcon} className="animate-spin" />
              ) : (
                <FileSpreadsheet size={11} color={THEME_COLORS.successIcon} />
              )}
              <Text className="text-xs font-semibold text-slate-300">
                {isExporting === "xlsx" ? "Exporting…" : "Excel"}
              </Text>
            </Pressable>

            <Pressable
              onPress={() => handleExport("csv")}
              disabled={isExporting !== null}
              className={`flex-row items-center gap-1 px-2.5 py-1 rounded transition-all cursor-pointer ${
                isExporting === "csv" ? "bg-blue-950/80 text-blue-300" : "hover:bg-slate-800"
              }`}
              accessibilityRole="button"
              accessibilityLabel="Export Quality Suite as CSV"
            >
              {isExporting === "csv" ? (
                <RefreshCw size={11} color={THEME_COLORS.primaryIcon} className="animate-spin" />
              ) : (
                <FileText size={11} color={THEME_COLORS.primaryIcon} />
              )}
              <Text className="text-xs font-semibold text-slate-300">
                {isExporting === "csv" ? "Exporting…" : "CSV"}
              </Text>
            </Pressable>
          </View>

          <Pressable
            onPress={() => router.push("/daylite/quality" as Href)}
            className="flex-row items-center gap-1 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors cursor-pointer"
          >
            <Text className="text-xs font-semibold text-slate-300">Explore All Issues</Text>
            <ExternalLink size={11} color={THEME_COLORS.textMuted} />
          </Pressable>
        </View>
      </View>

      {exportError ? (
        <View className="bg-rose-950/60 border border-rose-800/80 p-2 rounded-lg flex-row items-center justify-between">
          <Text className="text-xs text-rose-300">{exportError}</Text>
          <Pressable onPress={() => setExportError(null)} className="cursor-pointer">
            <X size={12} color={THEME_COLORS.dangerIcon} />
          </Pressable>
        </View>
      ) : null}

      {/* ── Filter Tabs & Telemetry Summary Bar ──────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2 pt-0.5">
        <View className="flex-row items-center gap-1 overflow-x-auto flex-nowrap">
          {(
            [
              { key: "ALL", label: "All Dimensions" },
              { key: "CONTACTS", label: "Contacts & Duplicates" },
              { key: "ADDRESSES", label: "Address & Locations" },
              { key: "INTEGRITY", label: "Profile & Chronology" },
              { key: "GOVERNANCE", label: "Governance & Links" },
            ] as const
          ).map((tab) => {
            const isActive = activeCategory === tab.key;
            return (
              <Pressable
                key={tab.key}
                onPress={() => setActiveCategory(tab.key)}
                className={`px-3 py-1.5 rounded-lg border transition-all cursor-pointer ${
                  isActive
                    ? "bg-blue-600 border-blue-500 shadow-sm"
                    : "bg-slate-900/60 border-slate-800/80 hover:bg-slate-800/80"
                }`}
              >
                <Text
                  className={`text-xs font-semibold ${
                    isActive ? "text-white font-bold" : "text-slate-400"
                  }`}
                >
                  {tab.label}
                </Text>
              </Pressable>
            );
          })}
        </View>

        {/* Minimal Findings Summary Badges */}
        <View className="flex-row items-center gap-2">
          {totalCriticalFindings > 0 && (
            <View className="flex-row items-center gap-1 bg-rose-950/40 border border-rose-800/50 px-2.5 py-1 rounded-full">
              <AlertCircle size={10} color={THEME_COLORS.dangerIcon} />
              <Text className="text-[10px] font-bold text-rose-300 font-mono">
                {totalCriticalFindings.toLocaleString()} Critical
              </Text>
            </View>
          )}

          {totalWarningFindings > 0 && (
            <View className="flex-row items-center gap-1 bg-amber-950/40 border border-amber-800/50 px-2.5 py-1 rounded-full">
              <AlertTriangle size={10} color={THEME_COLORS.warningIcon} />
              <Text className="text-[10px] font-bold text-amber-300 font-mono">
                {totalWarningFindings.toLocaleString()} Warnings
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* ── KPI Grid (Grouped by Severity) ───────────────────── */}
      <View className="flex-col gap-4 mt-2">

        {/* CRITICAL SECTION */}
        {criticalCards.length > 0 && (
          <View className="flex-col gap-3">
            <View className="flex-row items-center justify-between border-b border-rose-900/50 pb-2">
              <View className="flex-row items-center gap-2">
                <View className="w-6 h-6 rounded-md bg-rose-600/20 border border-rose-500/30 items-center justify-center">
                  <ShieldX size={14} color={THEME_COLORS.dangerIcon} />
                </View>
                <Text className="text-sm font-black text-rose-400 tracking-widest uppercase">Critical</Text>
              </View>
              <Text className="text-xs font-bold text-rose-500 bg-rose-950/40 px-2 py-0.5 rounded-full">
                {totalCriticalFindings.toLocaleString()} Findings
              </Text>
            </View>
            <View className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {criticalCards.map(c => (
                <ContactQualityCard
                  key={c.issueCode}
                  title={c.title}
                  count={c.count}
                  issueCode={c.issueCode}
                  description={c.description}
                  unitLabel={c.unitLabel}
                  icon={c.icon}
                />
              ))}
            </View>
          </View>
        )}

        {/* WARNING SECTION */}
        {warningCards.length > 0 && (
          <View className="flex-col gap-3">
            <View className="flex-row items-center justify-between border-b border-amber-900/50 pb-2">
              <View className="flex-row items-center gap-2">
                <View className="w-6 h-6 rounded-md bg-amber-600/20 border border-amber-500/30 items-center justify-center">
                  <AlertTriangle size={14} color={THEME_COLORS.warningIcon} />
                </View>
                <Text className="text-sm font-black text-amber-400 tracking-widest uppercase">Warning</Text>
              </View>
              <Text className="text-xs font-bold text-amber-500 bg-amber-950/40 px-2 py-0.5 rounded-full">
                {totalWarningFindings.toLocaleString()} Findings
              </Text>
            </View>
            <View className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {warningCards.map(c => (
                <ContactQualityCard
                  key={c.issueCode}
                  title={c.title}
                  count={c.count}
                  issueCode={c.issueCode}
                  description={c.description}
                  unitLabel={c.unitLabel}
                  icon={c.icon}
                />
              ))}
            </View>
          </View>
        )}

        {/* INFO SECTION */}
        {infoCards.length > 0 && (
          <View className="flex-col gap-3">
            <View className="flex-row items-center justify-between border-b border-blue-900/50 pb-2">
              <View className="flex-row items-center gap-2">
                <View className="w-6 h-6 rounded-md bg-blue-600/20 border border-blue-500/30 items-center justify-center">
                  <AlertCircle size={14} color={THEME_COLORS.primaryIcon} />
                </View>
                <Text className="text-sm font-black text-blue-400 tracking-widest uppercase">Info</Text>
              </View>
              <Text className="text-xs font-bold text-blue-500 bg-blue-950/40 px-2 py-0.5 rounded-full">
                {summary.total_info_findings?.toLocaleString() || infoCards.reduce((acc, c) => acc + c.count, 0).toLocaleString()} Findings
              </Text>
            </View>
            <View className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {infoCards.map(c => (
                <ContactQualityCard
                  key={c.issueCode}
                  title={c.title}
                  count={c.count}
                  issueCode={c.issueCode}
                  description={c.description}
                  unitLabel={c.unitLabel}
                  icon={c.icon}
                />
              ))}
            </View>
          </View>
        )}

        {filteredCards.length === 0 && (
          <View className="p-6 items-center justify-center bg-dark-bg/40 border border-slate-800/80 rounded-xl my-2">
            <CheckCircle2 size={24} color={THEME_COLORS.successIcon} />
            <Text className="text-sm font-bold text-white mt-2">No Quality Findings</Text>
            <Text className="text-xs text-slate-400 mt-0.5 text-center">
              All evaluated rules in this category have 0 findings.
            </Text>
          </View>
        )}

      </View>
    </View>
  );
};
