import React from "react";

type IconProps = React.HTMLAttributes<HTMLSpanElement> & {
  size?: number;
  color?: string;
  strokeWidth?: number;
};

const createMockIcon = (name: string) => {
  const IconComponent = (props: IconProps) => React.createElement("span", { "data-icon": name, ...props });
  IconComponent.displayName = `Lucide_${name}`;
  return IconComponent;
};

const defaultIcon = createMockIcon("DefaultIcon");

const iconCache: Record<string, React.FC<IconProps>> = {};

const mockModule = new Proxy(
  { __esModule: true, default: defaultIcon },
  {
    get: (target: Record<string, unknown>, prop: string | symbol) => {
      if (typeof prop === "string") {
        if (prop in target) return target[prop];
        if (!iconCache[prop]) {
          iconCache[prop] = createMockIcon(prop);
        }
        return iconCache[prop];
      }
      return defaultIcon;
    },
  }
);

module.exports = mockModule;
