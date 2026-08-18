import React, { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import {
  ChevronLeft,
  ChevronRight,
  Download,
  KeyRound,
  Search,
  Shield,
  ShieldCheck,
  Smartphone,
  User,
  Users,
} from "lucide-react-native";
import { downloadSecurityUsersExport } from "@/api/security.api";
import { THEME_COLORS } from "@/constants/theme";
import { useSecurityUsers } from "@/hooks/useSecurity";

const STATUS_FILTERS = [
  { id: "", label: "All Accounts" },
  { id: "LINKED", label: "Staff Logins" },
  { id: "UNLINKED", label: "External / Candidate" },
  { id: "ADMIN", label: "Master Admins" },
  { id: "MFA", label: "MFA Enabled" },
  { id: "ACTIVE", label: "Active Only" },
  { id: "INACTIVE", label: "Inactive" },
  { id: "DELETED", label: "Deleted" },
];

export function SecurityUsersTab() {
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const pageSize = 20;

  const { data: usersData, isLoading, isFetching } = useSecurityUsers(
    undefined,
    statusFilter || undefined,
    searchTerm.trim() || undefined,
    pageSize,
    page * pageSize
  );

  const handleFilterChange = (filterId: string) => {
    setStatusFilter(filterId);
    setPage(0);
  };

  const handleSearchChange = (text: string) => {
    setSearchTerm(text);
    setPage(0);
  };

  const handleExport = async () => {
    try {
      setIsExporting(true);
      await downloadSecurityUsersExport(
        undefined,
        statusFilter || undefined,
        searchTerm.trim() || undefined
      );
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const totalPages = usersData ? Math.ceil(usersData.total / pageSize) : 0;

  return (
    <View className="gap-4 w-full">
      {/* Search & Export Toolbar */}
      <View className="flex-col md:flex-row items-stretch md:items-center justify-between gap-3 w-full">
        {/* Search Bar */}
        <View className="flex-1 flex-row items-center bg-dark-card border border-dark-border rounded-xl px-3 py-2">
          <Search size={16} color={THEME_COLORS.textMuted} />
          <TextInput
            className="flex-1 ml-2 text-sm text-white placeholder:text-slate-500 font-sans outline-none"
            placeholder="Search username, email, phone, employee code, name, role..."
            placeholderTextColor="#64748b"
            value={searchTerm}
            onChangeText={handleSearchChange}
          />
        </View>

        {/* Export Button */}
        <Pressable
          className="flex-row items-center justify-center gap-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 px-4 py-2.5 rounded-xl self-start md:self-auto"
          onPress={handleExport}
          disabled={isExporting}
        >
          {isExporting ? (
            <ActivityIndicator size="small" color="#c084fc" />
          ) : (
            <Download size={16} color="#c084fc" />
          )}
          <Text className="text-xs font-bold text-purple-300">
            {isExporting ? "Exporting..." : "Export Directory"}
          </Text>
        </Pressable>
      </View>

      {/* Filter Pills */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} className="w-full">
        <View className="flex-row gap-2">
          {STATUS_FILTERS.map((f) => {
            const isSelected = statusFilter === f.id;
            return (
              <Pressable
                key={f.id}
                onPress={() => handleFilterChange(f.id)}
                className={`px-3 py-1.5 rounded-lg border text-xs font-semibold ${
                  isSelected
                    ? "bg-purple-600/30 border-purple-500 text-purple-300"
                    : "bg-dark-card border-dark-border text-slate-400 hover:border-slate-700"
                }`}
              >
                <Text
                  className={`text-xs font-semibold ${
                    isSelected ? "text-purple-300 font-bold" : "text-slate-400"
                  }`}
                >
                  {f.label}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </ScrollView>

      {/* Directory Table */}
      <View className="bg-dark-card border border-dark-border rounded-xl overflow-hidden shadow-sm w-full">
        {isLoading ? (
          <View className="py-8 items-center justify-center">
            <ActivityIndicator size="large" color="#a855f7" />
            <Text className="text-xs text-slate-400 mt-2">Loading user accounts...</Text>
          </View>
        ) : !usersData || usersData.items.length === 0 ? (
          <View className="py-8 items-center justify-center">
            <User size={32} color={THEME_COLORS.textMuted} />
            <Text className="text-sm font-semibold text-slate-400 mt-2">No user accounts found.</Text>
            <Text className="text-xs text-slate-500 mt-1">Try adjusting your filters or search keyword.</Text>
          </View>
        ) : (
          <View className="w-full divide-y divide-dark-border">
            {/* Header */}
            <View className="flex-row items-center px-4 py-3 bg-slate-900/60 border-b border-dark-border">
              <Text className="w-16 text-[11px] font-bold uppercase tracking-wider text-slate-400">ID</Text>
              <Text className="flex-1 min-w-[180px] text-[11px] font-bold uppercase tracking-wider text-slate-400">User Identity</Text>
              <Text className="w-40 text-[11px] font-bold uppercase tracking-wider text-slate-400">Assigned Role</Text>
              <Text className="flex-1 min-w-[180px] text-[11px] font-bold uppercase tracking-wider text-slate-400">Linked Employee</Text>
              <Text className="w-36 text-[11px] font-bold uppercase tracking-wider text-slate-400">Security Flags</Text>
              <Text className="w-32 text-[11px] font-bold uppercase tracking-wider text-slate-400 text-right">Last API Access</Text>
            </View>

            {/* Rows */}
            {usersData.items.map((u) => {
              const isOnline = u.is_active && !u.is_deleted;
              return (
                <View
                  key={u.user_id}
                  className="flex-row items-center px-4 py-3.5 hover:bg-dark-bg/40 transition-colors"
                >
                  {/* User ID */}
                  <Text className="w-16 text-xs font-mono text-slate-400">#{u.user_id}</Text>

                  {/* User Identity */}
                  <View className="flex-1 min-w-[180px] pr-3">
                    <View className="flex-row items-center gap-1.5 flex-wrap">
                      <Text className="text-xs font-bold text-white" numberOfLines={1}>
                        {u.username || "Anonymous User"}
                      </Text>
                      {!isOnline && (
                        <View className="px-1.5 py-0.5 rounded bg-red-950/80 border border-red-800/60">
                          <Text className="text-[9px] font-bold text-red-400">
                            {u.is_deleted ? "DELETED" : "INACTIVE"}
                          </Text>
                        </View>
                      )}
                    </View>
                    <Text className="text-[11px] text-slate-400 mt-0.5" numberOfLines={1}>
                      {u.user_email || u.user_mobile || "No contact mapped"}
                    </Text>
                  </View>

                  {/* Assigned Role */}
                  <View className="w-40 pr-3">
                    <View className="flex-row items-center gap-1">
                      <KeyRound size={12} color="#a855f7" />
                      <Text className="text-xs font-medium text-purple-300" numberOfLines={1}>
                        {u.role_desc || "No Role"}
                      </Text>
                    </View>
                  </View>

                  {/* Linked Employee */}
                  <View className="flex-1 min-w-[180px] pr-3">
                    {u.emp_id ? (
                      <View>
                        <View className="flex-row items-center gap-1.5 flex-wrap">
                          <Text className="text-xs font-semibold text-slate-200" numberOfLines={1}>
                            {u.emp_name}
                          </Text>
                          <View
                            className={`px-1.5 py-0.2 rounded border ${
                              u.emp_status === "ACTIVE"
                                ? "bg-emerald-950/60 border-emerald-800/60"
                                : u.emp_status === "RESIGNED"
                                ? "bg-amber-950/60 border-amber-800/60"
                                : "bg-rose-950/60 border-rose-800/60"
                            }`}
                          >
                            <Text
                              className={`text-[9px] font-bold ${
                                u.emp_status === "ACTIVE"
                                  ? "text-emerald-400"
                                  : u.emp_status === "RESIGNED"
                                  ? "text-amber-400"
                                  : "text-rose-400"
                              }`}
                            >
                              {u.emp_status}
                            </Text>
                          </View>
                        </View>
                        <Text className="text-[10px] text-slate-500 font-mono">Emp #{u.emp_id} • Code: {u.emp_code || "N/A"}</Text>
                      </View>
                    ) : (
                      <View className="flex-row items-center gap-1">
                        <Users size={12} color="#64748b" />
                        <Text className="text-xs text-slate-500 italic">External Login</Text>
                      </View>
                    )}
                  </View>

                  {/* Security Flags (Admin, MFA, Mobile, Devices) */}
                  <View className="w-36 flex-row items-center gap-1.5">
                    {u.is_master_admin && (
                      <View className="px-1.5 py-0.5 rounded bg-amber-950/80 border border-amber-800/60">
                        <Text className="text-[9px] font-bold text-amber-400">ADMIN</Text>
                      </View>
                    )}
                    {u.is_mfa_enabled ? (
                      <ShieldCheck size={14} color={THEME_COLORS.successIcon} />
                    ) : (
                      <Shield size={14} color="#64748b" />
                    )}
                    {u.is_mobile_app_user && (
                      <Smartphone size={14} color="#38bdf8" />
                    )}
                    {u.registered_devices_count > 0 && (
                      <Text className="text-[10px] font-mono text-slate-400">
                        {u.registered_devices_count} dev
                      </Text>
                    )}
                  </View>

                  {/* Last API Access */}
                  <View className="w-32 items-end">
                    <Text className="text-[11px] font-mono text-slate-400">
                      {u.last_access_api ? u.last_access_api.substring(0, 10) : "Never"}
                    </Text>
                  </View>
                </View>
              );
            })}
          </View>
        )}

        {/* Pagination Controls */}
        {usersData && usersData.total > 0 && (
          <View className="flex-row items-center justify-between px-4 py-3 bg-dark-bg/60 border-t border-dark-border w-full">
            <Text className="text-xs text-slate-400 font-medium">
              Showing {page * pageSize + 1}–
              {Math.min((page + 1) * pageSize, usersData.total)} of{" "}
              {usersData.total.toLocaleString()} accounts
              {isFetching && " (Updating...)"}
            </Text>

            <View className="flex-row items-center gap-2">
              <Pressable
                className={`p-1.5 rounded-lg border border-dark-border ${
                  page === 0 ? "opacity-30" : "bg-dark-card hover:border-slate-600"
                }`}
                onPress={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
              >
                <ChevronLeft size={16} color={THEME_COLORS.primaryIcon} />
              </Pressable>
              <Text className="text-xs text-slate-300 font-mono px-1">
                {page + 1} / {Math.max(1, totalPages)}
              </Text>
              <Pressable
                className={`p-1.5 rounded-lg border border-dark-border ${
                  page + 1 >= totalPages ? "opacity-30" : "bg-dark-card hover:border-slate-600"
                }`}
                onPress={() => setPage((p) => p + 1)}
                disabled={page + 1 >= totalPages}
              >
                <ChevronRight size={16} color={THEME_COLORS.primaryIcon} />
              </Pressable>
            </View>
          </View>
        )}
      </View>
    </View>
  );
}
