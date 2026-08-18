import React, { useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, Text, TextInput, View } from "react-native";
import { useRouter } from "expo-router";
import {
  Banknote,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Download,
  ExternalLink,
  Search,
} from "lucide-react-native";
import { downloadPayrollDirectoryExport } from "@/api/payroll.api";
import { THEME_COLORS } from "@/constants/theme";
import { usePayrollDirectory } from "@/hooks/usePayroll";

const STATUS_FILTERS = [
  { id: "", label: "All Records" },
  { id: "ACTIVE", label: "Active Employees" },
  { id: "CORRUPTED", label: "Math Discrepancies" },
  { id: "NEGATIVE", label: "Negative Figures" },
];

interface PayrollRegisterTabProps {
  compId?: number;
}

export function PayrollRegisterTab({ compId }: PayrollRegisterTabProps = {}) {
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const pageSize = 20;

  const { data: dirData, isLoading } = usePayrollDirectory(
    statusFilter,
    searchTerm,
    pageSize,
    page * pageSize,
    undefined,
    compId,
  );

  const handleExport = async () => {
    try {
      setIsExporting(true);
      await downloadPayrollDirectoryExport(statusFilter, searchTerm);
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const totalPages = dirData ? Math.ceil(dirData.total / pageSize) : 0;

  return (
    <View className="flex-1 space-y-3">
      {/* Compact Search & Export Toolbar */}
      <View className="flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <View className="flex-1 flex-row items-center bg-dark-card border border-dark-border px-3 py-1.5 rounded-lg">
          <Search size={14} color="#94a3b8" />
          <TextInput
            className="flex-1 ml-2 text-[11px] text-white outline-none"
            placeholder="Search by Employee Code, Name, or SalMonth..."
            placeholderTextColor="#64748b"
            value={searchTerm}
            onChangeText={(txt: string) => {
              setSearchTerm(txt);
              setPage(0);
            }}
          />
        </View>

        {/* Compact Export Button */}
        <Pressable
          className="flex-row items-center justify-center gap-1.5 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 px-3 py-1.5 rounded-lg self-start md:self-auto"
          onPress={handleExport}
          disabled={isExporting}
        >
          {isExporting ? (
            <ActivityIndicator size="small" color="#c084fc" />
          ) : (
            <Download size={13} color="#c084fc" />
          )}
          <Text className="text-[11px] font-bold text-purple-300">
            {isExporting ? "Exporting..." : "Export Register CSV"}
          </Text>
        </Pressable>
      </View>

      {/* Filter Tabs */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} className="w-full">
        <View className="flex-row gap-1.5">
          {STATUS_FILTERS.map((f) => {
            const isSelected = statusFilter === f.id;
            return (
              <Pressable
                key={f.id}
                onPress={() => {
                  setStatusFilter(f.id);
                  setPage(0);
                }}
                className={`px-3 py-1 rounded-md border text-[11px] font-semibold ${
                  isSelected
                    ? "bg-purple-600/30 border-purple-500 text-purple-300 font-bold"
                    : "bg-dark-card border-dark-border text-slate-400 hover:border-slate-700"
                }`}
              >
                <Text
                  className={`text-[11px] font-semibold ${
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

      {/* ── Compact Table Container ── */}
      <View className="bg-dark-card border border-dark-border rounded-lg overflow-hidden shadow-sm w-full">
        {isLoading ? (
          <View className="py-12 items-center justify-center">
            <ActivityIndicator size="small" color="#a855f7" />
            <Text className="text-[11px] text-slate-400 mt-2">Loading salary records...</Text>
          </View>
        ) : !dirData || dirData.items.length === 0 ? (
          <View className="py-12 items-center justify-center">
            <Banknote size={28} color={THEME_COLORS.textMuted} />
            <Text className="text-xs font-semibold text-slate-400 mt-2">
              No salary records found.
            </Text>
            <Text className="text-[10px] text-slate-500 mt-0.5">Try adjusting your filters or search.</Text>
          </View>
        ) : (
          <View className="w-full divide-y divide-dark-border">
            {/* Header */}
            <View className="flex-row items-center px-3 py-2 bg-slate-900/60 border-b border-dark-border">
              <Text className="w-16 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Sal ID
              </Text>
              <Text className="flex-1 min-w-[160px] text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Employee Identity
              </Text>
              <Text className="w-24 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Sal Month
              </Text>
              <Text className="w-24 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Paid Days
              </Text>
              <Text className="w-32 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
                Total Earned
              </Text>
              <Text className="w-32 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
                Total Deduction
              </Text>
              <Text className="w-32 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
                Net Pay Output
              </Text>
            </View>

            {/* Rows */}
            {dirData.items.map((row) => (
              <View
                key={row.earned_sal_id}
                className="flex-row items-center px-3 py-2 hover:bg-dark-bg/40 transition-colors"
              >
                {/* Sal ID */}
                <Text className="w-16 text-[11px] font-mono text-slate-400">#{row.earned_sal_id}</Text>

                {/* Employee Identity */}
                <Pressable
                  onPress={() =>
                    router.push({
                      pathname: "/modules/attendance/employee/[empId]",
                      params: { empId: String(row.emp_id) },
                    })
                  }
                  className="flex-1 min-w-[160px] pr-2 flex-row items-center gap-1 group"
                >
                  <View className="flex-1">
                    <Text
                      className="text-[11px] font-bold text-white group-hover:text-purple-400 underline transition-colors"
                      numberOfLines={1}
                    >
                      {row.emp_name}
                    </Text>
                    <Text className="text-[9px] text-slate-500 font-mono">
                      Code: {row.emp_code || "N/A"}
                    </Text>
                  </View>
                  <ExternalLink size={11} color="#c084fc" />
                </Pressable>

                {/* Sal Month */}
                <View className="w-24 pr-2">
                  <View className="flex-row items-center gap-1">
                    <Calendar size={11} color="#94a3b8" />
                    <Text className="text-[11px] font-mono font-semibold text-purple-300">
                      {row.sal_month}
                    </Text>
                  </View>
                </View>

                {/* Paid Days */}
                <View className="w-24 pr-2">
                  <Text className="text-[11px] font-mono text-slate-300">{row.paid_days} Days</Text>
                </View>

                {/* Total Earned */}
                <View className="w-32 pr-2">
                  <Text className="text-[11px] font-mono text-emerald-400 font-semibold text-right">
                    ₹{row.total_earned.toLocaleString()}
                  </Text>
                </View>

                {/* Total Deduction */}
                <View className="w-32 pr-2">
                  <Text className="text-[11px] font-mono text-rose-400 font-semibold text-right">
                    ₹{row.total_deduction.toLocaleString()}
                  </Text>
                </View>

                {/* Net Pay */}
                <View className="w-32">
                  <Text className="text-[11px] font-mono text-white font-bold text-right">
                    ₹{row.net_pay.toLocaleString()}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Compact Pagination Footer */}
        {dirData && totalPages > 1 && (
          <View className="flex-row items-center justify-between px-3 py-2 bg-dark-bg/60 border-t border-dark-border">
            <Text className="text-[11px] text-slate-400">
              Showing <Text className="font-bold text-slate-200">{page * pageSize + 1}</Text> to{" "}
              <Text className="font-bold text-slate-200">
                {Math.min((page + 1) * pageSize, dirData.total)}
              </Text>{" "}
              of <Text className="font-bold text-slate-200">{dirData.total}</Text> records
            </Text>

            <View className="flex-row items-center gap-1.5">
              <Pressable
                className={`p-1 rounded-md border ${
                  page === 0
                    ? "border-dark-border bg-dark-card/50 opacity-40"
                    : "border-dark-border bg-dark-card hover:bg-slate-800"
                }`}
                disabled={page === 0}
                onPress={() => setPage((p) => Math.max(0, p - 1))}
              >
                <ChevronLeft size={14} color="#94a3b8" />
              </Pressable>

              <Text className="text-[11px] text-slate-300 font-mono">
                {page + 1} / {totalPages}
              </Text>

              <Pressable
                className={`p-1 rounded-md border ${
                  page >= totalPages - 1
                    ? "border-dark-border bg-dark-card/50 opacity-40"
                    : "border-dark-border bg-dark-card hover:bg-slate-800"
                }`}
                disabled={page >= totalPages - 1}
                onPress={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              >
                <ChevronRight size={14} color="#94a3b8" />
              </Pressable>
            </View>
          </View>
        )}
      </View>
    </View>
  );
}
