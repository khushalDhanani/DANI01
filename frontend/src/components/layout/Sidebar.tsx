import React, { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { usePathname, useRouter } from "expo-router";
import type { Href } from "expo-router";
import {
  ChevronDown,
  ChevronRight,
  Database,
  Sparkles,
} from "lucide-react-native";
import {
  DAYLITE_NAV_GROUP,
  PLATFORM_NAV_ITEMS,
} from "@/constants/navigation";
import { useHealth } from "@/hooks/useHealth";
import { LAYOUT } from "@/constants/layout";
import { THEME_COLORS } from "@/constants/theme";

interface SidebarProps {
  /** When true, renders as a mobile drawer panel (adds close button behaviour) */
  isDrawer?: boolean;
  /** Called after any navigation or explicit close action (drawer mode) */
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const router = useRouter();
  const pathname = usePathname();
  const { isSuccess: apiOnline, isLoading: apiChecking } = useHealth();
  const [dayliteExpanded, setDayliteExpanded] = useState(true);

  const isDayliteActive =
    pathname.startsWith("/daylite") || pathname.startsWith("/modules");

  const isItemActive = (href: string): boolean => {
    if (href === "/") return pathname === "/";
    if (href === "/daylite") {
      return (
        pathname === "/daylite" ||
        pathname === "/daylite/" ||
        pathname === "/modules" ||
        pathname.startsWith("/modules/PERSON")
      );
    }
    if (href === "/daylite/person") {
      return (
        pathname === "/daylite/person" ||
        pathname.startsWith("/daylite/person/")
      );
    }
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  const handleNav = (href: string) => {
    router.push(href as Href);
    onClose?.();
  };

  const toggleDaylite = () => {
    setDayliteExpanded((prev) => !prev);
  };

  return (
    <View
      className="h-full bg-dark-card border-r border-dark-border flex-col justify-between"
      style={{
        width: LAYOUT.SIDEBAR_WIDTH,
        minWidth: LAYOUT.SIDEBAR_WIDTH,
        maxWidth: LAYOUT.SIDEBAR_WIDTH,
        flexGrow: 0,
        flexShrink: 0,
      }}
    >
      {/* ── Compact Brand ───────────────────────────────── */}
      <View className="px-3.5 py-3 border-b border-dark-border">
        <View className="flex-row items-center gap-2.5">
          <View className="w-7 h-7 rounded-lg bg-blue-600 items-center justify-center">
            <Database size={15} color={THEME_COLORS.onPrimary} />
          </View>
          <View>
            <Text className="text-xs font-black text-white tracking-tight">
              AIRIS <Text className="text-blue-400">INSIGHTS</Text>
            </Text>
            <Text className="text-[8px] uppercase font-bold text-slate-500 tracking-wider">
              DB Intelligence
            </Text>
          </View>
        </View>
      </View>

      {/* ── Navigation Sections (Scrollable) ─────────────── */}
      <ScrollView
        className="flex-1 px-2 pt-3"
        contentContainerStyle={{ gap: 14, paddingBottom: 16 }}
        showsVerticalScrollIndicator={false}
      >
        {/* ── Section 1: Database Platform ─────────────────── */}
        <View className="gap-0.5">
          <Text className="text-[9px] uppercase font-bold text-slate-500 tracking-widest px-2.5 mb-1">
            Database Platform
          </Text>

          {PLATFORM_NAV_ITEMS.map((item) => {
            const active = isItemActive(item.href);
            const Icon = item.icon;

            return (
              <Pressable
                key={item.href}
                onPress={() => handleNav(item.href)}
                accessibilityRole="button"
                accessibilityLabel={`Navigate to ${item.label}`}
                className={`flex-row items-center justify-between px-2.5 py-2 rounded-lg transition-all ${
                  active
                    ? "bg-blue-600 shadow-sm"
                    : "hover:bg-slate-800/60 active:bg-slate-800"
                }`}
              >
                <View className="flex-row items-center gap-2.5 flex-1">
                  <Icon
                    size={15}
                    color={active ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted}
                  />
                  <Text
                    className={`text-xs font-semibold ${
                      active ? "text-white" : "text-slate-300"
                    }`}
                    numberOfLines={1}
                  >
                    {item.label}
                  </Text>
                </View>
              </Pressable>
            );
          })}
        </View>

        {/* ── Section 2: Day Lite (Main Group & Indented Sub-items) ── */}
        <View className="gap-0.5">
          <Text className="text-[9px] uppercase font-bold text-slate-500 tracking-widest px-2.5 mb-1">
            Data Analytics
          </Text>

          {/* Main Day Lite Group Tab */}
          <Pressable
            onPress={toggleDaylite}
            accessibilityRole="button"
            accessibilityLabel="Toggle Day Lite group"
            className={`flex-row items-center justify-between px-2.5 py-2 rounded-lg transition-all ${
              isDayliteActive && !dayliteExpanded
                ? "bg-blue-600 shadow-sm"
                : "hover:bg-slate-800/60 active:bg-slate-800"
            }`}
          >
            <View className="flex-row items-center gap-2.5 flex-1">
              <Sparkles
                size={15}
                color={
                  isDayliteActive && !dayliteExpanded
                    ? THEME_COLORS.onPrimary
                    : THEME_COLORS.primaryIcon
                }
              />
              <Text
                className={`text-xs font-bold ${
                  isDayliteActive && !dayliteExpanded
                    ? "text-white"
                    : "text-slate-100"
                }`}
              >
                {DAYLITE_NAV_GROUP.label}
              </Text>
            </View>

            {dayliteExpanded ? (
              <ChevronDown size={14} color={THEME_COLORS.textMuted} />
            ) : (
              <ChevronRight size={14} color={THEME_COLORS.textMuted} />
            )}
          </Pressable>

          {/* Indented Sub-items inside Day Lite */}
          {dayliteExpanded && (
            <View className="pl-4 pr-1 mt-0.5 border-l-2 border-slate-800 ml-3.5 gap-0.5">
              {DAYLITE_NAV_GROUP.children.map((subItem) => {
                const active = isItemActive(subItem.href);
                const SubIcon = subItem.icon;

                return (
                  <Pressable
                    key={subItem.href}
                    onPress={() => handleNav(subItem.href)}
                    accessibilityRole="button"
                    accessibilityLabel={`Navigate to ${subItem.label}`}
                    className={`flex-row items-center justify-between px-2.5 py-1.5 rounded-lg transition-all ${
                      active
                        ? "bg-blue-600 shadow-sm"
                        : "hover:bg-slate-800/50 active:bg-slate-800"
                    }`}
                  >
                    <View className="flex-row items-center gap-2 flex-1">
                      <SubIcon
                        size={13}
                        color={active ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted}
                      />
                      <Text
                        className={`text-xs font-medium ${
                          active ? "text-white font-semibold" : "text-slate-300"
                        }`}
                        numberOfLines={1}
                      >
                        {subItem.label}
                      </Text>
                    </View>

                    {subItem.badge && (
                      <View
                        className={`px-1.5 py-0.2 rounded ${
                          active
                            ? "bg-white/20"
                            : "bg-emerald-950/80 border border-emerald-800/60"
                        }`}
                      >
                        <Text
                          className={`text-[8px] font-mono font-black ${
                            active ? "text-white" : "text-emerald-400"
                          }`}
                        >
                          {subItem.badge}
                        </Text>
                      </View>
                    )}
                  </Pressable>
                );
              })}
            </View>
          )}
        </View>
      </ScrollView>

      {/* ── Compact Status Footer ───────────────────────── */}
      <View className="px-3.5 py-2.5 border-t border-dark-border bg-dark-card">
        <View className="flex-row items-center gap-2">
          <View
            style={{
              width: 6,
              height: 6,
              borderRadius: 3,
              backgroundColor: apiChecking
                ? THEME_COLORS.warning
                : apiOnline
                ? THEME_COLORS.success
                : THEME_COLORS.danger,
            }}
          />
          <Text className="text-[10px] text-slate-400 font-medium" numberOfLines={1}>
            {apiChecking
              ? "Connecting…"
              : apiOnline
              ? "FastAPI Live"
              : "API Offline"}
          </Text>
        </View>
        <Text className="text-[8px] text-slate-600 mt-0.5">AIRIS_TEST (Read-only)</Text>
      </View>
    </View>
  );
};
