import React from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Globe,
  Lock,
  Shield,
  User,
  UserCheck,
  UserMinus,
  Users,
  UserX,
} from "lucide-react-native";
import { Text, View } from "react-native";
import { CoverageBar } from "../components/CoverageBar";
import { ContactQualitySection } from "./ContactQualitySection";
import { THEME_COLORS } from "@/constants/theme";
import type { PersonModuleMetricsResponse } from "@/types/modules.types";

interface PersonMetricsViewProps {
  metricsResponse?: PersonModuleMetricsResponse;
  isLoading?: boolean;
}

export const PersonMetricsView: React.FC<PersonMetricsViewProps> = ({
  metricsResponse,
  isLoading,
}) => {
  const metrics = metricsResponse?.metrics;
  const total = metrics?.total_persons ?? 0;

  if (isLoading) {
    return (
      <View className="gap-3.5 animate-pulse">
        <View className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <View key={i} className="h-16 bg-dark-card border border-dark-border rounded-lg" />
          ))}
        </View>
        <View className="h-48 bg-dark-card border border-dark-border rounded-lg" />
        <View className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          <View className="h-36 bg-dark-card border border-dark-border rounded-lg" />
          <View className="h-36 bg-dark-card border border-dark-border rounded-lg" />
        </View>
      </View>
    );
  }

  if (!metrics || total === 0) {
    return (
      <View className="bg-dark-card border border-dark-border rounded-lg p-6 items-center text-center">
        <Users size={28} color={THEME_COLORS.textMuted} />
        <Text className="text-sm font-bold text-white mt-2">No Person Data Available</Text>
        <Text className="text-xs text-slate-400 mt-0.5 max-w-sm">
          No records were found in the root table dbo.DLPersonMst.
        </Text>
      </View>
    );
  }

  return (
    <View className="gap-3.5">
      {/* ── 1. Compact Person Lifecycle Status Cards ────────── */}
      <View className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
        {/* Total Persons */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              Total Persons
            </Text>
            <Users size={12} color={THEME_COLORS.primaryIcon} />
          </View>
          <Text className="text-lg font-black text-white font-mono mt-1">
            {total.toLocaleString()}
          </Text>
          <Text className="text-[9px] text-slate-500 font-mono">100% catalog</Text>
        </View>

        {/* Active Persons */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">
              Active
            </Text>
            <CheckCircle2 size={12} color={THEME_COLORS.success} />
          </View>
          <Text className="text-lg font-black text-emerald-400 font-mono mt-1">
            {(metrics.active_persons ?? 0).toLocaleString()}
          </Text>
          <Text className="text-[9px] text-emerald-500/80 font-mono">
            {metrics.active_percent?.toFixed(1) ?? 0}% rate
          </Text>
        </View>

        {/* Inactive Persons */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              Inactive
            </Text>
            <UserMinus size={12} color={THEME_COLORS.textMuted} />
          </View>
          <Text className="text-lg font-black text-slate-300 font-mono mt-1">
            {(metrics.inactive_persons ?? 0).toLocaleString()}
          </Text>
          <Text className="text-[9px] text-slate-500 font-mono">
            {metrics.inactive_percent?.toFixed(1) ?? 0}% rate
          </Text>
        </View>

        {/* Deleted Persons */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-rose-400 tracking-wider">
              Deleted
            </Text>
            <UserX size={12} color={THEME_COLORS.dangerIcon} />
          </View>
          <Text className="text-lg font-black text-rose-400 font-mono mt-1">
            {(metrics.deleted_persons ?? 0).toLocaleString()}
          </Text>
          <Text className="text-[9px] text-rose-500/80 font-mono">
            {metrics.deleted_percent?.toFixed(1) ?? 0}% rate
          </Text>
        </View>

        {/* Temporary Persons */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-amber-400 tracking-wider">
              Temporary
            </Text>
            <AlertTriangle size={12} color={THEME_COLORS.warningIcon} />
          </View>
          <Text className="text-lg font-black text-amber-400 font-mono mt-1">
            {(metrics.temp_persons ?? 0).toLocaleString()}
          </Text>
          <Text className="text-[9px] text-amber-500/80 font-mono">
            {metrics.temp_percent?.toFixed(1) ?? 0}% rate
          </Text>
        </View>

        {/* Blacklisted Persons */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-purple-400 tracking-wider">
              Blacklisted
            </Text>
            <Shield size={12} color={THEME_COLORS.companyIcon} />
          </View>
          <Text className="text-lg font-black text-purple-400 font-mono mt-1">
            {(metrics.blacklist_persons ?? 0).toLocaleString()}
          </Text>
          <Text className="text-[9px] text-purple-500/80 font-mono">
            {metrics.blacklist_percent?.toFixed(1) ?? 0}% rate
          </Text>
        </View>
      </View>

      {/* ── 2. Business Mappings: Classification & Visibility ─────── */}
      <View className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {/* Visitors: PersonIsVisitor_Contact = 1 */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">
              Visitors (Type 1)
            </Text>
            <User size={12} color={THEME_COLORS.ownerIcon} />
          </View>
          <Text className="text-lg font-black text-indigo-300 font-mono mt-1">
            {(metrics.visitor_count ?? 0).toLocaleString()}
          </Text>
          <Text className="text-[9px] text-indigo-400/80 font-mono">
            {metrics.visitor_percent?.toFixed(1) ?? 0}% of catalog
          </Text>
        </View>

        {/* Contacts: PersonIsVisitor_Contact = 2 */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-blue-400 tracking-wider">
              Contacts (Type 2)
            </Text>
            <UserCheck size={12} color={THEME_COLORS.primaryIcon} />
          </View>
          <Text className="text-lg font-black text-blue-300 font-mono mt-1">
            {(metrics.contact_entity_count ?? 0).toLocaleString()}
          </Text>
          <Text className="text-[9px] text-blue-400/80 font-mono">
            {metrics.contact_entity_percent?.toFixed(1) ?? 0}% of catalog
          </Text>
        </View>

        {/* Public Contacts: PersonIsShareContact = 1 */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-teal-400 tracking-wider">
              Public Contacts (Share 1)
            </Text>
            <Globe size={12} color={THEME_COLORS.publicIcon} />
          </View>
          <Text className="text-lg font-black text-teal-300 font-mono mt-1">
            {(metrics.public_count ?? 0).toLocaleString()}
          </Text>
          <Text className="text-[9px] text-teal-400/80 font-mono">
            {metrics.public_percent?.toFixed(1) ?? 0}% public
          </Text>
        </View>

        {/* Private Contacts: PersonIsShareContact = 0 */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-2.5 flex-col justify-between">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              Private Contacts (Share 0)
            </Text>
            <Lock size={12} color={THEME_COLORS.textMuted} />
          </View>
          <Text className="text-lg font-black text-slate-300 font-mono mt-1">
            {(metrics.private_count ?? 0).toLocaleString()}
          </Text>
          <Text className="text-[9px] text-slate-500 font-mono">
            {metrics.private_percent?.toFixed(1) ?? 0}% private
          </Text>
        </View>
      </View>

      {/* ── 3. Contact Quality Analyzer Section ────────────────── */}
      <ContactQualitySection />

      {/* ── 3. Compact Child Table Coverage Grid ──────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-lg p-3 gap-2.5">
        <View className="flex-row items-center justify-between">
          <Text className="text-xs font-bold text-white uppercase tracking-wider">
            Child Dimension Coverage
          </Text>
          <Text className="text-[10px] text-slate-500 font-mono">
            Entities populated across 7 extension tables
          </Text>
        </View>

        <View className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-4 gap-y-2">
          {/* Address Coverage */}
          <CoverageBar
            label="Address Records"
            count={metrics.persons_with_address ?? 0}
            total={total}
            percent={metrics.address_coverage_percent ?? 0}
            colorScheme="amber"
            subtitle={`${(metrics.total_addresses ?? 0).toLocaleString()} total addresses`}
          />

          {/* Email Coverage */}
          <CoverageBar
            label="Email Channels"
            count={metrics.persons_with_email ?? 0}
            total={total}
            percent={metrics.email_coverage_percent ?? 0}
            colorScheme="blue"
          />

          {/* Phone Coverage */}
          <CoverageBar
            label="Phone Channels"
            count={metrics.persons_with_phone ?? 0}
            total={total}
            percent={metrics.phone_coverage_percent ?? 0}
            colorScheme="emerald"
          />

          {/* Overall Contact Coverage */}
          <CoverageBar
            label="Any Contact"
            count={metrics.persons_with_contact ?? 0}
            total={total}
            percent={metrics.contact_coverage_percent ?? 0}
            colorScheme="blue"
            subtitle={`${(metrics.total_contacts ?? 0).toLocaleString()} total channels`}
          />

          {/* Company Link Coverage */}
          <CoverageBar
            label="Company Affiliation"
            count={metrics.persons_with_company_link ?? 0}
            total={total}
            percent={metrics.company_link_coverage_percent ?? 0}
            colorScheme="purple"
            subtitle={`${(metrics.total_company_links ?? 0).toLocaleString()} total links`}
          />

          {/* Relationship Coverage */}
          <CoverageBar
            label="Inter-Personal Relations"
            count={metrics.persons_with_relationship ?? 0}
            total={total}
            percent={metrics.relationship_coverage_percent ?? 0}
            colorScheme="rose"
            subtitle={`${(metrics.total_relationships ?? 0).toLocaleString()} total relations`}
          />

          {/* Document Coverage */}
          <CoverageBar
            label="Document Attachments"
            count={metrics.persons_with_document ?? 0}
            total={total}
            percent={metrics.document_coverage_percent ?? 0}
            colorScheme="indigo"
            subtitle={`${(metrics.total_documents ?? 0).toLocaleString()} documents`}
          />

          {/* Extra Fields Coverage */}
          <CoverageBar
            label="Custom Attributes"
            count={metrics.persons_with_extra_field ?? 0}
            total={total}
            percent={metrics.extra_field_coverage_percent ?? 0}
            colorScheme="indigo"
            subtitle={`${(metrics.total_extra_fields ?? 0).toLocaleString()} values`}
          />

          {/* IM Coverage */}
          <CoverageBar
            label="Instant Messaging"
            count={metrics.persons_with_im ?? 0}
            total={total}
            percent={metrics.im_coverage_percent ?? 0}
            colorScheme="emerald"
            subtitle={`${(metrics.total_ims ?? 0).toLocaleString()} IM handles`}
          />
        </View>
      </View>

      {/* ── 4. Contact & Address Data Completeness & Health ──── */}
      <View className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Contact Channel Health */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-3 gap-2">
          <View className="flex-row items-center gap-1.5">
            <CheckCircle2 size={12} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white uppercase tracking-wider">
              Contact Health Breakdown
            </Text>
          </View>
          <View className="grid grid-cols-3 gap-2">
            <View className="bg-dark-bg/60 p-2 rounded border border-dark-border/40">
              <Text className="text-[9px] text-slate-400 uppercase font-semibold">Active</Text>
              <Text className="text-sm font-black text-emerald-400 font-mono mt-0.5">
                {(metrics.active_contacts ?? 0).toLocaleString()}
              </Text>
              <Text className="text-[9px] text-slate-500">
                {metrics.active_contacts_percent?.toFixed(1) ?? 0}%
              </Text>
            </View>

            <View className="bg-dark-bg/60 p-2 rounded border border-dark-border/40">
              <Text className="text-[9px] text-slate-400 uppercase font-semibold">Verified</Text>
              <Text className="text-sm font-black text-blue-400 font-mono mt-0.5">
                {(metrics.verified_contacts ?? 0).toLocaleString()}
              </Text>
              <Text className="text-[9px] text-slate-500">
                {metrics.verified_contacts_percent?.toFixed(1) ?? 0}%
              </Text>
            </View>

            <View className="bg-dark-bg/60 p-2 rounded border border-dark-border/40">
              <Text className="text-[9px] text-slate-400 uppercase font-semibold">Primary</Text>
              <Text className="text-sm font-black text-amber-400 font-mono mt-0.5">
                {(metrics.primary_contacts ?? 0).toLocaleString()}
              </Text>
              <Text className="text-[9px] text-slate-500">
                {metrics.primary_contacts_percent?.toFixed(1) ?? 0}%
              </Text>
            </View>
          </View>
        </View>

        {/* Address Quality & Geo Health */}
        <View className="bg-dark-card border border-dark-border rounded-lg p-3 gap-2">
          <View className="flex-row items-center gap-1.5">
            <CheckCircle2 size={12} color={THEME_COLORS.warningIcon} />
            <Text className="text-xs font-bold text-white uppercase tracking-wider">
              Address Health Breakdown
            </Text>
          </View>
          <View className="grid grid-cols-3 gap-2">
            <View className="bg-dark-bg/60 p-2 rounded border border-dark-border/40">
              <Text className="text-[9px] text-slate-400 uppercase font-semibold">Active</Text>
              <Text className="text-sm font-black text-emerald-400 font-mono mt-0.5">
                {(metrics.active_addresses ?? 0).toLocaleString()}
              </Text>
              <Text className="text-[9px] text-slate-500">
                {metrics.active_addresses_percent?.toFixed(1) ?? 0}%
              </Text>
            </View>

            <View className="bg-dark-bg/60 p-2 rounded border border-dark-border/40">
              <Text className="text-[9px] text-slate-400 uppercase font-semibold">Geo-Coded</Text>
              <Text className="text-sm font-black text-purple-400 font-mono mt-0.5">
                {(metrics.geo_addresses ?? 0).toLocaleString()}
              </Text>
              <Text className="text-[9px] text-slate-500">
                {metrics.geo_addresses_percent?.toFixed(1) ?? 0}%
              </Text>
            </View>

            <View className="bg-dark-bg/60 p-2 rounded border border-dark-border/40">
              <Text className="text-[9px] text-slate-400 uppercase font-semibold">Formatted</Text>
              <Text className="text-sm font-black text-amber-400 font-mono mt-0.5">
                {(metrics.formatted_addresses ?? 0).toLocaleString()}
              </Text>
              <Text className="text-[9px] text-slate-500">
                {metrics.formatted_addresses_percent?.toFixed(1) ?? 0}%
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* ── 5. Missing Data / Gap Telemetry ────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-lg p-3 gap-2">
        <View className="flex-row items-center gap-1.5">
          <AlertTriangle size={12} color={THEME_COLORS.dangerIcon} />
          <Text className="text-xs font-bold text-white uppercase tracking-wider">
            Critical Data Gaps
          </Text>
        </View>

        <View className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          <View className="bg-dark-bg/80 border border-slate-800 rounded p-2">
            <Text className="text-[9px] text-slate-400 uppercase font-semibold">No Email</Text>
            <Text className="text-sm font-black text-rose-400 font-mono mt-0.5">
              {(metrics.persons_without_email ?? 0).toLocaleString()}
            </Text>
            <Text className="text-[9px] text-slate-500">
              {total > 0
                ? `${(((metrics.persons_without_email ?? 0) / total) * 100).toFixed(1)}% missing`
                : "0%"}
            </Text>
          </View>

          <View className="bg-dark-bg/80 border border-slate-800 rounded p-2">
            <Text className="text-[9px] text-slate-400 uppercase font-semibold">No Phone</Text>
            <Text className="text-sm font-black text-rose-400 font-mono mt-0.5">
              {(metrics.persons_without_phone ?? 0).toLocaleString()}
            </Text>
            <Text className="text-[9px] text-slate-500">
              {total > 0
                ? `${(((metrics.persons_without_phone ?? 0) / total) * 100).toFixed(1)}% missing`
                : "0%"}
            </Text>
          </View>

          <View className="bg-dark-bg/80 border border-slate-800 rounded p-2">
            <Text className="text-[9px] text-slate-400 uppercase font-semibold">No Address</Text>
            <Text className="text-sm font-black text-amber-400 font-mono mt-0.5">
              {(metrics.persons_without_address ?? 0).toLocaleString()}
            </Text>
            <Text className="text-[9px] text-slate-500">
              {total > 0
                ? `${(((metrics.persons_without_address ?? 0) / total) * 100).toFixed(1)}% missing`
                : "0%"}
            </Text>
          </View>

          <View className="bg-dark-bg/80 border border-slate-800 rounded p-2">
            <Text className="text-[9px] text-slate-400 uppercase font-semibold">No Custom Fields</Text>
            <Text className="text-sm font-black text-slate-300 font-mono mt-0.5">
              {(metrics.persons_without_extra_field ?? 0).toLocaleString()}
            </Text>
            <Text className="text-[9px] text-slate-500">
              {total > 0
                ? `${(((metrics.persons_without_extra_field ?? 0) / total) * 100).toFixed(1)}% missing`
                : "0%"}
            </Text>
          </View>

          <View className="bg-dark-bg/80 border border-slate-800 rounded p-2">
            <Text className="text-[9px] text-slate-400 uppercase font-semibold">No Relations</Text>
            <Text className="text-sm font-black text-slate-300 font-mono mt-0.5">
              {(metrics.persons_without_relationship ?? 0).toLocaleString()}
            </Text>
            <Text className="text-[9px] text-slate-500">
              {total > 0
                ? `${(((metrics.persons_without_relationship ?? 0) / total) * 100).toFixed(1)}% missing`
                : "0%"}
            </Text>
          </View>

          <View className="bg-dark-bg/80 border border-slate-800 rounded p-2">
            <Text className="text-[9px] text-slate-400 uppercase font-semibold">No Documents</Text>
            <Text className="text-sm font-black text-slate-300 font-mono mt-0.5">
              {(metrics.persons_without_document ?? 0).toLocaleString()}
            </Text>
            <Text className="text-[9px] text-slate-500">
              {total > 0
                ? `${(((metrics.persons_without_document ?? 0) / total) * 100).toFixed(1)}% missing`
                : "0%"}
            </Text>
          </View>
        </View>
      </View>

      {/* ── 6. Compact Privacy Notice & Telemetry Footer ──────── */}
      <View className="flex-row items-center justify-between p-2.5 bg-dark-card border border-dark-border rounded-lg text-xs text-slate-500">
        <View className="flex-row items-center gap-1.5">
          <CheckCircle2 size={12} color={THEME_COLORS.successIcon} />
          <Text className="text-[10px] text-slate-400">
            Privacy-safe: Aggregate telemetry only. No PII is loaded or exposed.
          </Text>
        </View>
        <Text className="text-[9px] text-slate-500 font-mono">
          Computed in {metricsResponse?.duration_ms ?? 0}ms
        </Text>
      </View>
    </View>
  );
};
