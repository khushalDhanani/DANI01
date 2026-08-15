// @ts-check
import js from "@eslint/js";
import tsPlugin from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";

/** React Native + Expo global variables */
const reactNativeGlobals = {
  // Node / Metro bundler
  process: "readonly",
  // Browser globals available in React Native web
  alert: "readonly",
  console: "readonly",
  setTimeout: "readonly",
  clearTimeout: "readonly",
  setInterval: "readonly",
  clearInterval: "readonly",
  fetch: "readonly",
  // React Native globals
  __DEV__: "readonly",
};

/** Jest test runner globals */
const jestGlobals = {
  jest: "readonly",
  describe: "readonly",
  it: "readonly",
  test: "readonly",
  expect: "readonly",
  beforeEach: "readonly",
  afterEach: "readonly",
  beforeAll: "readonly",
  afterAll: "readonly",
  module: "readonly",
  require: "readonly",
};

/** @type {import("eslint").Linter.Config[]} */
export default [
  // Base JS recommended rules
  js.configs.recommended,

  // TypeScript + React files
  {
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: {
      globals: reactNativeGlobals,
      parser: tsParser,
      parserOptions: {
        project: "./tsconfig.json",
        ecmaFeatures: { jsx: true },
        ecmaVersion: "latest",
        sourceType: "module",
      },
    },
    plugins: {
      "@typescript-eslint": tsPlugin,
      react: reactPlugin,
      "react-hooks": reactHooksPlugin,
    },
    settings: {
      react: { version: "detect" },
    },
    rules: {
      // TypeScript strict rules
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
      "@typescript-eslint/explicit-function-return-type": "off",
      "@typescript-eslint/consistent-type-imports": [
        "error",
        { prefer: "type-imports", fixStyle: "separate-type-imports" },
      ],

      // React rules
      "react/react-in-jsx-scope": "off", // Not needed in React 17+
      "react/prop-types": "off", // TypeScript handles this
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "error",

      // General code quality
      "no-console": ["error", { allow: ["warn", "error"] }],
      "no-unused-vars": "off", // Handled by @typescript-eslint/no-unused-vars
    },
  },

  // Test files and test mocks (allow Jest globals)
  {
    files: ["**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx", "src/__mocks__/**/*"],
    languageOptions: {
      globals: {
        ...reactNativeGlobals,
        ...jestGlobals,
      },
    },
  },

  // Architectural boundary rules for screens, features, components, and hooks:
  // Forbid direct Axios or raw apiClient imports in screens/features/hooks (must use TanStack Query hooks and domain API modules)
  {
    files: [
      "app/**/*.ts",
      "app/**/*.tsx",
      "src/features/**/*.ts",
      "src/features/**/*.tsx",
      "src/components/**/*.ts",
      "src/components/**/*.tsx",
      "src/hooks/**/*.ts",
      "src/hooks/**/*.tsx",
    ],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          paths: [
            {
              name: "axios",
              message:
                "Do not call Axios here. Use a TanStack Query hook and domain API module.",
            },
            {
              name: "@/api/client",
              message:
                "Do not access apiClient directly here. Use a domain API module.",
            },
          ],
        },
      ],
    },
  },

  // Ignore generated and config files
  {
    ignores: [
      "dist/",
      ".expo/",
      "node_modules/",
      "scripts/",
      "*.config.js",
      "*.config.ts",
      "*.config.mts",
      "babel.config.js",
      "metro.config.js",
      "jest.config.js",
    ],
  },
];
