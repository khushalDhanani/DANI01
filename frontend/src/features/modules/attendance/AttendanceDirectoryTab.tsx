import React, { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import { useRouter } from "expo-router";
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Download,
  ExternalLink,
  Search,
  User,
} from "lucide-react-native";
import { downloadAttendanceDirectoryExport } from "@/api/attendance.api";
import { THEME_COLORS } from "@/constants/theme";
import { useAttendanceDirectory } from "@/hooks/useAttendance";
import { formatDate } from "@/utils/formatters";

const STATUS_FILTERS = [
  { id: "", label: "All Logs" },
  { id: "PRESENT", label: "Present" },
  { id: "ABSENT", label: "Absent" },
  { id: "LATE", label: "Late Coming" },
  { id: "EARLY", label: "Early Exit" },
  { id: "OT", label: "Overtime" },
  { id: "LEAVE", label: "On Leave" },
  { id: "WO", label: "Weekly Off" },
];


interface AttendanceDirectoryTabProps {
  deptId?: number;
  compId?: number;
  empId?: number;
}

export function AttendanceDirectoryTab({ deptId, compId, empId }: AttendanceDirectoryTabProps = {}) {
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<string>("");

  const [searchTerm, setSearchTerm] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const pageSize = 20;

  const { data: dirData, isLoading, isFetching } = useAttendanceDirectory(
    statusFilter || undefined,
    searchTerm.trim() || undefined,
    pageSize,
    page * pageSize,
    deptId,
    compId,
    empId
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
      await downloadAttendanceDirectoryExport(
        statusFilter || undefined,
        searchTerm.trim() || undefined
      );
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const totalPages = dirData ? Math.ceil(dirData.total / pageSize) : 0;

  return (
    <View className="gap-2.5 w-full">
      {/* Search & Export Toolbar */}
      <View className="flex-col md:flex-row items-stretch md:items-center justify-between gap-2.5 w-full">
        {/* Search Bar */}
        <View className="flex-1 flex-row items-center bg-dark-card border border-dark-border rounded-xl px-3 py-1.5">
          <Search size={16} color={THEME_COLORS.textMuted} />
          <TextInput
            className="flex-1 ml-2 text-sm text-white placeholder:text-slate-500 font-sans outline-none"
            placeholder="Search employee code, name, shift code, status..."
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
            {isExporting ? "Exporting..." : "Export Logs"}
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
                className={`px-3 py-1.5 rounded-lg border text-xs font-semibold ${isSelected
                    ? "bg-purple-600/30 border-purple-500 text-purple-300"
                    : "bg-dark-card border-dark-border text-slate-400 hover:border-slate-700"
                  }`}
              >
                <Text
                  className={`text-xs font-semibold ${isSelected ? "text-purple-300 font-bold" : "text-slate-400"
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
            <Text className="text-xs text-slate-400 mt-2">Loading attendance logs...</Text>
          </View>
        ) : !dirData || dirData.items.length === 0 ? (
          <View className="py-8 items-center justify-center">
            <User size={32} color={THEME_COLORS.textMuted} />
            <Text className="text-sm font-semibold text-slate-400 mt-2">No attendance logs found.</Text>
            <Text className="text-xs text-slate-500 mt-1">Try adjusting your filters or search keyword.</Text>
          </View>
        ) : (
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={true}
            className="w-full"
            contentContainerStyle={{ minWidth: "100%", flexGrow: 1 }}
          >
            <View className="min-w-[1050px] w-full divide-y divide-dark-border">
              {/* Header */}
              <View className="flex-row items-center px-3 py-2 bg-slate-900/80 border-b border-dark-border">
                <Text className="w-16 text-[10px] font-bold uppercase tracking-wider text-slate-400">ID</Text>
                <Text className="flex-1 min-w-[200px] pr-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">Employee Identity</Text>
                <Text className="w-32 pr-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Att Date</Text>
                <Text className="w-44 pr-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Status</Text>
                <Text className="w-40 pr-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Actual Punch</Text>
                <Text className="w-24 pr-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">Shift</Text>
                <Text className="w-32 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">Grace & OT Mins</Text>
              </View>

              {/* Rows */}
              {dirData.items.map((row) => {
                const isPresent = row.status_label === "Present";
                return (
                  <View
                    key={row.att_id}
                    className="flex-row items-center px-3 py-2 hover:bg-dark-bg/40 transition-colors"
                  >
                    {/* ID */}
                    <Text className="w-16 text-xs font-mono text-slate-400">#{row.att_id}</Text>

                    {/* Employee Identity */}
                    <Pressable
                      onPress={() =>
                        router.push({
                          pathname: "/modules/attendance/employee/[empId]",
                          params: { empId: String(row.emp_id) },
                        })
                      }
                      className="flex-1 min-w-[200px] pr-3 flex-row items-center gap-1.5 group"
                    >
                      <View className="flex-1">
                        <Text className="text-xs font-bold text-white group-hover:text-purple-400 underline transition-colors" numberOfLines={1}>
                          {row.emp_name} - {row.emp_code || "N/A"}
                        </Text>
                      </View>
                      <ExternalLink size={12} color="#c084fc" />
                    </Pressable>


                    {/* Att Date */}
                    <View className="w-32 pr-2">
                      <View className="flex-row items-center gap-1">
                        <Calendar size={12} color="#94a3b8" />
                        <Text className="text-xs font-mono text-slate-300">{formatDate(row.att_date)}</Text>
                      </View>
                    </View>

                    {/* Status Badge */}
                    <View className="w-44 pr-2 flex-row items-center">
                      {(() => {
                        const lbl = row.status_label || "";
                        const isPres = lbl === "Present";
                        const isWarning = lbl.includes("Late") || lbl.includes("Early");
                        const isDanger = lbl.includes("Absent");
                        const badgeBg = isPres
                          ? "bg-emerald-950/90 border-emerald-700/60"
                          : isWarning
                            ? "bg-amber-950/90 border-amber-700/60"
                            : isDanger
                              ? "bg-rose-950/90 border-rose-700/60"
                              : "bg-purple-950/90 border-purple-700/60";
                        const dotBg = isPres
                          ? "bg-emerald-400"
                          : isWarning
                            ? "bg-amber-400"
                            : isDanger
                              ? "bg-rose-400"
                              : "bg-purple-400";
                        const textFg = isPres
                          ? "text-emerald-300"
                          : isWarning
                            ? "text-amber-300"
                            : isDanger
                              ? "text-rose-300"
                              : "text-purple-300";

                        return (
                          <View className={`px-2.5 py-1 rounded-full border flex-row items-center gap-1.5 shrink-0 ${badgeBg}`}>
                            <View className={`w-1.5 h-1.5 rounded-full ${dotBg}`} />
                            <Text className={`text-[10px] font-bold ${textFg}`} numberOfLines={1}>
                              {row.status_label}
                            </Text>
                          </View>
                        );
                      })()}
                    </View>


                    {/* Actual Punch */}
                    <View className="w-40 pr-2">
                      {row.in_time && row.out_time ? (
                        <Text className="text-xs font-mono text-slate-300 font-medium">
                          {row.in_time.substring(0, 5)} – {row.out_time.substring(0, 5)}
                        </Text>
                      ) : row.in_time && !row.out_time ? (
                        <View className="flex-row items-center gap-1">
                          <Text className="text-xs font-mono text-slate-300">
                            {row.in_time.substring(0, 5)} –
                          </Text>
                          <View className="px-1.5 py-0.2 rounded bg-amber-950 border border-amber-800/80">
                            <Text className="text-[9px] font-mono font-bold text-amber-400">
                              Missing Out
                            </Text>
                          </View>
                        </View>
                      ) : !row.in_time && row.out_time ? (
                        <View className="flex-row items-center gap-1">
                          <View className="px-1.5 py-0.2 rounded bg-amber-950 border border-amber-800/80">
                            <Text className="text-[9px] font-mono font-bold text-amber-400">
                              Missing In
                            </Text>
                          </View>
                          <Text className="text-xs font-mono text-slate-300">
                            – {row.out_time.substring(0, 5)}
                          </Text>
                        </View>
                      ) : isPresent ? (
                        <View className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                          <Text className="text-[10px] font-mono text-slate-400">
                            No Biometric Log
                          </Text>
                        </View>
                      ) : (
                        <Text className="text-xs font-mono text-slate-500">--:-- – --:--</Text>
                      )}
                    </View>


                    {/* Shift Code */}
                    <View className="w-24 pr-2">
                      <Text className="text-xs font-mono text-purple-300 font-semibold">
                        {row.shift_code || "DEFAULT"}
                      </Text>
                    </View>

                    {/* Grace & OT */}
                    <View className="w-32 items-end flex-col gap-0.5">
                      {row.ot_mins > 0 && (
                        <Text className="text-[10px] font-mono font-bold text-amber-400">
                          + {row.ot_mins}m OT
                        </Text>
                      )}
                      {row.late_mins > 0 && (
                        <Text className="text-[10px] font-mono text-rose-400">
                          {row.late_mins}m Late
                        </Text>
                      )}
                      {row.early_mins > 0 && (
                        <Text className="text-[10px] font-mono text-amber-400">
                          {row.early_mins}m Early
                        </Text>
                      )}
                      {row.ot_mins === 0 && row.late_mins === 0 && row.early_mins === 0 && (
                        <Text className="text-[10px] font-mono text-slate-500">Standard</Text>
                      )}
                    </View>
                  </View>
                );
              })}
            </View>
          </ScrollView>
        )}

        {/* Pagination Controls */}
        {dirData && dirData.total > 0 && (
          <View className="flex-row items-center justify-between px-4 py-3 bg-dark-bg/60 border-t border-dark-border w-full">
            <Text className="text-xs text-slate-400 font-medium">
              Showing {page * pageSize + 1}–
              {Math.min((page + 1) * pageSize, dirData.total)} of{" "}
              {dirData.total.toLocaleString()} logs
              {isFetching && " (Updating...)"}
            </Text>

            <View className="flex-row items-center gap-2">
              <Pressable
                className={`p-1.5 rounded-lg border border-dark-border ${page === 0 ? "opacity-30" : "bg-dark-card hover:border-slate-600"
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
                className={`p-1.5 rounded-lg border border-dark-border ${page + 1 >= totalPages ? "opacity-30" : "bg-dark-card hover:border-slate-600"
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
