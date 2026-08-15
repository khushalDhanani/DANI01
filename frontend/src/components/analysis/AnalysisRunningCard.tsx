import React, { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, Text, View } from "react-native";
import { Clock, Square } from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";

interface AnalysisRunningCardProps {
  onStopWaiting: () => void;
  scopeText?: string;
}

export const AnalysisRunningCard: React.FC<AnalysisRunningCardProps> = ({
  onStopWaiting,
  scopeText = "Entire Database",
}) => {
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatElapsed = (sec: number): string => {
    const mins = Math.floor(sec / 60);
    const remainingSec = sec % 60;
    return `${String(mins).padStart(2, "0")}:${String(remainingSec).padStart(2, "0")}`;
  };

  return (
    <View className="bg-dark-card border border-blue-500/40 rounded-xl p-5 gap-4 shadow-lg">
      <View className="flex-row items-center justify-between flex-wrap gap-3">
        <View className="flex-row items-center gap-3">
          <ActivityIndicator size="small" color={THEME_COLORS.primary} />
          <View>
            <Text className="text-sm font-bold text-white">
              Running Synchronous Quick Analysis…
            </Text>
            <Text className="text-[11px] text-slate-400">
              Scope: <Text className="font-mono text-blue-400 font-bold">{scopeText}</Text>
            </Text>
          </View>
        </View>

        {/* Live Elapsed Timer */}
        <View className="flex-row items-center gap-1.5 bg-slate-900 border border-slate-800 px-3 py-1 rounded-lg">
          <Clock size={13} color={THEME_COLORS.warningIcon} />
          <Text className="text-xs font-mono font-bold text-amber-400">
            {formatElapsed(elapsedSeconds)}
          </Text>
          <Text className="text-[10px] text-slate-500">elapsed</Text>
        </View>
      </View>

      {/* Progress & Explanation Banner */}
      <View className="bg-slate-900/90 border border-slate-800 rounded-lg p-3 gap-1.5">
        <Text className="text-xs text-slate-300 leading-relaxed">
          The backend is executing structural discovery, bounded sampling, Polars multi-column profiling, and semantic classification across database tables synchronously.
        </Text>
        <Text className="text-[11px] text-slate-500 leading-normal">
          This operation typically requires 2–4 minutes to complete. Please keep this session active.
        </Text>
      </View>

      {/* Action Footer */}
      <View className="flex-row items-center justify-between pt-1 border-t border-slate-800">
        <Text className="text-[10px] text-slate-500">
          Client HTTP wait in progress (10m timeout)
        </Text>

        <Pressable
          onPress={onStopWaiting}
          className="bg-slate-800 hover:bg-slate-700 active:bg-slate-900 px-3 py-1.5 rounded-lg flex-row items-center gap-1.5 border border-slate-700"
          accessibilityLabel="Stop waiting for HTTP response"
          accessibilityRole="button"
        >
          <Square size={11} color={THEME_COLORS.dangerIcon} fill={THEME_COLORS.dangerIcon} />
          <Text className="text-xs font-semibold text-rose-300">
            Stop Waiting
          </Text>
        </Pressable>
      </View>
    </View>
  );
};
