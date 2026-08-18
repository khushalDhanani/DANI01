import React from "react";
import { Activity, RefreshCw } from "lucide-react-native";
import { Pressable, Text, View } from "react-native";
import { Redirect, useLocalSearchParams } from "expo-router";
import { PageContainer } from "@/components/layout/PageContainer";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ModuleHeader } from "@/features/modules/components/ModuleHeader";
import { ModuleTablesList } from "@/features/modules/components/ModuleTablesList";
import {
  useModuleDefinition,
  useModuleValidation,
} from "@/hooks/useModules";
import { THEME_COLORS } from "@/constants/theme";

export default function GenericModuleScreen() {
  const { moduleCode } = useLocalSearchParams<{ moduleCode: string }>();
  const normalizedCode = (moduleCode || "").toUpperCase();

  // Generic Module Queries (always called unconditionally)
  const {
    data: moduleDef,
    isLoading: isLoadingDef,
    isError: isErrorDef,
    error: errorDef,
    refetch: refetchDef,
  } = useModuleDefinition(normalizedCode);

  const {
    data: validation,
    isLoading: isLoadingVal,
  } = useModuleValidation(normalizedCode);

  // Redirect PERSON to the dedicated Daylite page
  if (normalizedCode === "PERSON") {
    return <Redirect href="/daylite" />;
  }

  // Redirect EMPLOYEE to the dedicated employee module page
  if (normalizedCode === "EMPLOYEE") {
    return <Redirect href="/modules/employee" />;
  }

  // Redirect ORGANIZATION to the dedicated organization module page
  if (normalizedCode === "ORGANIZATION") {
    return <Redirect href="/modules/organization" />;
  }

  // Redirect CONTACT to the dedicated contact module page
  if (normalizedCode === "CONTACT") {
    return <Redirect href="/modules/contact" />;
  }

  // Redirect SECURITY to the dedicated security module page
  if (normalizedCode === "SECURITY") {
    return <Redirect href="/modules/security" />;
  }

  // Redirect ATTENDANCE to the dedicated attendance module page
  if (normalizedCode === "ATTENDANCE") {
    return <Redirect href="/modules/attendance" />;
  }

  // Redirect PAYROLL to the dedicated payroll module page
  if (normalizedCode === "PAYROLL") {
    return <Redirect href="/modules/payroll" />;
  }

  // Redirect CROSS_DOMAIN_DQ to the dedicated cross-domain data quality page
  if (normalizedCode === "CROSS_DOMAIN_DQ" || normalizedCode === "CROSS_DOMAIN") {
    return <Redirect href="/modules/cross_domain_dq" />;
  }

  // Redirect PROCEDURE_LOGIC to the dedicated procedure logic analyzer page
  if (normalizedCode === "PROCEDURE_LOGIC" || normalizedCode === "PROCEDURE") {
    return <Redirect href="/modules/procedure_logic" />;
  }




  if (isErrorDef) {
    return (
      <PageContainer>
        <ErrorState
          message={errorDef?.message || "Failed to load module definition."}
          onRetry={() => refetchDef()}
          title={`Failed to load module "${normalizedCode}"`}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* ── Top Header ────────────────────────────────────────── */}
      <ModuleHeader
        module={moduleDef}
        validation={validation}
        isLoading={isLoadingDef || isLoadingVal}
      />

      {/* ── Generic Module Content ────────────────────────────── */}
      {isLoadingDef ? (
        <View className="gap-4">
          <LoadingSkeleton height={120} borderRadius={12} />
          <LoadingSkeleton height={200} borderRadius={12} />
        </View>
      ) : (
        <View className="gap-4">
          {/* Action Bar */}
          <View className="flex-row items-center gap-2">
            <Pressable
              onPress={() => refetchDef()}
              className="flex-row items-center gap-2 bg-dark-bg border border-dark-border px-3 py-2 rounded-lg hover:border-slate-500"
            >
              <RefreshCw size={14} color={THEME_COLORS.textMuted} />
              <Text className="text-sm font-medium text-slate-300">Refresh Meta</Text>
            </Pressable>
          </View>

          {/* Table List & Schema Alignment */}
          {moduleDef && (
            <ModuleTablesList module={moduleDef} validation={validation} />
          )}

          <View className="bg-dark-card border border-dark-border rounded-xl p-4 items-center text-center">
            <View className="w-12 h-12 rounded-full bg-slate-800 items-center justify-center mb-3">
              <Activity size={22} color={THEME_COLORS.textMuted} />
            </View>
            <Text className="text-base font-bold text-white mb-1">
              Domain Metrics Not Yet Configured
            </Text>
            <Text className="text-xs text-slate-400 max-w-md text-center leading-relaxed">
              Domain aggregate metrics for module &quot;{normalizedCode}&quot; will be implemented in a dedicated milestone.
            </Text>
          </View>
        </View>
      )}
    </PageContainer>
  );
}
