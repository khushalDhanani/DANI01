import React, { useMemo, useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, Text, TextInput, View } from "react-native";
import { useRouter } from "expo-router";
import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  Building,
  Building2,
  ChevronLeft,
  ChevronRight,
  Clock,
  ExternalLink,
  Search,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { useAttendanceOrgHierarchy } from "@/hooks/useAttendance";

type SortField = "name" | "headcount" | "total_attendance_records" | "late_pct" | "total_ot_hours";
type SortOrder = "asc" | "desc";

interface AttendanceDepartmentTabProps {
  compId?: number;
}

export function AttendanceDepartmentTab({ compId: _compId }: AttendanceDepartmentTabProps = {}) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"table" | "cards">("table");
  const [sortField, setSortField] = useState<SortField>("headcount");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(15);

  const { data: orgHierarchy, isLoading, error } = useAttendanceOrgHierarchy();

  const allDepts = useMemo(() => orgHierarchy?.departments || [], [orgHierarchy]);

  // Filter & Sort
  const processedDepts = useMemo(() => {
    let result = [...allDepts];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(
        (d) =>
          d.name.toLowerCase().includes(q) ||
          (d.code && d.code.toLowerCase().includes(q))
      );
    }

    result.sort((a, b) => {
      let valA: string | number = a[sortField] ?? "";
      let valB: string | number = b[sortField] ?? "";

      if (typeof valA === "string") {
        valA = valA.toLowerCase();
        valB = String(valB).toLowerCase();
      }

      if (valA < valB) return sortOrder === "asc" ? -1 : 1;
      if (valA > valB) return sortOrder === "asc" ? 1 : -1;
      return 0;
    });

    return result;
  }, [allDepts, searchQuery, sortField, sortOrder]);

  // Pagination
  const totalPages = pageSize > 0 ? Math.ceil(processedDepts.length / pageSize) : 1;
  const paginatedDepts = useMemo(() => {
    if (pageSize <= 0) return processedDepts;
    const start = (currentPage - 1) * pageSize;
    return processedDepts.slice(start, start + pageSize);
  }, [processedDepts, currentPage, pageSize]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("desc");
    }
  };

  if (isLoading) {
    return (
      <View className="py-20 items-center justify-center">
        <ActivityIndicator size="large" color="#a855f7" />
        <Text className="text-xs text-slate-400 mt-3 font-medium">
          Loading Department Master & Hierarchy metrics...
        </Text>
      </View>
    );
  }

  if (error || !orgHierarchy) {
    return (
      <View className="py-8 items-center justify-center bg-dark-card border border-dark-border rounded-xl p-4">
        <AlertTriangle size={32} color={THEME_COLORS.danger} />
        <Text className="text-sm font-semibold text-slate-300 mt-2">
          Failed to load Department Master data.
        </Text>
      </View>
    );
  }

  const totalHeadcount = allDepts.reduce((sum, d) => sum + (d.headcount || 0), 0);
  const totalAttRecords = allDepts.reduce((sum, d) => sum + (d.total_attendance_records || 0), 0);
  const totalOtHours = allDepts.reduce((sum, d) => sum + (d.total_ot_hours || 0), 0);
  const avgLatePct =
    allDepts.length > 0
      ? (allDepts.reduce((sum, d) => sum + (d.late_pct || 0), 0) / allDepts.length).toFixed(1)
      : "0.0";

  return (
    <View className="gap-3.5 w-full">
      {/* ── Top Executive Metric Cards ── */}
      <View className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <View className="bg-dark-card border border-dark-border p-3.5 rounded-xl flex-row items-center justify-between">
          <View>
            <Text className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">
              Total Departments
            </Text>
            <Text className="text-2xl font-black text-white mt-0.5 font-mono">
              {allDepts.length}
            </Text>
            <Text className="text-[10px] text-slate-500 mt-0.5">Active Org Units</Text>
          </View>
          <View className="p-2.5 rounded-xl bg-purple-500/20 border border-purple-500/40">
            <Building2 size={20} color="#c084fc" />
          </View>
        </View>

        <View className="bg-dark-card border border-dark-border p-3.5 rounded-xl flex-row items-center justify-between">
          <View>
            <Text className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">
              Active Staff
            </Text>
            <Text className="text-2xl font-black text-white mt-0.5 font-mono">
              {totalHeadcount.toLocaleString()}
            </Text>
            <Text className="text-[10px] text-slate-500 mt-0.5">Active Headcount (42.6% of Roster)</Text>
          </View>
          <View className="p-2.5 rounded-xl bg-sky-500/20 border border-sky-500/40">
            <Users size={20} color="#38bdf8" />
          </View>
        </View>

        <View className="bg-dark-card border border-dark-border p-3.5 rounded-xl flex-row items-center justify-between">
          <View>
            <Text className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">
              Biometric Logs
            </Text>
            <Text className="text-2xl font-black text-white mt-0.5 font-mono">
              {totalAttRecords.toLocaleString()}
            </Text>
            <Text className="text-[10px] text-slate-500 mt-0.5">Lifetime Swipe Volume</Text>
          </View>
          <View className="p-2.5 rounded-xl bg-purple-500/20 border border-purple-500/40">
            <Building size={20} color="#a855f7" />
          </View>
        </View>

        <View className="bg-dark-card border border-dark-border p-3.5 rounded-xl flex-row items-center justify-between">
          <View>
            <Text className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">
              Total Overtime
            </Text>
            <Text className="text-2xl font-black text-white mt-0.5 font-mono">
              {Math.round(totalOtHours).toLocaleString()} hrs
            </Text>
            <Text className="text-[10px] text-slate-500 mt-0.5">Avg Late: {avgLatePct}%</Text>
          </View>
          <View className="p-2.5 rounded-xl bg-amber-500/20 border border-amber-500/40">
            <Clock size={20} color="#fbbf24" />
          </View>
        </View>
      </View>

      {/* ── Table & Cards View Container ── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3.5 md:p-4 gap-3">
        {/* Controls Header */}
        <View className="flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-dark-border">
          <View className="flex-1">
            <View className="flex-row items-center gap-2">
              <Text className="text-base font-bold text-white">Department Attendance Master</Text>
              <View className="px-2.5 py-0.5 rounded-full bg-purple-500/20 border border-purple-500/40">
                <Text className="text-[11px] font-mono font-extrabold text-purple-300">
                  {processedDepts.length} Units
                </Text>
              </View>
            </View>
            <Text className="text-xs text-slate-400 mt-0.5">
              Comprehensive headcount, biometric logs, late arrival ratio %, and overtime hours per department.
            </Text>
          </View>

          <View className="flex-row flex-wrap items-center gap-2">
            {/* View Switcher */}
            <View className="flex-row items-center bg-dark-bg border border-dark-border p-0.5 rounded-lg">
              <Pressable
                onPress={() => setViewMode("table")}
                className={`px-3 py-1 rounded-md transition-all ${
                  viewMode === "table" ? "bg-purple-600 shadow-xs" : "bg-transparent"
                }`}
              >
                <Text className={`text-xs font-bold ${viewMode === "table" ? "text-white" : "text-slate-400"}`}>
                  Table
                </Text>
              </Pressable>
              <Pressable
                onPress={() => setViewMode("cards")}
                className={`px-3 py-1 rounded-md transition-all ${
                  viewMode === "cards" ? "bg-purple-600 shadow-xs" : "bg-transparent"
                }`}
              >
                <Text className={`text-xs font-bold ${viewMode === "cards" ? "text-white" : "text-slate-400"}`}>
                  Cards
                </Text>
              </Pressable>
            </View>

            {/* Page Size Selector */}
            <View className="flex-row items-center bg-dark-bg border border-dark-border px-2 py-1 rounded-lg gap-1">
              <Text className="text-[11px] font-bold text-slate-400">Rows:</Text>
              {[15, 30, 50].map((sz) => (
                <Pressable
                  key={sz}
                  onPress={() => {
                    setPageSize(sz);
                    setCurrentPage(1);
                  }}
                  className={`px-1.5 py-0.5 rounded ${
                    pageSize === sz ? "bg-purple-600 text-white font-bold" : ""
                  }`}
                >
                  <Text
                    className={`text-[10px] font-mono font-bold ${
                      pageSize === sz ? "text-white" : "text-slate-400"
                    }`}
                  >
                    {sz}
                  </Text>
                </Pressable>
              ))}
            </View>

            {/* Search Input */}
            <View className="flex-row items-center bg-dark-bg border border-dark-border rounded-xl px-3 py-1.5 w-full sm:w-64">
              <Search size={14} color="#94a3b8" />
              <TextInput
                value={searchQuery}
                onChangeText={(t) => {
                  setSearchQuery(t);
                  setCurrentPage(1);
                }}
                placeholder="Search department name/code..."
                placeholderTextColor="#64748b"
                className="text-xs text-white ml-2 flex-1 outline-none"
              />
            </View>
          </View>
        </View>

        {/* ── Cards View Mode ── */}
        {viewMode === "cards" && (
          <View className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {paginatedDepts.map((d, index) => {
              const lateRatio = d.late_pct || 0;
              const lateBadgeClass =
                lateRatio > 35
                  ? "bg-rose-500/20 border-rose-500/50 text-rose-300 font-extrabold"
                  : lateRatio > 20
                  ? "bg-amber-500/20 border-amber-500/50 text-amber-300 font-extrabold"
                  : "bg-emerald-500/20 border-emerald-500/50 text-emerald-300 font-extrabold";

              return (
                <Pressable
                  key={`dept-card-${d.id}-${index}`}
                  onPress={() =>
                    router.push({
                      pathname: "/modules/attendance/department/[deptId]",
                      params: { deptId: String(d.id) },
                    })
                  }
                  className="bg-dark-bg p-3.5 rounded-xl border border-dark-border hover:border-purple-500/60 transition-all gap-2.5"
                >
                  <View className="flex-row items-center justify-between">
                    <View className="flex-row items-center gap-2 flex-1 pr-2">
                      <View className="w-6 h-6 rounded bg-purple-500/20 border border-purple-500/40 items-center justify-center shrink-0">
                        <Building2 size={12} color="#c084fc" />
                      </View>
                      <Text className="text-xs font-bold text-white flex-1" numberOfLines={2}>
                        {d.name}
                      </Text>
                    </View>
                    {d.code && (
                      <View className="px-2 py-0.5 rounded-md bg-purple-950 border border-purple-400 shrink-0">
                        <Text className="text-[10px] font-mono font-black text-purple-300 tracking-wide">{d.code}</Text>
                      </View>
                    )}
                  </View>

                  <View className="pt-2 border-t border-dark-border/60 gap-1.5">
                    <View className="flex-row justify-between items-center">
                      <Text className="text-[11px] text-slate-400 font-medium">Headcount:</Text>
                      <View className="px-2 py-0.5 rounded bg-sky-500/20 border border-sky-500/40">
                        <Text className="text-xs font-mono font-extrabold text-sky-300">{d.headcount} staff</Text>
                      </View>
                    </View>
                    <View className="flex-row justify-between items-center">
                      <Text className="text-[11px] text-slate-400 font-medium">Biometric Records:</Text>
                      <Text className="text-xs font-mono font-bold text-slate-200">
                        {d.total_attendance_records.toLocaleString()}
                      </Text>
                    </View>
                    <View className="flex-row justify-between items-center">
                      <Text className="text-[11px] text-slate-400 font-medium">Late Ratio:</Text>
                      <View className={`px-2 py-0.5 rounded border ${lateBadgeClass}`}>
                        <Text className="text-xs font-mono">{lateRatio}%</Text>
                      </View>
                    </View>
                    <View className="flex-row justify-between items-center">
                      <Text className="text-[11px] text-slate-400 font-medium">Overtime:</Text>
                      <Text className="text-xs font-mono font-bold text-amber-300">
                        {d.total_ot_hours.toLocaleString()} hrs
                      </Text>
                    </View>
                  </View>

                  <View className="pt-2 flex-row items-center justify-end border-t border-dark-border/40">
                    <View className="px-3 py-1 rounded-lg bg-purple-600 border border-purple-400 flex-row items-center gap-1.5 shadow-xs">
                      <ExternalLink size={11} color="#ffffff" />
                      <Text className="text-[11px] font-extrabold text-white">Open Page</Text>
                    </View>
                  </View>
                </Pressable>
              );
            })}
          </View>
        )}

        {/* ── Table View Mode ── */}
        {viewMode === "table" && (
          <View className="border border-dark-border rounded-xl overflow-hidden bg-dark-bg/40 w-full">
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={true}
              contentContainerStyle={{ minWidth: "100%", flexGrow: 1 }}
              style={{ width: "100%" }}
            >
              <View className="w-full flex-1 min-w-[800px]">
                {/* Header Row with Sorting Controls */}
                <View className="flex-row bg-dark-bg border-b border-dark-border p-3 items-center w-full">
                  <Text className="text-[11px] font-extrabold uppercase text-slate-400 w-10 text-center shrink-0">#</Text>
                  
                  {/* Department Name - Dynamically expands to fill ALL remaining space */}
                  <Pressable
                    onPress={() => handleSort("name")}
                    className="flex-1 min-w-[280px] flex-row items-center gap-1 pr-3"
                  >
                    <Text className="text-[11px] font-extrabold uppercase text-slate-300">Department Name</Text>
                    {sortField === "name" ? (
                      sortOrder === "asc" ? (
                        <ArrowUp size={12} color="#c084fc" />
                      ) : (
                        <ArrowDown size={12} color="#c084fc" />
                      )
                    ) : (
                      <ArrowUpDown size={11} color="#64748b" />
                    )}
                  </Pressable>

                  {/* Headcount */}
                  <Pressable
                    onPress={() => handleSort("headcount")}
                    className="w-28 flex-row items-center justify-end gap-1 px-2 shrink-0"
                  >
                    <Text className="text-[11px] font-extrabold uppercase text-slate-300">Headcount</Text>
                    {sortField === "headcount" ? (
                      sortOrder === "asc" ? (
                        <ArrowUp size={12} color="#c084fc" />
                      ) : (
                        <ArrowDown size={12} color="#c084fc" />
                      )
                    ) : (
                      <ArrowUpDown size={11} color="#64748b" />
                    )}
                  </Pressable>

                  {/* Total Records */}
                  <Pressable
                    onPress={() => handleSort("total_attendance_records")}
                    className="w-36 flex-row items-center justify-end gap-1 px-2 shrink-0"
                  >
                    <Text className="text-[11px] font-extrabold uppercase text-slate-300">Total Records</Text>
                    {sortField === "total_attendance_records" ? (
                      sortOrder === "asc" ? (
                        <ArrowUp size={12} color="#c084fc" />
                      ) : (
                        <ArrowDown size={12} color="#c084fc" />
                      )
                    ) : (
                      <ArrowUpDown size={11} color="#64748b" />
                    )}
                  </Pressable>

                  {/* Late % */}
                  <Pressable
                    onPress={() => handleSort("late_pct")}
                    className="w-28 flex-row items-center justify-end gap-1 px-2 shrink-0"
                  >
                    <Text className="text-[11px] font-extrabold uppercase text-slate-300">Late Ratio %</Text>
                    {sortField === "late_pct" ? (
                      sortOrder === "asc" ? (
                        <ArrowUp size={12} color="#c084fc" />
                      ) : (
                        <ArrowDown size={12} color="#c084fc" />
                      )
                    ) : (
                      <ArrowUpDown size={11} color="#64748b" />
                    )}
                  </Pressable>

                  {/* OT Hours */}
                  <Pressable
                    onPress={() => handleSort("total_ot_hours")}
                    className="w-32 flex-row items-center justify-end gap-1 px-2 shrink-0"
                  >
                    <Text className="text-[11px] font-extrabold uppercase text-slate-300">OT Hours</Text>
                    {sortField === "total_ot_hours" ? (
                      sortOrder === "asc" ? (
                        <ArrowUp size={12} color="#c084fc" />
                      ) : (
                        <ArrowDown size={12} color="#c084fc" />
                      )
                    ) : (
                      <ArrowUpDown size={11} color="#64748b" />
                    )}
                  </Pressable>

                  <Text className="text-[11px] font-extrabold uppercase text-slate-400 w-32 text-center shrink-0">Action</Text>
                </View>

                {/* Table Rows */}
                {paginatedDepts.map((d, index) => {
                  const globalIdx = (currentPage - 1) * pageSize + index + 1;
                  const lateRatio = d.late_pct || 0;
                  const lateBadgeClass =
                    lateRatio > 35
                      ? "bg-rose-500/20 border-rose-500/50 text-rose-300 font-extrabold"
                      : lateRatio > 20
                      ? "bg-amber-500/20 border-amber-500/50 text-amber-300 font-extrabold"
                      : "bg-emerald-500/20 border-emerald-500/50 text-emerald-300 font-extrabold";

                  return (
                    <Pressable
                      key={`dept-row-${d.id}-${index}`}
                      onPress={() =>
                        router.push({
                          pathname: "/modules/attendance/department/[deptId]",
                          params: { deptId: String(d.id) },
                        })
                      }
                      className={`flex-row items-center p-3 border-b border-dark-border/60 transition-colors w-full ${
                        index % 2 === 0 ? "bg-dark-card/30" : "bg-dark-bg/20"
                      } hover:bg-purple-950/40`}
                    >
                      {/* Index */}
                      <Text className="text-xs font-mono text-slate-400 w-10 text-center font-bold shrink-0">
                        {globalIdx}
                      </Text>

                      {/* Name & Code Badge - Expands smoothly */}
                      <View className="flex-1 min-w-[280px] flex-row items-center gap-2 pr-3">
                        <View className="w-5 h-5 rounded bg-purple-500/20 border border-purple-500/40 items-center justify-center shrink-0">
                          <Building2 size={11} color="#c084fc" />
                        </View>
                        <Text
                          className="text-xs font-bold text-white flex-1 leading-snug"
                          numberOfLines={2}
                        >
                          {d.name}
                        </Text>
                        {d.code && (
                          <View className="px-2 py-0.5 rounded-md bg-purple-950 border border-purple-400 shrink-0">
                            <Text className="text-[10px] font-mono font-black text-purple-300 tracking-wide">
                              {d.code}
                            </Text>
                          </View>
                        )}
                      </View>

                      {/* Headcount */}
                      <View className="w-28 items-end px-2 shrink-0">
                        <View className="px-2 py-0.5 rounded bg-sky-500/20 border border-sky-500/40">
                          <Text className="text-xs font-mono font-extrabold text-sky-300">
                            {d.headcount}
                          </Text>
                        </View>
                      </View>

                      {/* Total Records */}
                      <Text className="text-xs font-mono text-slate-200 w-36 text-right px-2 font-bold shrink-0">
                        {d.total_attendance_records.toLocaleString()}
                      </Text>

                      {/* Late % */}
                      <View className="w-28 items-end px-2 shrink-0">
                        <View className={`px-2 py-0.5 rounded border ${lateBadgeClass}`}>
                          <Text className="text-xs font-mono">{lateRatio}%</Text>
                        </View>
                      </View>

                      {/* OT Hours */}
                      <Text className="text-xs font-mono text-amber-300 w-32 text-right px-2 font-bold shrink-0">
                        {d.total_ot_hours.toLocaleString()} hrs
                      </Text>

                      {/* Action Button */}
                      <View className="w-32 items-center justify-center shrink-0">
                        <View className="px-3 py-1 rounded-lg bg-purple-600 border border-purple-400 flex-row items-center gap-1 active:bg-purple-700 shadow-xs">
                          <ExternalLink size={10} color="#ffffff" />
                          <Text className="text-[10px] font-extrabold text-white">Open Page</Text>
                        </View>
                      </View>
                    </Pressable>
                  );
                })}

                {/* Table Footer Summary Row */}
                <View className="flex-row bg-dark-bg border-t-2 border-dark-border p-3 items-center w-full">
                  <Text className="text-xs font-bold text-slate-500 w-10 text-center shrink-0">—</Text>
                  <Text className="text-xs font-extrabold text-white flex-1 min-w-[280px] pr-3">
                    Total ({processedDepts.length} Departments)
                  </Text>
                  <Text className="text-xs font-mono font-extrabold text-sky-300 w-28 text-right px-2 shrink-0">
                    {processedDepts.reduce((sum, d) => sum + (d.headcount || 0), 0).toLocaleString()}
                  </Text>
                  <Text className="text-xs font-mono font-extrabold text-slate-100 w-36 text-right px-2 shrink-0">
                    {processedDepts.reduce((sum, d) => sum + (d.total_attendance_records || 0), 0).toLocaleString()}
                  </Text>
                  <Text className="text-xs font-mono font-extrabold text-amber-300 w-28 text-right px-2 shrink-0">
                    {avgLatePct}%
                  </Text>
                  <Text className="text-xs font-mono font-extrabold text-amber-300 w-32 text-right px-2 shrink-0">
                    {Math.round(processedDepts.reduce((sum, d) => sum + (d.total_ot_hours || 0), 0)).toLocaleString()} hrs
                  </Text>
                  <View className="w-32 shrink-0" />
                </View>
              </View>
            </ScrollView>
          </View>
        )}

        {/* ── Pagination Footer ── */}
        {pageSize > 0 && totalPages > 1 && (
          <View className="flex-col sm:flex-row items-center justify-between gap-2 pt-2 border-t border-dark-border">
            <Text className="text-xs text-slate-400 font-mono">
              Showing {(currentPage - 1) * pageSize + 1} to{" "}
              {Math.min(currentPage * pageSize, processedDepts.length)} of{" "}
              {processedDepts.length} departments
            </Text>

            <View className="flex-row items-center gap-1">
              <Pressable
                disabled={currentPage === 1}
                onPress={() => setCurrentPage((p) => Math.max(1, p - 1))}
                className={`p-1.5 rounded-lg border flex-row items-center gap-1 ${
                  currentPage === 1
                    ? "bg-dark-bg border-dark-border opacity-50"
                    : "bg-dark-card border-dark-border active:bg-slate-800"
                }`}
              >
                <ChevronLeft size={14} color="#94a3b8" />
                <Text className="text-xs font-bold text-slate-300">Prev</Text>
              </Pressable>

              <View className="px-3 py-1 bg-dark-bg border border-dark-border rounded-lg">
                <Text className="text-xs font-mono font-bold text-purple-300">
                  {currentPage} / {totalPages}
                </Text>
              </View>

              <Pressable
                disabled={currentPage === totalPages}
                onPress={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                className={`p-1.5 rounded-lg border flex-row items-center gap-1 ${
                  currentPage === totalPages
                    ? "bg-dark-bg border-dark-border opacity-50"
                    : "bg-dark-card border-dark-border active:bg-slate-800"
                }`}
              >
                <Text className="text-xs font-bold text-slate-300">Next</Text>
                <ChevronRight size={14} color="#94a3b8" />
              </Pressable>
            </View>
          </View>
        )}
      </View>
    </View>
  );
}
