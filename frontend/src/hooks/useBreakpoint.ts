import { useWindowDimensions } from "react-native";
import { BREAKPOINTS } from "@/constants/layout";

export type Breakpoint = "xs" | "sm" | "md" | "lg" | "xl" | "2xl";

export interface BreakpointState {
  /** Current named breakpoint based on window width */
  breakpoint: Breakpoint;
  /** Raw window width */
  width: number;
  /** Raw window height */
  height: number;
  // Convenience booleans
  isMobile: boolean;    // < sm (< 640)
  isTablet: boolean;    // sm – lg (640–1023)
  isDesktop: boolean;   // ≥ lg (≥ 1024)
  // Shorthand for named thresholds
  isSm: boolean;
  isMd: boolean;
  isLg: boolean;
  isXl: boolean;
  is2Xl: boolean;
}

/**
 * Returns the current window breakpoint and convenience booleans.
 * Re-renders automatically on window resize (web) or orientation change (native).
 *
 * Usage:
 *   const { isDesktop, width } = useBreakpoint();
 */
export function useBreakpoint(): BreakpointState {
  const { width, height } = useWindowDimensions();

  const isSm = width >= BREAKPOINTS.SM;
  const isMd = width >= BREAKPOINTS.MD;
  const isLg = width >= BREAKPOINTS.LG;
  const isXl = width >= BREAKPOINTS.XL;
  const is2Xl = width >= BREAKPOINTS.XXL;

  let breakpoint: Breakpoint = "xs";
  if (is2Xl) breakpoint = "2xl";
  else if (isXl) breakpoint = "xl";
  else if (isLg) breakpoint = "lg";
  else if (isMd) breakpoint = "md";
  else if (isSm) breakpoint = "sm";

  return {
    breakpoint,
    width,
    height,
    isMobile: !isSm,
    isTablet: isSm && !isLg,
    isDesktop: isLg,
    isSm,
    isMd,
    isLg,
    isXl,
    is2Xl,
  };
}
