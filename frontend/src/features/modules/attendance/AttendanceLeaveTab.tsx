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
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock,
  Download,
  FileText,
  Search,
  XCircle,
} from "lucide-react-native";
import { downloadLeaveApplicationsExport } from "@/api/attendance.api";
import { THEME_COLORS } from "@/constants/theme";
import {
  useLeaveApplications,
  useLeaveBalances,
  useLeaveOverview,
} from "@/hooks/useAttendance";

const LEAVE_STATUS_FILTERS = [
  { id: "", label: "All Requests" },
  { id: "APPROVED", label: "Approved" },
  { id: "PENDING", label: "Pending" },
  { id: "REJECTED", label: "Rejected" },
  { id: "CANCELLED", label: "Cancelled" },
];

interface AttendanceLeaveTabProps {
  deptId?: number;
  compId?: number;
}

export function AttendanceLeaveTab({ deptId, compId }: AttendanceLeaveTabProps = {}) {
  const [subView, setSubView] = useState<"applications" | "balances">("applications");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const pageSize = 20;

  const { data: overview } = useLeaveOverview();

  const effectiveSearch = searchTerm.trim() || (deptId ? `Dept#${deptId}` : compId ? `Comp#${compId}` : undefined);

  const { data: appsData, isLoading: isLoadingApps, isFetching: isFetchingApps } =
    useLeaveApplications(
      subView === "applications" ? statusFilter || undefined : undefined,
      effectiveSearch,
      pageSize,
      page * pageSize
    );

  const { data: balData, isLoading: isLoadingBal, isFetching: isFetchingBal } =
    useLeaveBalances(
      undefined,
      effectiveSearch,
      pageSize,
      page * pageSize
    );


  const handleExport = async () => {
    try {
      setIsExporting(true);
      await downloadLeaveApplicationsExport(
        statusFilter || undefined,
        searchTerm.trim() || undefined
      );
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const activeData = subView === "applications" ? appsData : balData;
  const totalPages = activeData ? Math.ceil(activeData.total / pageSize) : 0;

  return (
    <View className="gap-4 w-full">
      {/* ── Leave Pipeline Summary Cards ── */}
      {overview && (
        <View className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Total Applications</Text>
              <FileText size={16} color="#a855f7" />
            </View>
            <Text className="text-xl font-black text-white">{overview.total_leave_requests.toLocaleString()}</Text>
            <Text className="text-[10px] text-slate-500 mt-0.5">{overview.active_employees_on_leave} staff currently on leave</Text>
          </View>

          <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Approved</Text>
              <CheckCircle2 size={16} color="#34d399" />
            </View>
            <Text className="text-xl font-black text-emerald-400">{overview.approved_requests.toLocaleString()}</Text>
            <Text className="text-[10px] text-emerald-400/80 mt-0.5">{overview.approved_pct}% approval rate</Text>
          </View>

          <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Pending Approval</Text>
              <Clock size={16} color="#fbbf24" />
            </View>
            <Text className="text-xl font-black text-amber-400">{overview.pending_requests.toLocaleString()}</Text>
            <Text className="text-[10px] text-amber-400/80 mt-0.5">{overview.pending_pct}% in review</Text>
          </View>

          <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Rejected / Cancelled</Text>
              <XCircle size={16} color="#f87171" />
            </View>
            <Text className="text-xl font-black text-rose-400">
              {(overview.rejected_requests + overview.cancelled_requests).toLocaleString()}
            </Text>
            <Text className="text-[10px] text-rose-400/80 mt-0.5">
              {overview.rejected_pct}% rejected • {overview.cancelled_pct}% cancelled
            </Text>
          </View>
        </View>
      )}

      {/* ── Sub-view Selector & Toolbar ── */}
      <View className="flex-col md:flex-row items-stretch md:items-center justify-between gap-3 w-full">
        {/* Toggle Applications / Balances */}
        <View className="flex-row items-center bg-dark-card border border-dark-border p-1 rounded-xl self-start">
          <Pressable
            onPress={() => {
              setSubView("applications");
              setPage(0);
            }}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              subView === "applications" ? "bg-purple-600 shadow-md" : "hover:bg-dark-bg"
            }`}
          >
            <Text className={`text-xs font-bold ${subView === "applications" ? "text-white" : "text-slate-400"}`}>
              Leave Applications
            </Text>
          </Pressable>
          <Pressable
            onPress={() => {
              setSubView("balances");
              setPage(0);
            }}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              subView === "balances" ? "bg-purple-600 shadow-md" : "hover:bg-dark-bg"
            }`}
          >
            <Text className={`text-xs font-bold ${subView === "balances" ? "text-white" : "text-slate-400"}`}>
              Monthly Balances Ledger
            </Text>
          </Pressable>
        </View>

        {/* Search Bar */}
        <View className="flex-1 flex-row items-center bg-dark-card border border-dark-border rounded-xl px-3 py-2">
          <Search size={16} color={THEME_COLORS.textMuted} />
          <TextInput
            className="flex-1 ml-2 text-sm text-white placeholder:text-slate-500 font-sans outline-none"
            placeholder={
              subView === "applications"
                ? "Search employee code, name, leave type, reason..."
                : "Search employee code, name, period (e.g. 202607)..."
            }
            placeholderTextColor="#64748b"
            value={searchTerm}
            onChangeText={(t) => {
              setSearchTerm(t);
              setPage(0);
            }}
          />
        </View>

        {/* Export Button */}
        {subView === "applications" && (
          <Pressable
            className="flex-row items-center justify-center gap-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 px-4 py-2.5 rounded-xl self-start md:self-auto"
            onPress={handleExport}
            disabled={isExporting}
          >
            {isExporting ? <ActivityIndicator size="small" color="#c084fc" /> : <Download size={16} color="#c084fc" />}
            <Text className="text-xs font-bold text-purple-300">
              {isExporting ? "Exporting..." : "Export Requests"}
            </Text>
          </Pressable>
        )}
      </View>

      {/* Status Filter Pills for Applications */}
      {subView === "applications" && (
        <ScrollView horizontal showsHorizontalScrollIndicator={false} className="w-full">
          <View className="flex-row gap-2">
            {LEAVE_STATUS_FILTERS.map((f) => {
              const isSelected = statusFilter === f.id;
              return (
                <Pressable
                  key={f.id}
                  onPress={() => {
                    setStatusFilter(f.id);
                    setPage(0);
                  }}
                  className={`px-3 py-1.5 rounded-lg border text-xs font-semibold ${
                    isSelected
                      ? "bg-purple-600/30 border-purple-500 text-purple-300"
                      : "bg-dark-card border-dark-border text-slate-400 hover:border-slate-700"
                  }`}
                >
                  <Text className={`text-xs font-semibold ${isSelected ? "text-purple-300 font-bold" : "text-slate-400"}`}>
                    {f.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </ScrollView>
      )}

      {/* ── Table Container ── */}
      <View className="bg-dark-card border border-dark-border rounded-xl overflow-hidden shadow-sm w-full">
        {subView === "applications" ? (
          isLoadingApps ? (
            <View className="py-8 items-center justify-center">
              <ActivityIndicator size="large" color="#a855f7" />
              <Text className="text-xs text-slate-400 mt-2">Loading leave applications...</Text>
            </View>
          ) : !appsData || appsData.items.length === 0 ? (
            <View className="py-8 items-center justify-center">
              <FileText size={32} color={THEME_COLORS.textMuted} />
              <Text className="text-sm font-semibold text-slate-400 mt-2">No leave applications found.</Text>
            </View>
          ) : (
            <View className="w-full divide-y divide-dark-border">
              {/* Applications Header */}
              <View className="flex-row items-center px-4 py-3 bg-slate-900/60 border-b border-dark-border">
                <Text className="w-16 text-[11px] font-bold uppercase tracking-wider text-slate-400">ID</Text>
                <Text className="flex-1 min-w-[180px] text-[11px] font-bold uppercase tracking-wider text-slate-400">Applicant Identity</Text>
                <Text className="w-36 text-[11px] font-bold uppercase tracking-wider text-slate-400">Leave Type</Text>
                <Text className="w-48 text-[11px] font-bold uppercase tracking-wider text-slate-400">Duration Period</Text>
                <Text className="w-32 text-[11px] font-bold uppercase tracking-wider text-slate-400">Status</Text>
                <Text className="flex-1 min-w-[200px] text-[11px] font-bold uppercase tracking-wider text-slate-400">Reason / Remarks</Text>
              </View>

              {/* Applications Rows */}
              {appsData.items.map((row) => {
                const isApproved = row.status_desc === "Approved";
                const isPending = row.status_desc === "Pending";
                const isRejected = row.status_desc === "Rejected";
                return (
                  <View key={row.leave_request_id} className="flex-row items-center px-4 py-3.5 hover:bg-dark-bg/40 transition-colors">
                    <Text className="w-16 text-xs font-mono text-slate-400">#{row.leave_request_id}</Text>

                    <View className="flex-1 min-w-[180px] pr-3">
                      <Text className="text-xs font-bold text-white" numberOfLines={1}>{row.emp_name}</Text>
                      <Text className="text-[10px] text-slate-500 font-mono">Code: {row.emp_code || "N/A"}</Text>
                    </View>

                    <View className="w-36 pr-2">
                      <Text className="text-xs font-semibold text-purple-300" numberOfLines={1}>{row.leave_type_desc}</Text>
                      <Text className="text-[10px] text-slate-500 font-mono">{row.leave_days} Day(s)</Text>
                    </View>

                    <View className="w-48 pr-2">
                      <Text className="text-xs font-mono text-slate-300">{row.from_date} to {row.to_date}</Text>
                      <Text className="text-[10px] text-slate-500 font-mono">Applied: {row.request_date}</Text>
                    </View>

                    <View className="w-32 pr-2 flex-row items-center">
                      <View
                        className={`px-2.5 py-1 rounded-full border flex-row items-center gap-1.5 self-start ${
                          isApproved
                            ? "bg-emerald-950/90 border-emerald-700/60"
                            : isPending
                            ? "bg-amber-950/90 border-amber-700/60"
                            : isRejected
                            ? "bg-rose-950/90 border-rose-700/60"
                            : "bg-slate-900 border-slate-700"
                        }`}
                      >
                        <View
                          className={`w-1.5 h-1.5 rounded-full ${
                            isApproved
                              ? "bg-emerald-400"
                              : isPending
                              ? "bg-amber-400"
                              : isRejected
                              ? "bg-rose-400"
                              : "bg-slate-400"
                          }`}
                        />
                        <Text
                          className={`text-[10px] font-bold ${
                            isApproved
                              ? "text-emerald-300"
                              : isPending
                              ? "text-amber-300"
                              : isRejected
                              ? "text-rose-300"
                              : "text-slate-300"
                          }`}
                          numberOfLines={1}
                        >
                          {row.status_desc}
                        </Text>
                      </View>
                    </View>


                    <View className="flex-1 min-w-[200px]">
                      <Text className="text-xs text-slate-300 italic" numberOfLines={1}>
                        {row.reason || "No reason provided"}
                      </Text>
                    </View>
                  </View>
                );
              })}
            </View>
          )
        ) : (
          isLoadingBal ? (
            <View className="py-8 items-center justify-center">
              <ActivityIndicator size="large" color="#a855f7" />
              <Text className="text-xs text-slate-400 mt-2">Loading monthly leave balances...</Text>
            </View>
          ) : !balData || balData.items.length === 0 ? (
            <View className="py-8 items-center justify-center">
              <FileText size={32} color={THEME_COLORS.textMuted} />
              <Text className="text-sm font-semibold text-slate-400 mt-2">No leave balances found.</Text>
            </View>
          ) : (
            <View className="w-full divide-y divide-dark-border">
              {/* Balances Header */}
              <View className="flex-row items-center px-4 py-3 bg-slate-900/60 border-b border-dark-border">
                <Text className="w-16 text-[11px] font-bold uppercase tracking-wider text-slate-400">ID</Text>
                <Text className="flex-1 min-w-[180px] text-[11px] font-bold uppercase tracking-wider text-slate-400">Employee Identity</Text>
                <Text className="w-24 text-[11px] font-bold uppercase tracking-wider text-slate-400">YearMonth</Text>
                <Text className="w-32 text-[11px] font-bold uppercase tracking-wider text-slate-400 text-right">PL Balance</Text>
                <Text className="w-32 text-[11px] font-bold uppercase tracking-wider text-slate-400 text-right">CL Balance</Text>
                <Text className="w-32 text-[11px] font-bold uppercase tracking-wider text-slate-400 text-right">SL Balance</Text>
              </View>

              {/* Balances Rows */}
              {balData.items.map((row) => (
                <View key={row.bal_id} className="flex-row items-center px-4 py-3.5 hover:bg-dark-bg/40 transition-colors">
                  <Text className="w-16 text-xs font-mono text-slate-400">#{row.bal_id}</Text>

                  <View className="flex-1 min-w-[180px] pr-3">
                    <Text className="text-xs font-bold text-white" numberOfLines={1}>{row.emp_name}</Text>
                    <Text className="text-[10px] text-slate-500 font-mono">Code: {row.emp_code || "N/A"}</Text>
                  </View>

                  <View className="w-24 font-mono text-xs text-purple-300">
                    <Text className="text-xs font-mono text-purple-300">{row.year_month}</Text>
                  </View>

                  <View className="w-32 items-end">
                    <Text className={`text-xs font-mono font-bold ${row.net_pl_bal < 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {row.net_pl_bal}
                    </Text>
                    <Text className="text-[9px] text-slate-500 font-mono">Op: {row.op_pl} | Avail: {row.availed_pl}</Text>
                  </View>

                  <View className="w-32 items-end">
                    <Text className={`text-xs font-mono font-bold ${row.net_cl_bal < 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {row.net_cl_bal}
                    </Text>
                    <Text className="text-[9px] text-slate-500 font-mono">Op: {row.op_cl} | Avail: {row.availed_cl}</Text>
                  </View>

                  <View className="w-32 items-end">
                    <Text className={`text-xs font-mono font-bold ${row.net_sl_bal < 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {row.net_sl_bal}
                    </Text>
                    <Text className="text-[9px] text-slate-500 font-mono">Op: {row.op_sl} | Avail: {row.availed_sl}</Text>
                  </View>
                </View>
              ))}
            </View>
          )
        )}

        {/* Pagination Footer */}
        {activeData && activeData.total > 0 && (
          <View className="flex-row items-center justify-between px-4 py-3 bg-dark-bg/60 border-t border-dark-border w-full">
            <Text className="text-xs text-slate-400 font-medium">
              Showing {page * pageSize + 1}–
              {Math.min((page + 1) * pageSize, activeData.total)} of{" "}
              {activeData.total.toLocaleString()} records
              {(isFetchingApps || isFetchingBal) && " (Updating...)"}
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
