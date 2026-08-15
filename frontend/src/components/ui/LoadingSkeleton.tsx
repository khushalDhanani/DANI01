import React, { useEffect, useRef } from "react";
import { Animated, View, type ViewStyle } from "react-native";
import { THEME_COLORS } from "@/constants/theme";

interface LoadingSkeletonProps {
  width?: number | string;
  height?: number | string;
  borderRadius?: number;
  style?: ViewStyle;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  width = "100%",
  height = 20,
  borderRadius = 8,
  style,
}) => {
  const opacityAnim = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(opacityAnim, {
          toValue: 0.7,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(opacityAnim, {
          toValue: 0.3,
          duration: 800,
          useNativeDriver: true,
        }),
      ])
    );
    pulse.start();

    return () => pulse.stop();
  }, [opacityAnim]);

  return (
    <Animated.View
      style={[
        {
          width: width as unknown as number,
          height: height as unknown as number,
          borderRadius,
          backgroundColor: THEME_COLORS.skeleton,
          opacity: opacityAnim,
        },
        style,
      ]}
    />
  );
};

export const CardSkeleton: React.FC = () => (
  <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3">
    <View className="flex-row items-center justify-between">
      <LoadingSkeleton width={120} height={16} />
      <LoadingSkeleton width={60} height={20} borderRadius={6} />
    </View>
    <LoadingSkeleton width="100%" height={28} />
    <View className="flex-row gap-2 pt-1">
      <LoadingSkeleton width={80} height={12} />
      <LoadingSkeleton width={100} height={12} />
    </View>
  </View>
);
