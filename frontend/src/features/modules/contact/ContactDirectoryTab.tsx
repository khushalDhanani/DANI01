import React, { useState } from "react";
import {
  ActivityIndicator,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  Mail,
  MapPin,
  Phone,
  Search,
  ShieldCheck,
  Smartphone,
  UserCheck,
  Users,
} from "lucide-react-native";
import { downloadContactDirectoryExport } from "@/api/contact.api";
import { THEME_COLORS } from "@/constants/theme";
import { useContactDirectory } from "@/hooks/useContact";
import type { ContactEmailFilter, ContactPhoneFilter } from "@/types/contact.types";

export function ContactDirectoryTab() {
  const [emailFilter, setEmailFilter] = useState<ContactEmailFilter | undefined>(undefined);
  const [phoneFilter, setPhoneFilter] = useState<ContactPhoneFilter | undefined>(undefined);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [isExporting, setIsExporting] = useState(false);
  const limit = 25;

  const { data, isLoading, isError } = useContactDirectory(
    emailFilter,
    phoneFilter,
    search || undefined,
    limit,
    page * limit
  );

  const totalPages = data ? Math.ceil(data.total / limit) : 0;

  const handleExport = async () => {
    try {
      setIsExporting(true);
      await downloadContactDirectoryExport(emailFilter, phoneFilter, search || undefined, "csv");
    } catch (err) {
      console.error("Export directory error:", err);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <View className="flex-1">
      {/* Filters & Search Header */}
      <View className="flex-row items-center gap-3 mb-3">
        {/* Search Box */}
        <View className="flex-1 flex-row items-center gap-2 bg-dark-card border border-dark-border px-3 py-2 rounded-xl">
          <Search size={14} color={THEME_COLORS.textMuted} />
          <TextInput
            className="flex-1 text-xs text-white"
            placeholder="Search name, code, email, phone, dept..."
            placeholderTextColor={THEME_COLORS.textDisabled}
            value={search}
            onChangeText={(txt) => {
              setSearch(txt);
              setPage(0);
            }}
          />
        </View>

        {/* Export Button */}
        <TouchableOpacity
          className="bg-blue-600 hover:bg-blue-500 px-3.5 py-2.5 rounded-xl flex-row items-center gap-2"
          disabled={isExporting}
          onPress={handleExport}
        >
          {isExporting ? (
            <ActivityIndicator size="small" color="#ffffff" />
          ) : (
            <>
              <Download size={13} color="#ffffff" />
              <Text className="text-xs font-bold text-white">Export CSV</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {/* Filter Pills Bar */}
      <View className="flex-row flex-wrap items-center gap-4 mb-4 pb-2 border-b border-dark-border">
        {/* Email Filters */}
        <View className="flex-row items-center gap-1.5">
          <Text className="text-[10px] uppercase font-bold text-slate-500 mr-1">Email:</Text>
          <TouchableOpacity
            onPress={() => {
              setEmailFilter(undefined);
              setPage(0);
            }}
            className={`px-2.5 py-1 rounded-md border ${
              !emailFilter ? "bg-blue-600 border-blue-400" : "bg-dark-card border-dark-border"
            }`}
          >
            <Text className={`text-[11px] font-bold ${!emailFilter ? "text-white" : "text-slate-400"}`}>All</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => {
              setEmailFilter("WITH_COMPANY_EMAIL");
              setPage(0);
            }}
            className={`px-2.5 py-1 rounded-md border flex-row items-center gap-1 ${
              emailFilter === "WITH_COMPANY_EMAIL" ? "bg-blue-600 border-blue-400" : "bg-dark-card border-dark-border"
            }`}
          >
            <Building2 size={11} color={emailFilter === "WITH_COMPANY_EMAIL" ? "#fff" : THEME_COLORS.textMuted} />
            <Text className={`text-[11px] font-bold ${emailFilter === "WITH_COMPANY_EMAIL" ? "text-white" : "text-slate-400"}`}>
              Company
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => {
              setEmailFilter("WITH_PERSONAL_EMAIL");
              setPage(0);
            }}
            className={`px-2.5 py-1 rounded-md border flex-row items-center gap-1 ${
              emailFilter === "WITH_PERSONAL_EMAIL" ? "bg-blue-600 border-blue-400" : "bg-dark-card border-dark-border"
            }`}
          >
            <UserCheck size={11} color={emailFilter === "WITH_PERSONAL_EMAIL" ? "#fff" : THEME_COLORS.textMuted} />
            <Text className={`text-[11px] font-bold ${emailFilter === "WITH_PERSONAL_EMAIL" ? "text-white" : "text-slate-400"}`}>
              Personal
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => {
              setEmailFilter("WITHOUT_ANY_EMAIL");
              setPage(0);
            }}
            className={`px-2.5 py-1 rounded-md border flex-row items-center gap-1 ${
              emailFilter === "WITHOUT_ANY_EMAIL" ? "bg-blue-600 border-blue-400" : "bg-dark-card border-dark-border"
            }`}
          >
            <Users size={11} color={emailFilter === "WITHOUT_ANY_EMAIL" ? "#fff" : THEME_COLORS.textMuted} />
            <Text className={`text-[11px] font-bold ${emailFilter === "WITHOUT_ANY_EMAIL" ? "text-white" : "text-slate-400"}`}>
              No Email
            </Text>
          </TouchableOpacity>
        </View>

        {/* Phone Filters */}
        <View className="flex-row items-center gap-1.5">
          <Text className="text-[10px] uppercase font-bold text-slate-500 mr-1">Phone:</Text>
          <TouchableOpacity
            onPress={() => {
              setPhoneFilter(undefined);
              setPage(0);
            }}
            className={`px-2.5 py-1 rounded-md border ${
              !phoneFilter ? "bg-blue-600 border-blue-400" : "bg-dark-card border-dark-border"
            }`}
          >
            <Text className={`text-[11px] font-bold ${!phoneFilter ? "text-white" : "text-slate-400"}`}>All</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => {
              setPhoneFilter("WITH_PRIMARY_PHONE");
              setPage(0);
            }}
            className={`px-2.5 py-1 rounded-md border flex-row items-center gap-1 ${
              phoneFilter === "WITH_PRIMARY_PHONE" ? "bg-blue-600 border-blue-400" : "bg-dark-card border-dark-border"
            }`}
          >
            <Smartphone size={11} color={phoneFilter === "WITH_PRIMARY_PHONE" ? "#fff" : THEME_COLORS.textMuted} />
            <Text className={`text-[11px] font-bold ${phoneFilter === "WITH_PRIMARY_PHONE" ? "text-white" : "text-slate-400"}`}>
              Has Phone
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => {
              setPhoneFilter("MISSING_PRIMARY_PHONE");
              setPage(0);
            }}
            className={`px-2.5 py-1 rounded-md border flex-row items-center gap-1 ${
              phoneFilter === "MISSING_PRIMARY_PHONE" ? "bg-blue-600 border-blue-400" : "bg-dark-card border-dark-border"
            }`}
          >
            <AlertTriangle size={11} color={phoneFilter === "MISSING_PRIMARY_PHONE" ? "#fff" : THEME_COLORS.warningIcon} />
            <Text className={`text-[11px] font-bold ${phoneFilter === "MISSING_PRIMARY_PHONE" ? "text-white" : "text-slate-400"}`}>
              Missing
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => {
              setPhoneFilter("WITH_ICE_CONTACT");
              setPage(0);
            }}
            className={`px-2.5 py-1 rounded-md border flex-row items-center gap-1 ${
              phoneFilter === "WITH_ICE_CONTACT" ? "bg-blue-600 border-blue-400" : "bg-dark-card border-dark-border"
            }`}
          >
            <ShieldCheck size={11} color={phoneFilter === "WITH_ICE_CONTACT" ? "#fff" : THEME_COLORS.successIcon} />
            <Text className={`text-[11px] font-bold ${phoneFilter === "WITH_ICE_CONTACT" ? "text-white" : "text-slate-400"}`}>
              ICE Contact
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Directory Content */}
      {isLoading ? (
        <View className="py-8 items-center justify-center">
          <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
          <Text className="text-xs text-slate-400 mt-2 font-medium">Loading workforce contact directory...</Text>
        </View>
      ) : isError ? (
        <View className="py-8 items-center justify-center">
          <AlertTriangle size={36} color={THEME_COLORS.dangerIcon} />
          <Text className="text-xs text-red-400 mt-2 font-medium">Failed to load workforce directory.</Text>
        </View>
      ) : data?.items && data.items.length > 0 ? (
        <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
          <View className="gap-2.5 pb-4">
            {data.items.map((emp) => (
              <View key={emp.emp_id} className="bg-dark-card border border-dark-border rounded-xl p-3.5">
                {/* Top Row: Code, Name, Dept, Location */}
                <View className="flex-row items-center justify-between mb-3 flex-wrap gap-2">
                  <View className="flex-row items-center gap-2.5">
                    <View className="px-2 py-1 rounded bg-blue-950/80 border border-blue-800/60">
                      <Text className="text-[11px] font-mono font-bold text-blue-400">
                        {emp.emp_code || `ID ${emp.emp_id}`}
                      </Text>
                    </View>
                    <View>
                      <Text className="text-xs font-bold text-white">{emp.full_name}</Text>
                      <Text className="text-[11px] text-slate-400">
                        {emp.designation || "Staff"} • {emp.department || "No Department"}
                      </Text>
                    </View>
                  </View>

                  {emp.location && (
                    <View className="flex-row items-center gap-1 bg-dark-bg border border-dark-border px-2 py-1 rounded-md">
                      <MapPin size={11} color={THEME_COLORS.textMuted} />
                      <Text className="text-[10px] text-slate-400 font-medium">{emp.location}</Text>
                    </View>
                  )}
                </View>

                {/* Middle Row: Communication Channels */}
                <View className="flex-row flex-wrap gap-2.5 bg-dark-bg/60 border border-dark-border/60 p-2.5 rounded-lg">
                  {/* Company Email */}
                  <View className="flex-1 min-w-[150px]">
                    <View className="flex-row items-center gap-1 mb-0.5">
                      <Building2 size={11} color={THEME_COLORS.companyIcon} />
                      <Text className="text-[9px] uppercase font-bold text-slate-500">Company Email</Text>
                    </View>
                    <Text className={`text-xs font-mono font-semibold ${emp.company_email ? "text-slate-200" : "text-slate-600"}`}>
                      {emp.company_email || "None"}
                    </Text>
                  </View>

                  {/* Personal Email */}
                  <View className="flex-1 min-w-[150px]">
                    <View className="flex-row items-center gap-1 mb-0.5">
                      <Mail size={11} color={THEME_COLORS.imIcon} />
                      <Text className="text-[9px] uppercase font-bold text-slate-500">Personal Email</Text>
                    </View>
                    <Text className={`text-xs font-mono font-semibold ${emp.personal_email ? "text-slate-200" : "text-slate-600"}`}>
                      {emp.personal_email || "None"}
                    </Text>
                  </View>

                  {/* Primary Phone */}
                  <View className="flex-1 min-w-[150px]">
                    <View className="flex-row items-center gap-1 mb-0.5">
                      <Phone size={11} color={THEME_COLORS.successIcon} />
                      <Text className="text-[9px] uppercase font-bold text-slate-500">Primary Phone</Text>
                      {emp.is_verified_phone1 && <CheckCircle2 size={10} color={THEME_COLORS.successIcon} />}
                    </View>
                    <Text className={`text-xs font-mono font-semibold ${emp.primary_phone ? "text-slate-200" : "text-red-400"}`}>
                      {emp.primary_phone || "Missing"}
                    </Text>
                  </View>

                  {/* ICE Emergency Contact */}
                  <View className="flex-1 min-w-[150px]">
                    <View className="flex-row items-center gap-1 mb-0.5">
                      <ShieldCheck size={11} color={THEME_COLORS.warningIcon} />
                      <Text className="text-[9px] uppercase font-bold text-slate-500">ICE Emergency</Text>
                    </View>
                    <Text className={`text-xs font-mono font-semibold ${emp.ice_mobile ? "text-slate-200" : "text-slate-600"}`}>
                      {emp.ice_mobile ? `${emp.ice_mobile} (${emp.ice_contact_name || "Nominee"})` : "None"}
                    </Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        </ScrollView>
      ) : (
        <View className="py-8 items-center justify-center gap-2">
          <Users size={32} color={THEME_COLORS.textMuted} />
          <Text className="text-xs text-slate-400 font-medium">No employees match the selected contact filters.</Text>
        </View>
      )}

      {/* Pagination Footer */}
      {data && data.total > 0 && (
        <View className="flex-row items-center justify-between pt-3 border-t border-dark-border">
          <Text className="text-xs text-slate-400">
            Showing {data.offset + 1}–{Math.min(data.offset + limit, data.total)} of {data.total.toLocaleString()} employees
          </Text>

          <View className="flex-row items-center gap-2">
            <TouchableOpacity
              className={`flex-row items-center gap-1 px-3 py-1.5 rounded-lg border ${
                page === 0 ? "bg-dark-bg border-dark-border opacity-40" : "bg-dark-card border-dark-border"
              }`}
              disabled={page === 0}
              onPress={() => setPage((p) => Math.max(0, p - 1))}
            >
              <ChevronLeft size={14} color={page === 0 ? THEME_COLORS.textDisabled : THEME_COLORS.textMuted} />
              <Text className={`text-xs font-bold ${page === 0 ? "text-slate-600" : "text-slate-300"}`}>Previous</Text>
            </TouchableOpacity>

            <Text className="text-xs text-slate-400 font-mono px-1">
              Page {page + 1} of {Math.max(1, totalPages)}
            </Text>

            <TouchableOpacity
              className={`flex-row items-center gap-1 px-3 py-1.5 rounded-lg border ${
                page >= totalPages - 1 ? "bg-dark-bg border-dark-border opacity-40" : "bg-dark-card border-dark-border"
              }`}
              disabled={page >= totalPages - 1}
              onPress={() => setPage((p) => p + 1)}
            >
              <Text className={`text-xs font-bold ${page >= totalPages - 1 ? "text-slate-600" : "text-slate-300"}`}>Next</Text>
              <ChevronRight size={14} color={page >= totalPages - 1 ? THEME_COLORS.textDisabled : THEME_COLORS.textMuted} />
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
}
