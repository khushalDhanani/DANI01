import React, { useRef, useState } from "react";
import { Animated, Pressable, View } from "react-native";
import { useBreakpoint } from "@/hooks/useBreakpoint";
import { LAYOUT } from "@/constants/layout";
import { Sidebar } from "@/components/layout/Sidebar";
import { MobileHeader } from "@/components/layout/MobileHeader";

interface AppShellProps {
  children: React.ReactNode;
}

/**
 * Application Shell — responsive layout controller.
 *
 * Desktop (≥ lg / 1024px):
 *   ┌──────────────┬──────────────────────────────┐
 *   │   Sidebar    │   Content (Slot)             │
 *   │  (260px)     │                              │
 *   └──────────────┴──────────────────────────────┘
 *
 * Mobile / Tablet (< 1024px):
 *   ┌──────────────────────────────┐
 *   │   MobileHeader  [≡]         │
 *   ├──────────────────────────────┤
 *   │   Content (Slot)            │
 *   └──────────────────────────────┘
 *   [Animated drawer slides in from left on menu press]
 *
 * No business logic. No API calls. No Zustand.
 * Sidebar open/close is local ephemeral UI state.
 */
export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const { isDesktop } = useBreakpoint();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const slideAnim = useRef(new Animated.Value(-LAYOUT.SIDEBAR_WIDTH)).current;
  const backdropAnim = useRef(new Animated.Value(0)).current;

  const openDrawer = () => {
    setDrawerOpen(true);
    Animated.parallel([
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 260,
        useNativeDriver: true,
      }),
      Animated.timing(backdropAnim, {
        toValue: 1,
        duration: 260,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const closeDrawer = () => {
    Animated.parallel([
      Animated.timing(slideAnim, {
        toValue: -LAYOUT.SIDEBAR_WIDTH,
        duration: 220,
        useNativeDriver: true,
      }),
      Animated.timing(backdropAnim, {
        toValue: 0,
        duration: 220,
        useNativeDriver: true,
      }),
    ]).start(() => setDrawerOpen(false));
  };

  // ── Desktop layout ─────────────────────────────────────────
  if (isDesktop) {
    return (
      <View style={{ flex: 1, height: "100%", minHeight: 0 }} className="flex-row bg-dark-bg">
        <Sidebar />
        <View style={{ flex: 1, minHeight: 0, minWidth: 0, height: "100%", overflow: "hidden" }}>
          {children}
        </View>
      </View>
    );
  }

  // ── Mobile / Tablet layout ─────────────────────────────────
  return (
    <View style={{ flex: 1, height: "100%", minHeight: 0 }} className="bg-dark-bg">
      <MobileHeader onMenuPress={openDrawer} />

      {/* Route content */}
      <View style={{ flex: 1, minHeight: 0, minWidth: 0, height: "100%", overflow: "hidden" }}>
        {children}
      </View>

      {/* Drawer overlay — only mounted when open */}
      {drawerOpen && (
        <>
          {/* Backdrop */}
          <Animated.View
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: "rgba(0,0,0,0.55)",
              zIndex: 40,
              opacity: backdropAnim,
            }}
          >
            <Pressable
              style={{ flex: 1 }}
              onPress={closeDrawer}
              accessibilityLabel="Close navigation menu"
            />
          </Animated.View>

          {/* Sliding drawer panel */}
          <Animated.View
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              bottom: 0,
              width: LAYOUT.SIDEBAR_WIDTH,
              zIndex: 50,
              transform: [{ translateX: slideAnim }],
            }}
          >
            <Sidebar isDrawer onClose={closeDrawer} />
          </Animated.View>
        </>
      )}
    </View>
  );
};
