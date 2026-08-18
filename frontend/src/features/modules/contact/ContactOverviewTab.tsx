import React from "react";
import {
  ActivityIndicator,
  ScrollView,
  Text,
  View,
} from "react-native";
import {
  AlertTriangle,
  AtSign,
  Building2,
  CheckCircle2,
  Globe,
  Mail,
  MapPin,
  Phone,
  PhoneCall,
  ShieldCheck,
  Smartphone,
  UserCheck,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { useContactOverview } from "@/hooks/useContact";

export function ContactOverviewTab() {
  const { data: overview, isLoading, isError } = useContactOverview();

  if (isLoading) {
    return (
      <View className="py-8 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Loading contact & email intelligence...</Text>
      </View>
    );
  }

  if (isError || !overview) {
    return (
      <View className="py-8 items-center justify-center">
        <AlertTriangle size={36} color={THEME_COLORS.dangerIcon} />
        <Text className="text-sm text-red-400 mt-3 font-medium">Failed to load contact intelligence metrics.</Text>
      </View>
    );
  }

  const { email_metrics: email, phone_metrics: phone, address_metrics: addr } = overview;

  return (
    <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
      {/* Top Banner */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3 mb-4 flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <View className="flex-row items-center gap-4 flex-1">
          <View className="w-12 h-12 rounded-xl bg-blue-950/80 border border-blue-800/60 items-center justify-center">
            <Mail size={24} color={THEME_COLORS.primaryIcon} />
          </View>
          <View className="flex-1">
            <Text className="text-base font-bold text-white mb-1">Workforce Communication Intelligence</Text>
            <Text className="text-xs text-slate-400 leading-relaxed">
              Multi-channel auditing for {overview.total_active_employees.toLocaleString()} active employees across Corporate & Personal Emails, Mobile Phones, Emergency ICE, and Postal Addresses.
            </Text>
          </View>
        </View>
        <View className="bg-dark-bg border border-dark-border rounded-xl px-5 py-2.5 items-center self-start md:self-auto">
          <Text className="text-xl font-bold text-blue-400">{overview.total_active_employees}</Text>
          <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Active Staff</Text>
        </View>
      </View>

      {/* SECTION 1: EMAIL CHANNELS */}
      <Text className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-3">Email Communication Channels</Text>
      <View className="flex-row flex-wrap gap-4 mb-4">
        {/* Any Email */}
        <View className="flex-1 min-w-[220px] bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-semibold text-slate-400">With Any Email</Text>
            <View className="w-7 h-7 rounded-lg bg-sky-950/80 border border-sky-800/60 items-center justify-center">
              <AtSign size={14} color={THEME_COLORS.imIcon} />
            </View>
          </View>
          <Text className="text-xl font-black text-white mb-2">{email.with_any_email.toLocaleString()}</Text>
          <View className="flex-row items-center justify-between">
            <Text className="text-xs font-bold text-sky-400">{email.with_any_email_pct}% coverage</Text>
            <Text className="text-[11px] text-slate-500">Corp or Personal</Text>
          </View>
        </View>

        {/* Company Email */}
        <View className="flex-1 min-w-[220px] bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-semibold text-slate-400">Company Email (@aether)</Text>
            <View className="w-7 h-7 rounded-lg bg-purple-950/80 border border-purple-800/60 items-center justify-center">
              <Building2 size={14} color={THEME_COLORS.companyIcon} />
            </View>
          </View>
          <Text className="text-xl font-black text-white mb-2">{email.with_company_email.toLocaleString()}</Text>
          <View className="flex-row items-center justify-between">
            <Text className="text-xs font-bold text-purple-400">{email.with_company_email_pct}%</Text>
            <Text className="text-[11px] text-slate-500">Office & Desk Staff</Text>
          </View>
        </View>

        {/* Personal Email */}
        <View className="flex-1 min-w-[220px] bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-semibold text-slate-400">Personal Email</Text>
            <View className="w-7 h-7 rounded-lg bg-emerald-950/80 border border-emerald-800/60 items-center justify-center">
              <UserCheck size={14} color={THEME_COLORS.successIcon} />
            </View>
          </View>
          <Text className="text-xl font-black text-white mb-2">{email.with_personal_email.toLocaleString()}</Text>
          <View className="flex-row items-center justify-between">
            <Text className="text-xs font-bold text-emerald-400">{email.with_personal_email_pct}%</Text>
            <Text className="text-[11px] text-slate-500">Gmail / Yahoo / Others</Text>
          </View>
        </View>

        {/* Without Any Email */}
        <View className="flex-1 min-w-[220px] bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-semibold text-slate-400">Without Any Email</Text>
            <View className="w-7 h-7 rounded-lg bg-amber-950/80 border border-amber-800/60 items-center justify-center">
              <Users size={14} color={THEME_COLORS.warningIcon} />
            </View>
          </View>
          <Text className="text-xl font-black text-white mb-2">{email.without_any_email.toLocaleString()}</Text>
          <View className="flex-row items-center justify-between">
            <Text className="text-xs font-bold text-amber-400">{email.without_any_email_pct}%</Text>
            <Text className="text-[11px] text-slate-500">Plant & Field Staff</Text>
          </View>
        </View>
      </View>

      {/* SECTION 2: PHONE & MOBILE CHANNELS */}
      <Text className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-3">Phone & Mobile Coverage</Text>
      <View className="flex-row flex-wrap gap-4 mb-4">
        {/* Primary Phone */}
        <View className="flex-1 min-w-[220px] bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-semibold text-slate-400">Primary Mobile</Text>
            <View className="w-7 h-7 rounded-lg bg-emerald-950/80 border border-emerald-800/60 items-center justify-center">
              <Smartphone size={14} color={THEME_COLORS.successIcon} />
            </View>
          </View>
          <Text className="text-xl font-black text-white mb-2">{phone.with_primary_phone.toLocaleString()}</Text>
          <View className="flex-row items-center justify-between">
            <Text className="text-xs font-bold text-emerald-400">{phone.with_primary_phone_pct}%</Text>
            <Text className="text-[11px] text-slate-500">{phone.primary_phone_verified} Verified ({phone.primary_phone_verified_pct}%)</Text>
          </View>
        </View>

        {/* Secondary Phone */}
        <View className="flex-1 min-w-[220px] bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-semibold text-slate-400">Secondary Mobile</Text>
            <View className="w-7 h-7 rounded-lg bg-blue-950/80 border border-blue-800/60 items-center justify-center">
              <PhoneCall size={14} color={THEME_COLORS.primaryIcon} />
            </View>
          </View>
          <Text className="text-xl font-black text-white mb-2">{phone.with_secondary_phone.toLocaleString()}</Text>
          <View className="flex-row items-center justify-between">
            <Text className="text-xs font-bold text-blue-400">{phone.with_secondary_phone_pct}%</Text>
            <Text className="text-[11px] text-slate-500">Backup Contact</Text>
          </View>
        </View>

        {/* Correspondence Phone */}
        <View className="flex-1 min-w-[220px] bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-semibold text-slate-400">Correspondence Phone</Text>
            <View className="w-7 h-7 rounded-lg bg-fuchsia-950/80 border border-fuchsia-800/60 items-center justify-center">
              <Phone size={14} color={THEME_COLORS.relationIcon} />
            </View>
          </View>
          <Text className="text-xl font-black text-white mb-2">{phone.with_corr_phone1.toLocaleString()}</Text>
          <View className="flex-row items-center justify-between">
            <Text className="text-xs font-bold text-fuchsia-400">{phone.with_corr_phone1_pct}%</Text>
            <Text className="text-[11px] text-slate-500">Official Letters</Text>
          </View>
        </View>

        {/* Missing Phone */}
        <View className="flex-1 min-w-[220px] bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-semibold text-slate-400">Missing All Phones</Text>
            <View className="w-7 h-7 rounded-lg bg-red-950/80 border border-red-800/60 items-center justify-center">
              <AlertTriangle size={14} color={THEME_COLORS.dangerIcon} />
            </View>
          </View>
          <Text className={`text-xl font-black mb-2 ${phone.without_any_phone > 0 ? "text-red-400" : "text-white"}`}>
            {phone.without_any_phone}
          </Text>
          <View className="flex-row items-center justify-between">
            <Text className="text-xs font-bold text-red-400">{phone.without_any_phone_pct}% critical</Text>
            <Text className="text-[11px] text-slate-500">Zero Reachability</Text>
          </View>
        </View>
      </View>

      {/* SECTION 3: ADDRESS & EMERGENCY ICE CONTACTS */}
      <Text className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-3">Postal Address & Emergency Response</Text>
      <View className="flex-col md:flex-row gap-4 mb-4">
        <View className="flex-1 bg-dark-card border border-dark-border rounded-xl p-3">
          <View className="flex-row items-center gap-2 mb-4 pb-3 border-b border-dark-border">
            <MapPin size={18} color={THEME_COLORS.primaryIcon} />
            <Text className="text-sm font-bold text-white">Postal Address Coverage</Text>
          </View>
          <View className="flex-row justify-between items-center py-2">
            <Text className="text-xs text-slate-400">Permanent Residence Address:</Text>
            <Text className="text-xs font-bold text-white">{addr.with_permanent_address.toLocaleString()} ({addr.with_permanent_address_pct}%)</Text>
          </View>
          <View className="flex-row justify-between items-center py-2">
            <Text className="text-xs text-slate-400">Correspondence / Local Address:</Text>
            <Text className="text-xs font-bold text-white">{addr.with_correspondence_address.toLocaleString()} ({addr.with_correspondence_address_pct}%)</Text>
          </View>
          <View className="flex-row justify-between items-center py-2">
            <Text className="text-xs text-slate-400">Permanent Postal PIN Code:</Text>
            <Text className="text-xs font-bold text-white">{addr.with_permanent_pincode.toLocaleString()}</Text>
          </View>
          <View className="flex-row justify-between items-center py-2">
            <Text className="text-xs text-slate-400">Correspondence Postal PIN Code:</Text>
            <Text className="text-xs font-bold text-white">{addr.with_correspondence_pincode.toLocaleString()}</Text>
          </View>
        </View>

        <View className="flex-1 bg-dark-card border border-dark-border rounded-xl p-3">
          <View className="flex-row items-center gap-2 mb-4 pb-3 border-b border-dark-border">
            <ShieldCheck size={18} color={THEME_COLORS.successIcon} />
            <Text className="text-sm font-bold text-white">Emergency (ICE) Contacts</Text>
          </View>
          <Text className="text-xl font-black text-emerald-400 my-1">{addr.with_ice_emergency_contact}</Text>
          <Text className="text-xs text-slate-400 leading-relaxed mb-4">
            Active staff with In Case of Emergency (ICE) mobile contact registered in Family Records ({addr.with_ice_emergency_contact_pct}%).
          </Text>
          <View className="flex-row items-center gap-2 bg-emerald-950/60 border border-emerald-800/40 px-3 py-2 rounded-lg self-start">
            <CheckCircle2 size={13} color={THEME_COLORS.successIcon} />
            <Text className="text-[11px] font-bold text-emerald-300">Stored in dbo.EmployeeFamilyDet.ICEMobileNo</Text>
          </View>
        </View>
      </View>

      {/* SECTION 4: DOMAIN DISTRIBUTION */}
      <Text className="text-xs uppercase font-bold text-slate-400 tracking-wider mb-3">Email Domain Distribution</Text>
      <View className="bg-dark-card border border-dark-border rounded-xl p-3">
        <View className="flex-row items-center gap-2 mb-4">
          <Globe size={18} color={THEME_COLORS.primaryIcon} />
          <Text className="text-sm font-bold text-white">Workforce Email Providers & Domains</Text>
        </View>

        {overview.domain_breakdown.map((d) => (
          <View key={d.domain} className="mb-4">
            <View className="flex-row justify-between items-center mb-1.5">
              <Text className="text-xs font-semibold text-white">{d.domain}</Text>
              <Text className="text-xs text-slate-400 font-mono">
                {d.count.toLocaleString()} emps ({d.percentage}%)
              </Text>
            </View>
            <View className="h-2 rounded-full bg-dark-bg overflow-hidden">
              <View
                className="h-2 rounded-full"
                style={{
                  width: `${Math.min(100, d.percentage)}%`,
                  backgroundColor: d.domain.includes("aether")
                    ? THEME_COLORS.primary
                    : d.domain.includes("gmail")
                    ? "#ea4335"
                    : d.domain.includes("yahoo")
                    ? "#7c3aed"
                    : THEME_COLORS.accent,
                }}
              />
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}
