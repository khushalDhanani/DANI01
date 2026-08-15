import React from "react";
import { Pressable, Text, View } from "react-native";
import { usePathname, useRouter } from "expo-router";
import type { Href } from "expo-router";
import { Database, Activity, Layers } from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";

export const Header: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();

  const navItems = [
    { label: "Overview", href: "/", icon: Database },
    { label: "Database Explorer", href: "/database", icon: Layers },
    { label: "Analysis Runs", href: "/analysis", icon: Activity },
  ];

  return (
    <View className="bg-dark-card border-b border-dark-border px-6 py-4 flex-row items-center justify-between z-10">
      {/* Brand & Database Badge */}
      <View className="flex-row items-center gap-4">
        <Pressable
          onPress={() => router.push("/" as Href)}
          className="flex-row items-center gap-2.5"
        >
          <View className="w-9 h-9 rounded-xl bg-blue-600 items-center justify-center shadow-lg shadow-blue-500/20">
            <Database size={20} color={THEME_COLORS.onPrimary} />
          </View>
          <View>
            <Text className="text-lg font-black text-white tracking-tight">
              AIRIS <Text className="text-blue-400">INSIGHTS</Text>
            </Text>
            <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              DB Intelligence & Analytics
            </Text>
          </View>
        </Pressable>

        <View className="hidden md:flex flex-row items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
          <View className="w-2 h-2 rounded-full bg-emerald-400" />
          <Text className="text-xs font-semibold text-slate-300">
            AIRIS_TEST <Text className="text-slate-500">•</Text> Read-Only
          </Text>
        </View>
      </View>

      {/* Nav Tabs */}
      <View className="flex-row items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800/80">
        {navItems.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          const Icon = item.icon;

          return (
            <Pressable
              key={item.href}
              onPress={() => router.push(item.href as Href)}
              className={`flex-row items-center gap-2 px-3.5 py-1.5 rounded-lg transition-all ${
                isActive
                  ? "bg-blue-600 shadow-md shadow-blue-600/30"
                  : "hover:bg-slate-800/60"
              }`}
            >
              <Icon size={16} color={isActive ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
              <Text
                className={`text-xs font-bold tracking-wide ${
                  isActive ? "text-white" : "text-slate-400"
                }`}
              >
                {item.label}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
};
