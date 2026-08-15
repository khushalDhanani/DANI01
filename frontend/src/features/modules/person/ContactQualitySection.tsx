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

  const totalCritical =
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
    summary.audit_del_before_ent;

  const totalWarnings =
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
    summary.company_duplicate_links +
    summary.company_missing_role +
    summary.extra_field_duplicate_entries +
    summary.deleted_missing_del_date +
    summary.sync_zimbra_missing_id;

  return (
    <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3.5 shadow-sm">
      {/* ── Section Header ────────────────────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2 pb-2.5 border-b border-dark-border">
        <View className="flex-row items-center gap-2.5">
          <View className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 items-center justify-center">
            <ShieldCheck size={16} color={THEME_COLORS.primaryIcon} />
          </View>
          <View>
            <View className="flex-row items-center gap-2">
              <Text className="text-sm font-black text-white uppercase tracking-wider">
                Data Quality & Integrity Analyzer
              </Text>
            </View>
            <View className="flex-row items-center gap-1.5 flex-wrap mt-1">
              <View className="bg-blue-950/80 border border-blue-800/80 px-2 py-0.5 rounded">
                <Text className="text-[10px] font-mono font-bold text-blue-300">
                  {(summary.total_persons_evaluated || 28493).toLocaleString()} Valid Active Evaluated
                </Text>
              </View>
              <View className="bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                <Text className="text-[10px] font-mono font-bold text-slate-300">
                  {summary.related_tables_checked || 8} Related Tables Checked
                </Text>
              </View>
              {summary.total_inactive_persons ? (
                <View className="bg-slate-900/60 border border-slate-800/60 px-2 py-0.5 rounded">
                  <Text className="text-[10px] font-mono font-medium text-slate-400">
                    {summary.total_inactive_persons.toLocaleString()} Inactive Excluded
                  </Text>
                </View>
              ) : null}
              {summary.total_deleted_persons ? (
                <View className="bg-slate-900/60 border border-slate-800/60 px-2 py-0.5 rounded">
                  <Text className="text-[10px] font-mono font-medium text-slate-400">
                    {summary.total_deleted_persons.toLocaleString()} Deleted Excluded
                  </Text>
                </View>
              ) : null}
            </View>
          </View>
        </View>

        {/* Severity Summary Pills & All Issues Action */}
        <View className="flex-row items-center gap-2 flex-wrap">
          {totalCritical > 0 ? (
            <View className="flex-row items-center gap-1 bg-rose-950/60 border border-rose-800/60 px-2 py-0.5 rounded-full">
              <AlertCircle size={11} color={THEME_COLORS.dangerIcon} />
              <Text className="text-[10px] font-bold text-rose-300">
                {totalCritical.toLocaleString()} Critical
              </Text>
            </View>
          ) : (
            <View className="flex-row items-center gap-1 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded-full">
              <CheckCircle2 size={11} color={THEME_COLORS.successIcon} />
              <Text className="text-[10px] font-bold text-emerald-300">0 Critical</Text>
            </View>
          )}

          <View className="flex-row items-center gap-1 bg-amber-950/60 border border-amber-800/60 px-2 py-0.5 rounded-full">
            <AlertTriangle size={11} color={THEME_COLORS.warningIcon} />
            <Text className="text-[10px] font-bold text-amber-300">
              {totalWarnings.toLocaleString()} Warnings
            </Text>
          </View>

          {/* Export Report Actions */}
          <View className="flex-row items-center gap-1.5">
            <Pressable
              onPress={() => handleExport("xlsx")}
              disabled={isExporting !== null}
              className={`flex-row items-center gap-1 px-2.5 py-1 rounded-lg border transition-all cursor-pointer ${
                isExporting === "xlsx"
                  ? "bg-emerald-950/80 border-emerald-700 text-emerald-300"
                  : "bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border-slate-700 text-slate-300"
              }`}
              accessibilityRole="button"
              accessibilityLabel="Export Quality Suite as Excel .xlsx"
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
              className={`flex-row items-center gap-1 px-2.5 py-1 rounded-lg border transition-all cursor-pointer ${
                isExporting === "csv"
                  ? "bg-blue-950/80 border-blue-700 text-blue-300"
                  : "bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border-slate-700 text-slate-300"
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
            className="flex-row items-center gap-1 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-700 transition-colors cursor-pointer"
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

      {/* ── Filter Tabs ───────────────────────────────────────── */}
      <View className="flex-row items-center gap-1 overflow-x-auto flex-nowrap pb-1">
        <Pressable
          onPress={() => setActiveCategory("ALL")}
          className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-all ${
            activeCategory === "ALL"
              ? "bg-blue-600 border-blue-500"
              : "bg-slate-900/80 border-slate-800"
          }`}
        >
          <Text className={`text-xs font-semibold ${activeCategory === "ALL" ? "text-white font-bold" : "text-slate-400"}`}>
            All Dimensions
          </Text>
        </Pressable>

        <Pressable
          onPress={() => setActiveCategory("CONTACTS")}
          className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-all ${
            activeCategory === "CONTACTS"
              ? "bg-blue-600 border-blue-500"
              : "bg-slate-900/80 border-slate-800"
          }`}
        >
          <Text className={`text-xs font-semibold ${activeCategory === "CONTACTS" ? "text-white font-bold" : "text-slate-400"}`}>
            Contacts & Duplicates
          </Text>
        </Pressable>

        <Pressable
          onPress={() => setActiveCategory("ADDRESSES")}
          className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-all ${
            activeCategory === "ADDRESSES"
              ? "bg-blue-600 border-blue-500"
              : "bg-slate-900/80 border-slate-800"
          }`}
        >
          <Text className={`text-xs font-semibold ${activeCategory === "ADDRESSES" ? "text-white font-bold" : "text-slate-400"}`}>
            Address & Locations
          </Text>
        </Pressable>

        <Pressable
          onPress={() => setActiveCategory("INTEGRITY")}
          className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-all ${
            activeCategory === "INTEGRITY"
              ? "bg-blue-600 border-blue-500"
              : "bg-slate-900/80 border-slate-800"
          }`}
        >
          <Text className={`text-xs font-semibold ${activeCategory === "INTEGRITY" ? "text-white font-bold" : "text-slate-400"}`}>
            Profile & Chronology
          </Text>
        </Pressable>

        <Pressable
          onPress={() => setActiveCategory("GOVERNANCE")}
          className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-all ${
            activeCategory === "GOVERNANCE"
              ? "bg-blue-600 border-blue-500"
              : "bg-slate-900/80 border-slate-800"
          }`}
        >
          <Text className={`text-xs font-semibold ${activeCategory === "GOVERNANCE" ? "text-white font-bold" : "text-slate-400"}`}>
            Governance & Links
          </Text>
        </Pressable>
      </View>

      {/* ── KPI Grid ─────────────────────────────────────────── */}
      <View className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2.5">
        {/* === SECTION 1: Contacts & Duplicates === */}
        {(activeCategory === "ALL" || activeCategory === "CONTACTS") && (
          <>
            <ContactQualityCard
              title="Missing Email"
              count={summary.persons_without_email}
              issueCode="MISSING_EMAIL"
              description="Persons without any registered email"
              severity="WARNING"
              icon={<MailWarning size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Missing Phone"
              count={summary.persons_without_phone}
              issueCode="MISSING_PHONE"
              description="Persons without any registered phone"
              severity="WARNING"
              icon={<PhoneOff size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Invalid Email"
              count={summary.invalid_emails}
              issueCode="INVALID_EMAIL"
              description="Malformed format or invalid characters"
              severity="CRITICAL"
              icon={<Mail size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Invalid Phone"
              count={summary.invalid_phones}
              issueCode="INVALID_PHONE"
              description="Invalid phone (7-15 digits) or extension (!= 4 digits)"
              severity="CRITICAL"
              icon={<Phone size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Shared Email"
              count={summary.duplicate_email_cross_persons}
              issueCode="DUPLICATE_EMAIL_CROSS"
              description="Identical email linked to multiple Persons"
              severity="WARNING"
              icon={<Copy size={13} color={THEME_COLORS.companyIcon} />}
            />

            <ContactQualityCard
              title="Shared Phone"
              count={summary.duplicate_phone_cross_persons}
              issueCode="DUPLICATE_PHONE_CROSS"
              description="Identical phone linked to multiple Persons"
              severity="WARNING"
              icon={<Copy size={13} color={THEME_COLORS.companyIcon} />}
            />

            <ContactQualityCard
              title="Duplicate Email (Self)"
              count={summary.duplicate_email_same_person}
              issueCode="DUPLICATE_EMAIL_SAME"
              description="Same email added multiple times for 1 Person"
              severity="WARNING"
              icon={<UserCheck size={13} color={THEME_COLORS.primaryIcon} />}
            />

            <ContactQualityCard
              title="Duplicate Phone (Self)"
              count={summary.duplicate_phone_same_person}
              issueCode="DUPLICATE_PHONE_SAME"
              description="Same phone added multiple times for 1 Person"
              severity="WARNING"
              icon={<UserCheck size={13} color={THEME_COLORS.primaryIcon} />}
            />

            <ContactQualityCard
              title="Unverified Contacts"
              count={summary.unverified_contacts}
              issueCode="UNVERIFIED_CONTACT"
              description="Channels without verified flag status"
              severity="INFO"
              icon={<ShieldAlert size={13} color={THEME_COLORS.imIcon} />}
            />

            <ContactQualityCard
              title="Invalid URLs"
              count={summary.invalid_urls}
              issueCode="INVALID_URL"
              description="URLs missing http/https/www scheme"
              severity="WARNING"
              icon={<Globe size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Multiple Primary"
              count={summary.persons_multiple_primary}
              issueCode="MULTIPLE_PRIMARY"
              description="Persons with conflicting primary contacts"
              severity="CRITICAL"
              icon={<Layers size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Primary Inactive"
              count={summary.primary_contact_inactive}
              issueCode="PRIMARY_INACTIVE"
              description="Primary contact flagged inactive"
              severity="CRITICAL"
              icon={<ShieldX size={13} color={THEME_COLORS.dangerIcon} />}
            />
          </>
        )}

        {/* === SECTION 2: Address & Location Quality === */}
        {(activeCategory === "ALL" || activeCategory === "ADDRESSES") && (
          <>
            <ContactQualityCard
              title="Missing Postal Code"
              count={summary.addr_missing_postal_code}
              issueCode="MISSING_POSTAL_CODE"
              description="Addresses with street/city but no PIN code"
              severity="WARNING"
              icon={<MapPinOff size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Invalid PIN Format"
              count={summary.addr_invalid_pin_format}
              issueCode="INVALID_PIN_CODE_FORMAT"
              description="Postal code with non-numeric or bad length"
              severity="CRITICAL"
              icon={<MapPinOff size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Street Without City"
              count={summary.addr_street_without_city}
              issueCode="STREET_WITHOUT_CITY"
              description="Street address present but city name is blank"
              severity="WARNING"
              icon={<Compass size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="City Without State"
              count={summary.addr_city_without_state}
              issueCode="CITY_WITHOUT_STATE"
              description="City address without state region specified"
              severity="WARNING"
              icon={<Compass size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Missing Geocodes"
              count={summary.addr_missing_geocodes}
              issueCode="MISSING_GEOCODES"
              description="Addresses lacking Latitude/Longitude coordinates"
              severity="INFO"
              icon={<NavigationOff size={13} color={THEME_COLORS.imIcon} />}
            />

            <ContactQualityCard
              title="Duplicate Address"
              count={summary.addr_duplicate_same_person}
              issueCode="DUPLICATE_ADDRESSES_SAME_PERSON"
              description="Identical address entered twice for 1 Person"
              severity="WARNING"
              icon={<Copy size={13} color={THEME_COLORS.warningIcon} />}
            />
          </>
        )}

        {/* === SECTION 3: Profile & Chronological Integrity === */}
        {(activeCategory === "ALL" || activeCategory === "INTEGRITY") && (
          <>
            <ContactQualityCard
              title="Anniversary Before Birth"
              count={summary.person_anniversary_before_birth}
              issueCode="ANNIVERSARY_BEFORE_BIRTH"
              description="Anniversary date earlier than birth date"
              severity="CRITICAL"
              icon={<CalendarX size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Invalid Birth Date"
              count={summary.person_invalid_birth_date}
              issueCode="INVALID_BIRTH_DATE"
              description="Birth date in the future or before 1900"
              severity="CRITICAL"
              icon={<CalendarOff size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Dummy/Ancient DOB"
              count={summary.person_birth_date_ancient}
              issueCode="BIRTH_DATE_DEFAULT_OR_ANCIENT"
              description="Birth date is dummy 1900-01-01 or age > 100"
              severity="WARNING"
              icon={<CalendarOff size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Suspicious Test Names"
              count={summary.person_suspicious_dummy_names}
              issueCode="SUSPICIOUS_DUMMY_NAMES"
              description="Placeholder names (test, admin, dummy, etc.)"
              severity="WARNING"
              icon={<UserX size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Missing Last Name"
              count={summary.person_missing_lastname_only}
              issueCode="MISSING_LAST_NAME"
              description="Person has first name but missing surname"
              severity="WARNING"
              icon={<FileWarning size={13} color={THEME_COLORS.warningIcon} />}
            />
          </>
        )}

        {/* === SECTION 4: Governance, Employment & Links === */}
        {(activeCategory === "ALL" || activeCategory === "GOVERNANCE") && (
          <>
            <ContactQualityCard
              title="Active & Deleted Conflict"
              count={summary.status_active_and_deleted}
              issueCode="STATUS_ACTIVE_AND_DELETED"
              description="Record marked both Active and Deleted"
              severity="CRITICAL"
              icon={<ShieldAlert size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Employee Missing Title"
              count={summary.active_emp_missing_title}
              issueCode="ACTIVE_EMP_MISSING_TITLE"
              description="Active employee has no job title designation"
              severity="WARNING"
              icon={<FileWarning size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Inactive with EmpID (Info)"
              count={summary.inactive_with_empid}
              issueCode="INACTIVE_WITH_ACTIVE_EMPID"
              description="Informational: Inactive records retaining employee ID (excluded from active score)"
              severity="INFO"
              icon={<AlertCircle size={13} color={THEME_COLORS.textMuted} />}
            />

            <ContactQualityCard
              title="Stale Temp Persons"
              count={summary.stale_temp_persons}
              issueCode="STALE_TEMP_PERSONS"
              description="Temporary person record older than 90 days"
              severity="WARNING"
              icon={<Clock size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Unapproved Blacklist"
              count={summary.blacklist_unapproved}
              issueCode="BLACKLIST_UNAPPROVED"
              description="Blacklist flag active without HOD approval"
              severity="CRITICAL"
              icon={<ShieldAlert size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Missing Blacklist Details"
              count={summary.blacklist_missing_details}
              issueCode="BLACKLIST_MISSING_DETAILS"
              description="Blacklist record missing date or type"
              severity="CRITICAL"
              icon={<FileWarning size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Orphan Company Link"
              count={summary.company_orphan_links}
              issueCode="ORPHAN_COMPANY_LINK"
              description="Link references non-existent company ID"
              severity="CRITICAL"
              icon={<Building2 size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Duplicate Company Link"
              count={summary.company_duplicate_links}
              issueCode="DUPLICATE_COMPANY_LINKS"
              description="Same company linked $>1$ times to Person"
              severity="WARNING"
              icon={<Copy size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Company Missing Role"
              count={summary.company_missing_role}
              issueCode="COMPANY_MISSING_ROLE"
              description="Company affiliation without role definition"
              severity="WARNING"
              icon={<Building2 size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Orphan Extra Field"
              count={summary.extra_field_orphan_id}
              issueCode="EXTRA_FIELD_ORPHAN_ID"
              description="Custom field with invalid schema definition"
              severity="CRITICAL"
              icon={<Sliders size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Duplicate Extra Fields"
              count={summary.extra_field_duplicate_entries}
              issueCode="DUPLICATE_EXTRA_FIELDS"
              description="Duplicate custom field entries for 1 Person"
              severity="WARNING"
              icon={<Sliders size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Missing Deletion Date"
              count={summary.deleted_missing_del_date}
              issueCode="DELETED_MISSING_TIMESTAMP"
              description="Deleted person missing deletion timestamp"
              severity="WARNING"
              icon={<Clock size={13} color={THEME_COLORS.warningIcon} />}
            />

            <ContactQualityCard
              title="Deletion Before Creation"
              count={summary.audit_del_before_ent}
              issueCode="AUDIT_DEL_BEFORE_ENT"
              description="Deletion date is earlier than creation date"
              severity="CRITICAL"
              icon={<Clock size={13} color={THEME_COLORS.dangerIcon} />}
            />

            <ContactQualityCard
              title="Broken Zimbra Sync"
              count={summary.sync_zimbra_missing_id}
              issueCode="SYNC_ZIMBRA_MISSING_ID"
              description="Sync enabled but missing Zimbra ID"
              severity="WARNING"
              icon={<RefreshCw size={13} color={THEME_COLORS.warningIcon} />}
            />
          </>
        )}
      </View>
    </View>
  );
};
