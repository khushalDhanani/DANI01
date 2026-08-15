/**
 * Layout constants for responsive breakpoints and compact UI dimensions.
 */
export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  XXL: 1536,
} as const;

export const LAYOUT = {
  /** Maximum readable content column width on wide screens */
  MAX_CONTENT_WIDTH: 1440,

  /** Compact horizontal screen padding (mobile) */
  SCREEN_PADDING_MOBILE: 12,

  /** Compact horizontal screen padding (tablet) */
  SCREEN_PADDING_TABLET: 16,

  /** Compact horizontal screen padding (desktop) */
  SCREEN_PADDING_DESKTOP: 24,

  /** Sleek, compact sidebar width (desktop rail) */
  SIDEBAR_WIDTH: 200,
} as const;
