import "../global.css";
import React from "react";
import { StatusBar } from "react-native";
import { Stack } from "expo-router";
import { QueryProvider } from "@/providers/query-provider";
import { THEME_COLORS } from "@/constants/theme";

/**
 * Root Layout
 *
 * Responsibilities (infrastructure only):
 *  - NativeWind global CSS initialization
 *  - TanStack Query provider
 *  - StatusBar configuration
 *  - Expo Router Stack navigation context
 *
 * No feature logic, no business data fetching, no UI components.
 * Each screen manages its own safe area insets.
 */
export default function RootLayout() {
  return (
    <QueryProvider>
      <StatusBar barStyle="light-content" backgroundColor={THEME_COLORS.bg} />
      <Stack screenOptions={{ headerShown: false }} />
    </QueryProvider>
  );
}
