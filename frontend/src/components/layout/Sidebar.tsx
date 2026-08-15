import React, { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { usePathname, useRouter } from "expo-router";
import type { Href } from "expo-router";
import {
  ChevronDown,
  ChevronRight,
  Database,
} from "lucide-react-native";
import { NAV_SECTIONS } from "@/constants/navigation";
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

  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {};
    NAV_SECTIONS.forEach((section) => {
      section.groups?.forEach((group) => {
        initial[group.id] = group.defaultExpanded ?? true;
      });
    });
    return initial;
  });

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

  const toggleGroup = (groupId: string) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [groupId]: !prev[groupId],
    }));
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
          </View>
        </View>
      </View>

      {/* ── Navigation Sections (Scrollable) ─────────────── */}
      <ScrollView
        className="flex-1 px-2 pt-3"
        contentContainerStyle={{ gap: 14, paddingBottom: 16 }}
        showsVerticalScrollIndicator={false}
      >
        {NAV_SECTIONS.map((section) => (
          <View key={section.id} className="gap-0.5">
            {section.title && (
              <Text className="text-[9px] uppercase font-bold text-slate-500 tracking-widest px-2.5 mb-1">
                {section.title}
              </Text>
            )}

            {/* Flat items in section */}
            {section.items?.map((item) => {
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
                    {Icon && (
                      <Icon
                        size={15}
                        color={
                          active ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted
                        }
                      />
                    )}
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

            {/* Hierarchical groups in section */}
            {section.groups?.map((group) => {
              const isExpanded = expandedGroups[group.id] ?? false;
              const isChildActive = group.children.some((child) =>
                isItemActive(child.href)
              );
              const isGroupHrefActive = group.href
                ? isItemActive(group.href)
                : false;
              const isGroupActive = isGroupHrefActive || isChildActive;
              const GroupIcon = group.icon;

              return (
                <View key={group.id} className="gap-0.5">
                  {/* Group header row with split tap targets */}
                  <View
                    className={`flex-row items-center justify-between px-2.5 py-2 rounded-lg transition-all ${
                      isGroupActive && !isExpanded
                        ? "bg-blue-600 shadow-sm"
                        : "hover:bg-slate-800/60 active:bg-slate-800"
                    }`}
                  >
                    {/* Tap target 1: Label/Icon -> Navigates to group.href */}
                    <Pressable
                      onPress={() => {
                        if (group.href) {
                          handleNav(group.href);
                          if (!isExpanded) {
                            toggleGroup(group.id);
                          }
                        } else {
                          toggleGroup(group.id);
                        }
                      }}
                      accessibilityRole="button"
                      accessibilityLabel={`Navigate to ${group.label}`}
                      className="flex-row items-center gap-2.5 flex-1"
                    >
                      {GroupIcon && (
                        <GroupIcon
                          size={15}
                          color={
                            isGroupActive && !isExpanded
                              ? THEME_COLORS.onPrimary
                              : THEME_COLORS.primaryIcon
                          }
                        />
                      )}
                      <Text
                        className={`text-xs font-bold ${
                          isGroupActive && !isExpanded
                            ? "text-white"
                            : "text-slate-100"
                        }`}
                      >
                        {group.label}
                      </Text>
                    </Pressable>

                    {/* Tap target 2: Chevron arrow icon -> Toggles expand/collapse ONLY */}
                    <Pressable
                      onPress={() => toggleGroup(group.id)}
                      accessibilityRole="button"
                      accessibilityLabel={`Toggle ${group.label} group`}
                      className="p-1 -mr-1 rounded hover:bg-slate-700/50 active:bg-slate-700"
                    >
                      {isExpanded ? (
                        <ChevronDown size={14} color={THEME_COLORS.textMuted} />
                      ) : (
                        <ChevronRight size={14} color={THEME_COLORS.textMuted} />
                      )}
                    </Pressable>
                  </View>

                  {/* Indented children sub-items */}
                  {isExpanded && (
                    <View className="pl-4 pr-1 mt-0.5 border-l-2 border-slate-800 ml-3.5 gap-0.5">
                      {group.children.map((subItem) => {
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
                              {SubIcon && (
                                <SubIcon
                                  size={13}
                                  color={
                                    active
                                      ? THEME_COLORS.onPrimary
                                      : THEME_COLORS.textMuted
                                  }
                                />
                              )}
                              <Text
                                className={`text-xs font-medium ${
                                  active
                                    ? "text-white font-semibold"
                                    : "text-slate-300"
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
              );
            })}
          </View>
        ))}
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
