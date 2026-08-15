import React from "react";
import { Activity } from "lucide-react-native";
import { Text, View } from "react-native";
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
        <View className="gap-6">
          {/* Table List & Schema Alignment */}
          {moduleDef && (
            <ModuleTablesList module={moduleDef} validation={validation} />
          )}

          <View className="bg-dark-card border border-dark-border rounded-xl p-8 items-center text-center">
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
