import React from "react";
import { ActivityIndicator, ScrollView, Text, View } from "react-native";
import { AlertTriangle, Banknote, Calendar, Coins, TrendingUp, UserCheck } from "lucide-react-native";
import { usePayrollOverview } from "@/hooks/usePayroll";

interface PayrollOverviewTabProps {
  compId?: number;
}

export function PayrollOverviewTab({ compId }: PayrollOverviewTabProps = {}) {
  const { data: overview, isLoading } = usePayrollOverview(compId);

  if (isLoading) {
    return (
      <View className="py-12 items-center justify-center">
        <ActivityIndicator size="small" color="#a855f7" />
        <Text className="text-[11px] text-slate-400 mt-2 font-medium">
          Analyzing payroll registers and salary calculations...
        </Text>
      </View>
    );
  }

  if (!overview) {
    return (
      <View className="py-12 items-center justify-center">
        <AlertTriangle size={28} color="#ef4444" />
        <Text className="text-xs font-semibold text-slate-300 mt-2">
          Failed to load payroll overview data.
        </Text>
      </View>
    );
  }

  return (
    <ScrollView className="flex-1 space-y-3" showsVerticalScrollIndicator={false}>
      {/* ── Compact Summary Cards Grid ── */}
      <View className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Total Payroll Header Records */}
        <View className="bg-dark-card border border-dark-border p-3 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Salary Records
            </Text>
            <View className="p-1.5 rounded-lg bg-purple-950/80 border border-purple-800/60">
              <Banknote size={14} color="#c084fc" />
            </View>
          </View>
          <Text className="text-xl font-black text-white font-mono">
            {overview.total_payroll_records.toLocaleString()}
          </Text>
          <Text className="text-[10px] text-purple-300 mt-0.5 font-mono">
            Disbursements
          </Text>
        </View>

        {/* Employees with Payroll */}
        <View className="bg-dark-card border border-dark-border p-3 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Employees Paid
            </Text>
            <View className="p-1.5 rounded-lg bg-emerald-950/80 border border-emerald-800/60">
              <UserCheck size={14} color="#34d399" />
            </View>
          </View>
          <Text className="text-xl font-black text-emerald-400 font-mono">
            {overview.total_employees_with_payroll.toLocaleString()}
          </Text>
          <Text className="text-[10px] text-emerald-400/80 mt-0.5 font-mono">
            With salary history
          </Text>
        </View>

        {/* Latest Payroll Period */}
        <View className="bg-dark-card border border-dark-border p-3 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Latest Period
            </Text>
            <View className="p-1.5 rounded-lg bg-sky-950/80 border border-sky-800/60">
              <Calendar size={14} color="#38bdf8" />
            </View>
          </View>
          <Text className="text-xl font-black text-sky-400 font-mono">
            {overview.latest_payroll_month}
          </Text>
          <Text className="text-[10px] text-sky-400/80 mt-0.5 font-mono">
            {overview.latest_month_record_count} active slips
          </Text>
        </View>

        {/* Lifetime Disbursed Net Pay */}
        <View className="bg-dark-card border border-dark-border p-3 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Disbursed Net Pay
            </Text>
            <View className="p-1.5 rounded-lg bg-amber-950/80 border border-amber-800/60">
              <Coins size={14} color="#fbbf24" />
            </View>
          </View>
          <Text className="text-lg font-black text-amber-400 font-mono">
            ₹{overview.lifetime_total_net_pay.toLocaleString()}
          </Text>
          <Text className="text-[10px] text-amber-400/80 mt-0.5 font-mono">
            Net Salary Output
          </Text>
        </View>
      </View>

      {/* ── Compact Monthly Salary Trends Table ── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3 mt-2">
        <View className="flex-row items-center justify-between mb-2.5">
          <View className="flex-row items-center gap-1.5">
            <TrendingUp size={15} color="#c084fc" />
            <Text className="text-xs font-bold text-white">Monthly Payroll Registers</Text>
          </View>
          <Text className="text-[10px] font-mono text-slate-400">Last 12 Periods</Text>
        </View>

        <View className="w-full divide-y divide-dark-border border border-dark-border rounded-lg overflow-hidden">
          {/* Header */}
          <View className="flex-row items-center px-3 py-2 bg-slate-900/60">
            <Text className="w-28 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Sal Month
            </Text>
            <Text className="w-28 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Paid Staff
            </Text>
            <Text className="flex-1 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
              Total Earned
            </Text>
            <Text className="flex-1 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
              Total Deduction
            </Text>
            <Text className="flex-1 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
              Net Pay Output
            </Text>
          </View>

          {/* Rows */}
          {overview.monthly_trends.map((m) => (
            <View
              key={m.sal_month}
              className="flex-row items-center px-3 py-2 hover:bg-dark-bg/40 transition-colors"
            >
              <View className="w-28 flex-row items-center gap-1">
                <Calendar size={11} color="#c084fc" />
                <Text className="text-[11px] font-mono font-bold text-purple-300">{m.sal_month}</Text>
              </View>

              <Text className="w-28 text-[11px] font-mono text-slate-300">
                {m.record_count.toLocaleString()} emps
              </Text>

              <Text className="flex-1 text-[11px] font-mono text-emerald-400 text-right font-semibold">
                ₹{m.total_earned.toLocaleString()}
              </Text>

              <Text className="flex-1 text-[11px] font-mono text-rose-400 text-right font-semibold">
                ₹{m.total_deduction.toLocaleString()}
              </Text>

              <Text className="flex-1 text-[11px] font-mono text-white text-right font-bold">
                ₹{m.total_net_pay.toLocaleString()}
              </Text>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
}
