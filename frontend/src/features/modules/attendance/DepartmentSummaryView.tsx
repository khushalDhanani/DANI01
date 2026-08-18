import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import { ArrowLeft, Building2 } from "lucide-react-native";
import { AttendanceDepartmentTab } from "./AttendanceDepartmentTab";

export function DepartmentSummaryView() {
  const router = useRouter();

  return (
    <View className="p-3.5 gap-4">
      {/* ── Breadcrumb & Header ── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-3 bg-dark-card border border-dark-border p-4 rounded-xl">
        <View className="flex-1 gap-1">
          <View className="flex-row items-center gap-2">
            <Pressable
              onPress={() => router.push("/modules/attendance")}
              className="flex-row items-center gap-1 bg-dark-bg border border-dark-border px-2 py-0.5 rounded"
            >
              <ArrowLeft size={12} color="#94a3b8" />
              <Text className="text-[10px] font-bold text-slate-300">Back to Attendance</Text>
            </Pressable>
            <View className="bg-purple-950/80 border border-purple-800/60 px-2 py-0.5 rounded">
              <Text className="text-[10px] font-mono font-bold text-purple-400">
                EMPLOYEE ANALYTICS
              </Text>
            </View>
          </View>
          <Text className="text-xl font-black text-white mt-1">
            Department Master Summary
          </Text>
          <Text className="text-xs text-slate-400">
            Comprehensive department-wise breakdown of active headcount (1,316 active staff, 42.6% of master roster), biometric attendance volume, late arrival ratios %, and approved overtime hours across active employees.
          </Text>
        </View>

        <View className="flex-row items-center gap-2">
          <View className="bg-purple-900/30 border border-purple-800/50 px-3 py-2 rounded-xl flex-row items-center gap-2">
            <Building2 size={18} color="#c084fc" />
            <View>
              <Text className="text-[10px] font-bold text-purple-400 uppercase">Analysis Scope</Text>
              <Text className="text-xs font-bold text-white font-mono">Active Employees</Text>
            </View>
          </View>
        </View>
      </View>

      {/* ── Main Department Master Summary Component ── */}
      <AttendanceDepartmentTab />
    </View>
  );
}
