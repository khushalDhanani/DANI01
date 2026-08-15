import React from "react";
import { SafeAreaView, ScrollView, View } from "react-native";
import { useBreakpoint } from "@/hooks/useBreakpoint";
import { LAYOUT } from "@/constants/layout";

interface PageContainerProps {
  children: React.ReactNode;
  /** Allow the content area to scroll vertically */
  scrollable?: boolean;
}

/**
 * Content area wrapper for route screens.
 * Compact padding and maximum responsive data density with cross-platform scrolling support.
 */
export const PageContainer: React.FC<PageContainerProps> = ({
  children,
  scrollable = true,
}) => {
  const { isDesktop, isTablet } = useBreakpoint();

  const horizontalPadding = isDesktop
    ? LAYOUT.SCREEN_PADDING_DESKTOP
    : isTablet
    ? LAYOUT.SCREEN_PADDING_TABLET
    : LAYOUT.SCREEN_PADDING_MOBILE;

  if (scrollable) {
    return (
      <SafeAreaView style={{ flex: 1, height: "100%", minHeight: 0 }} className="bg-dark-bg">
        <ScrollView
          style={{ flex: 1, height: "100%" }}
          contentContainerStyle={{
            flexGrow: 1,
            paddingHorizontal: horizontalPadding,
            paddingTop: 12,
            paddingBottom: 20,
          }}
          showsVerticalScrollIndicator={true}
          keyboardShouldPersistTaps="handled"
          nestedScrollEnabled={true}
        >
          <View
            style={{
              width: "100%",
              maxWidth: isDesktop ? LAYOUT.MAX_CONTENT_WIDTH : undefined,
              alignSelf: "center",
            }}
          >
            {children}
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, height: "100%", minHeight: 0 }} className="bg-dark-bg">
      <View
        style={{
          flex: 1,
          height: "100%",
          minHeight: 0,
          width: "100%",
          maxWidth: isDesktop ? LAYOUT.MAX_CONTENT_WIDTH : undefined,
          alignSelf: "center",
          paddingHorizontal: horizontalPadding,
          paddingTop: 12,
          paddingBottom: 20,
        }}
      >
        {children}
      </View>
    </SafeAreaView>
  );
};
