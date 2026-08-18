import React, { useState } from "react";
import { ActivityIndicator, FlatList, Pressable, Text, TextInput, View } from "react-native";
import {
  ChevronLeft,
  ChevronRight,
  Download,
  Eye,
  Lock,
  Search,
  UserX,
  X,
} from "lucide-react-native";
import { employeeApi } from "@/api/employee.api";
import { THEME_COLORS } from "@/constants/theme";
import { useEmployeeRecords } from "@/hooks/useEmployee";

interface EmployeeRosterTabProps {
  onSelectEmployee: (empId: number) => void;
  initialStatus?: string;
  compId?: number;
}

export const EmployeeRosterTab: React.FC<EmployeeRosterTabProps> = ({
  onSelectEmployee,
  initialStatus = "ACTIVE",
  compId,
}) => {
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>(initialStatus);
  const [pageOffset, setPageOffset] = useState<number>(0);
  const pageSize = 25;

  const { data: recordsData, isLoading } = useEmployeeRecords({
    search: searchTerm || undefined,
    status: statusFilter,
    limit: pageSize,
    offset: pageOffset,
    compId: compId,
  });


  const total = recordsData?.total ?? 0;
  const totalPages = Math.ceil(total / pageSize) || 1;
  const currentPage = Math.floor(pageOffset / pageSize) + 1;

  const handleExportCSV = async () => {
    await employeeApi.exportRecords({
      status: statusFilter,
      search: searchTerm || undefined,
      format: "csv",
    });
  };

  return (
    <View className="gap-4">
      {/* ── Search & Filter Controls ────────────────────────── */}
      <View className="flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-dark-card border border-dark-border p-3.5 rounded-xl">
        {/* Search Input */}
        <View className="flex-1 flex-row items-center bg-dark-bg border border-dark-border rounded-lg px-3 py-2">
          <Search size={15} color={THEME_COLORS.textMuted} />
          <TextInput
            value={searchTerm}
            onChangeText={(txt) => {
              setSearchTerm(txt);
              setPageOffset(0);
            }}
            placeholder="Search employees by name, employee code, email, or phone..."
            placeholderTextColor={THEME_COLORS.textMuted}
            className="flex-1 text-xs text-white ml-2 outline-none"
          />
          {searchTerm ? (
            <Pressable onPress={() => setSearchTerm("")}>
              <X size={14} color={THEME_COLORS.textMuted} />
            </Pressable>
          ) : null}
        </View>

        {/* Status Filter Buttons */}
        <View className="flex-row items-center gap-1.5 overflow-x-auto">
          {["ACTIVE", "INACTIVE", "RESIGNED", "DELETED", "ALL"].map((st) => (
            <Pressable
              key={st}
              onPress={() => {
                setStatusFilter(st);
                setPageOffset(0);
              }}
              className={`px-3 py-1.5 rounded-lg border text-xs font-bold transition-all ${
                statusFilter === st
                  ? "bg-blue-600 border-blue-400 text-white"
                  : "bg-dark-bg border-dark-border text-slate-400"
              }`}
            >
              <Text className={`text-xs font-bold ${statusFilter === st ? "text-white" : "text-slate-400"}`}>
                {st}
              </Text>
            </Pressable>
          ))}

          {/* Export CSV Button */}
          <Pressable
            onPress={handleExportCSV}
            accessibilityRole="button"
            accessibilityLabel="Export employee roster CSV"
            className="flex-row items-center gap-1.5 bg-dark-bg border border-dark-border px-3 py-1.5 rounded-lg ml-1 hover:border-slate-500"
          >
            <Download size={13} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-slate-200">Export</Text>
          </Pressable>
        </View>
      </View>

      {/* ── Employee Records Table / List ───────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl overflow-hidden shadow-sm">
        {/* Table Header (Desktop) */}
        <View className="hidden md:flex flex-row items-center justify-between p-3 border-b border-dark-border bg-slate-900/60 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          <Text className="w-16">Badge</Text>
          <Text className="flex-1">Employee Name &amp; Role</Text>
          <Text className="w-48">Department &amp; Site</Text>
          <Text className="w-40">Functional Lead</Text>
          <Text className="w-24 text-center">Status</Text>
          <Text className="w-20 text-right">Actions</Text>
        </View>

        {/* List Body */}
        {isLoading ? (
          <View className="py-20 items-center justify-center">
            <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs text-slate-400 mt-2 font-medium">Fetching employee roster...</Text>
          </View>
        ) : !recordsData?.items.length ? (
          <View className="py-8 items-center justify-center">
            <UserX size={36} color={THEME_COLORS.textMuted} />
            <Text className="text-sm font-bold text-white mt-2">No employees match this filter</Text>
            <Text className="text-xs text-slate-400 mt-1">Try adjusting the search query or status filter.</Text>
          </View>
        ) : (
          <FlatList
            data={recordsData.items}
            keyExtractor={(item) => item.emp_id.toString()}
            renderItem={({ item }) => (
              <Pressable
                onPress={() => onSelectEmployee(item.emp_id)}
                accessibilityRole="button"
                accessibilityLabel={`Inspect profile for ${item.full_name}`}
                className="p-3 border-b border-dark-border/60 hover:bg-slate-800/40 transition-all flex-col md:flex-row md:items-center justify-between gap-2"
              >
                {/* Badge / Code */}
                <View className="w-16">
                  <View className="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded self-start">
                    <Text className="text-[10px] font-mono font-bold text-blue-300">
                      {item.emp_code || `ID:${item.emp_id}`}
                    </Text>
                  </View>
                </View>

                {/* Name & Contact */}
                <View className="flex-1">
                  <Text className="text-xs font-bold text-white">{item.full_name}</Text>
                  <View className="flex-row items-center gap-2 mt-0.5">
                    <Text className="text-[11px] text-slate-400">{item.designation_name || "Official Position Unassigned"}</Text>
                    {item.company_email ? (
                      <Text className="text-[10px] font-mono text-slate-500">• {item.company_email}</Text>
                    ) : null}
                  </View>
                </View>

                {/* Department & Site */}
                <View className="w-48">
                  <Text className="text-[11px] font-medium text-slate-300 truncate">
                    {item.department_name || "No Department"}
                  </Text>
                  <Text className="text-[10px] text-slate-400">{item.location_name || "Site N/A"}</Text>
                </View>

                {/* Manager */}
                <View className="w-40">
                  <Text className="text-[11px] text-slate-300 truncate">
                    {item.functional_mgr_name || "Unassigned"}
                  </Text>
                  {item.user_name ? (
                    <View className="flex-row items-center gap-1 mt-0.5">
                      <Lock size={10} color={THEME_COLORS.primaryIcon} />
                      <Text className="text-[10px] font-mono text-blue-400 truncate">{item.user_name}</Text>
                    </View>
                  ) : null}
                </View>

                {/* Status */}
                <View className="w-24 items-center">
                  <View
                    className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                      item.is_active
                        ? "bg-emerald-950 border border-emerald-800 text-emerald-300"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    <Text className={`text-[9px] font-bold ${item.is_active ? "text-emerald-300" : "text-slate-400"}`}>
                      {item.is_active ? "ACTIVE" : "INACTIVE"}
                    </Text>
                  </View>
                </View>

                {/* Actions */}
                <View className="w-20 items-end">
                  <View className="flex-row items-center gap-1 bg-dark-bg border border-dark-border px-2 py-1 rounded-lg">
                    <Eye size={12} color={THEME_COLORS.primaryIcon} />
                    <Text className="text-[10px] font-bold text-slate-300">View</Text>
                  </View>
                </View>
              </Pressable>
            )}
          />
        )}

        {/* ── Pagination Footer ───────────────────────────────── */}
        <View className="p-3 border-t border-dark-border bg-slate-900 flex-row items-center justify-between">
          <Text className="text-xs text-slate-400 font-mono">
            Showing {Math.min(pageOffset + 1, total)} - {Math.min(pageOffset + pageSize, total)} of {total.toLocaleString()} records
          </Text>

          <View className="flex-row items-center gap-2">
            <Pressable
              disabled={pageOffset === 0}
              onPress={() => setPageOffset(Math.max(0, pageOffset - pageSize))}
              className={`p-1.5 rounded-lg border ${
                pageOffset === 0
                  ? "bg-dark-bg border-dark-border opacity-40"
                  : "bg-dark-bg border-dark-border hover:bg-slate-800"
              }`}
            >
              <ChevronLeft size={16} color={THEME_COLORS.textMuted} />
            </Pressable>

            <Text className="text-xs font-mono text-slate-300">
              Page {currentPage} of {totalPages}
            </Text>

            <Pressable
              disabled={pageOffset + pageSize >= total}
              onPress={() => setPageOffset(pageOffset + pageSize)}
              className={`p-1.5 rounded-lg border ${
                pageOffset + pageSize >= total
                  ? "bg-dark-bg border-dark-border opacity-40"
                  : "bg-dark-bg border-dark-border hover:bg-slate-800"
              }`}
            >
              <ChevronRight size={16} color={THEME_COLORS.textMuted} />
            </Pressable>
          </View>
        </View>
      </View>
    </View>
  );
};
