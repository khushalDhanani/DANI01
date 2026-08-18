/**
 * Centralized Application & Environment Configuration
 */

const getApiBaseUrl = (): string => {
  const envUrl = process.env.EXPO_PUBLIC_API_URL;
  if (envUrl && envUrl.trim() !== "") {
    // Strip trailing slashes
    return envUrl.trim().replace(/\/+$/, "");
  }
  return "http://localhost:8000/api/v1";
};

export const ENV = {
  API_URL: getApiBaseUrl(),
  IS_DEV: process.env.NODE_ENV !== "production",
};

export const API_CONFIG = {
  BASE_URL: ENV.API_URL,
  TIMEOUT_MS: 30000,
  POLL_INTERVAL_MS: 2000,
  DEFAULT_PAGE_SIZE: 25,
};

export const QUERY_KEYS = {
  HEALTH: {
    API: ["health", "api"] as const,
    DATABASE: ["health", "database"] as const,
  },
  DATABASE: {
    SUMMARY: ["database", "summary"] as const,
    SCHEMAS: ["database", "schemas"] as const,
    TABLES: (params?: unknown) => ["database", "tables", params] as const,
    TABLE_SUMMARY: (schema: string, table: string) =>
      ["database", "tableSummary", schema, table] as const,
    COLUMNS: (schema: string, table: string) =>
      ["database", "columns", schema, table] as const,
    KEYS: (schema: string, table: string) =>
      ["database", "keys", schema, table] as const,
    INDEXES: (schema: string, table: string) =>
      ["database", "indexes", schema, table] as const,
    SAMPLE: (schema: string, table: string, limit?: number) =>
      ["database", "sample", schema, table, limit] as const,
    PROFILE: (schema: string, table: string) =>
      ["database", "profile", schema, table] as const,
    CLASSIFICATION: (schema: string, table: string) =>
      ["database", "classification", schema, table] as const,
  },
  ANALYSIS: {
    RUNS_LIST: (params?: unknown) => ["analysisRuns", "list", params] as const,
    RUN_DETAIL: (runId: string) => ["analysisRuns", "detail", runId] as const,
    RUN_TABLES: (runId: string, params?: unknown) =>
      ["analysisRuns", "tables", runId, params] as const,
    RUN_TABLE_DETAIL: (runId: string, schema: string, table: string) =>
      ["analysisRuns", "tableDetail", runId, schema, table] as const,
  },
  EMPLOYEE: {
    OVERVIEW: (compId?: number) => ["employee", "overview", compId] as const,

    STRUCTURE: ["employee", "structure"] as const,
    QUALITY: ["employee", "quality"] as const,
    QUALITY_ISSUES: (issue: string, search?: string, limit?: number, offset?: number) =>
      ["employee", "qualityIssues", issue, search, limit, offset] as const,
    RECORDS: (params?: unknown) => ["employee", "records", params] as const,
    DETAIL: (empId: number) => ["employee", "detail", empId] as const,
  },
  ORGANIZATION: {
    OVERVIEW: ["organization", "overview"] as const,
    HIERARCHY: ["organization", "hierarchy"] as const,
    UNITS: (unitType?: string, search?: string, compId?: number, limit?: number, offset?: number) =>
      ["organization", "units", unitType, search, compId, limit, offset] as const,
    REPORTING: ["organization", "reporting"] as const,
    QUALITY: ["organization", "quality"] as const,
    QUALITY_ISSUES: (issue: string, search?: string, limit?: number, offset?: number) =>
      ["organization", "qualityIssues", issue, search, limit, offset] as const,
  },
  CONTACT: {
    OVERVIEW: ["contact", "overview"] as const,
    DIRECTORY: (emailFilter?: string, phoneFilter?: string, search?: string, limit?: number, offset?: number) =>
      ["contact", "directory", emailFilter, phoneFilter, search, limit, offset] as const,
    QUALITY: ["contact", "quality"] as const,
    QUALITY_ISSUES: (issue: string, search?: string, limit?: number, offset?: number) =>
      ["contact", "qualityIssues", issue, search, limit, offset] as const,
  },
  SECURITY: {
    OVERVIEW: ["security", "overview"] as const,
    USERS: (roleId?: number, statusFilter?: string, search?: string, limit?: number, offset?: number) =>
      ["security", "users", roleId, statusFilter, search, limit, offset] as const,
    ROLES: ["security", "roles"] as const,
    ROLE_PERMISSIONS: (roleId: number) => ["security", "rolePermissions", roleId] as const,
    QUALITY: ["security", "quality"] as const,
    QUALITY_ISSUES: (issue: string, search?: string, limit?: number, offset?: number) =>
      ["security", "qualityIssues", issue, search, limit, offset] as const,
  },
  ATTENDANCE: {
    OVERVIEW: (deptId?: number, compId?: number) => ["attendance", "overview", deptId, compId] as const,
    ORG_HIERARCHY: ["attendance", "orgHierarchy"] as const,
    DEPARTMENT_DETAIL: (deptId: number) => ["attendance", "department", deptId] as const,
    EMPLOYEE_LIFETIME_ANALYTICS: (empId: number) => ["attendance", "employeeAnalytics", empId] as const,
    DIRECTORY: (statusFilter?: string, search?: string, limit?: number, offset?: number, deptId?: number, compId?: number, empId?: number) =>
      ["attendance", "directory", statusFilter, search, limit, offset, deptId, compId, empId] as const,

    LEAVE_OVERVIEW: ["attendance", "leaveOverview"] as const,
    LEAVE_APPLICATIONS: (statusFilter?: string, search?: string, limit?: number, offset?: number) =>
      ["attendance", "leaveApplications", statusFilter, search, limit, offset] as const,
    LEAVE_BALANCES: (yearMonth?: string, search?: string, limit?: number, offset?: number) =>
      ["attendance", "leaveBalances", yearMonth, search, limit, offset] as const,
    QUALITY: ["attendance", "quality"] as const,
    QUALITY_ISSUES: (issue: string, search?: string, limit?: number, offset?: number) =>
      ["attendance", "qualityIssues", issue, search, limit, offset] as const,
  },
  PAYROLL: {
    OVERVIEW: (compId?: number) => ["payroll", "overview", compId] as const,

    DIRECTORY: (statusFilter?: string, search?: string, limit?: number, offset?: number, deptId?: number, compId?: number, month?: string, empId?: number) =>
      ["payroll", "directory", statusFilter, search, limit, offset, deptId, compId, month, empId] as const,
    QUALITY: ["payroll", "quality"] as const,
    QUALITY_ISSUES: (issue: string, search?: string, limit?: number, offset?: number) =>
      ["payroll", "qualityIssues", issue, search, limit, offset] as const,
    EMPLOYEE_HISTORY: (empId: number) => ["payroll", "employeeHistory", empId] as const,
  },
  CROSS_DOMAIN_DQ: {
    OVERVIEW: (compId?: number) => ["crossDomainDQ", "overview", compId] as const,
    ISSUES: (ruleCode?: string, category?: string, search?: string, limit?: number, offset?: number, compId?: number) =>
      ["crossDomainDQ", "issues", ruleCode, category, search, limit, offset, compId] as const,
  },
  PROCEDURE_LOGIC: {
    OVERVIEW: ["procedureLogic", "overview"] as const,
    OBJECTS: (objectType?: string, module?: string, search?: string, limit?: number, offset?: number) =>
      ["procedureLogic", "objects", objectType, module, search, limit, offset] as const,
    INCONSISTENCIES: (severity?: string, ruleCode?: string, search?: string, limit?: number, offset?: number) =>
      ["procedureLogic", "inconsistencies", severity, ruleCode, search, limit, offset] as const,
    OBJECT_DETAIL: (objectId: number) => ["procedureLogic", "objectDetail", objectId] as const,
  },
};





