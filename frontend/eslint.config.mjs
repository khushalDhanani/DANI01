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
      "@typescript-eslint/no-unused-vars": ["error", {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
        caughtErrorsIgnorePattern: "^_",
      }],
      "@typescript-eslint/explicit-function-return-type": "off",
      "@typescript-eslint/consistent-type-imports": ["warn", { prefer: "type-imports" }],

      // React rules
      "react/react-in-jsx-scope": "off",           // Not needed in React 17+
      "react/prop-types": "off",                   // TypeScript handles this
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",

      // General code quality
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "no-unused-vars": "off",                     // Handled by @typescript-eslint/no-unused-vars
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
      "babel.config.js",
      "metro.config.js",
    ],
  },
];
