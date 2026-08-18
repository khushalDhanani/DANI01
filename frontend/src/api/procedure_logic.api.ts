import { apiClient } from "./client";
import { triggerBrowserDownload } from "./modules.api";
import type {
  LogicInconsistenciesListResponse,
  ProcedureLogicOverviewResponse,
  SqlObjectDetailResponse,
  SqlObjectListResponse,
} from "@/types/procedure_logic.types";

export async function fetchProcedureLogicOverview(): Promise<ProcedureLogicOverviewResponse> {
  const response = await apiClient.get<ProcedureLogicOverviewResponse>(
    "/modules/PROCEDURE_LOGIC/overview"
  );
  return response.data;
}

export async function fetchSqlObjectsCatalog(params?: {
  object_type?: string;
  module?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<SqlObjectListResponse> {
  const queryParams = new URLSearchParams();
  if (params?.object_type) queryParams.set("object_type", params.object_type);
  if (params?.module) queryParams.set("module", params.module);
  if (params?.search) queryParams.set("search", params.search);
  if (params?.limit) queryParams.set("limit", params.limit.toString());
  if (params?.offset !== undefined) queryParams.set("offset", params.offset.toString());

  const queryStr = queryParams.toString();
  const response = await apiClient.get<SqlObjectListResponse>(
    `/modules/PROCEDURE_LOGIC/objects${queryStr ? `?${queryStr}` : ""}`
  );
  return response.data;
}

export async function fetchLogicInconsistencies(params?: {
  severity?: string;
  rule_code?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<LogicInconsistenciesListResponse> {
  const queryParams = new URLSearchParams();
  if (params?.severity) queryParams.set("severity", params.severity);
  if (params?.rule_code) queryParams.set("rule_code", params.rule_code);
  if (params?.search) queryParams.set("search", params.search);
  if (params?.limit) queryParams.set("limit", params.limit.toString());
  if (params?.offset !== undefined) queryParams.set("offset", params.offset.toString());

  const queryStr = queryParams.toString();
  const response = await apiClient.get<LogicInconsistenciesListResponse>(
    `/modules/PROCEDURE_LOGIC/inconsistencies${queryStr ? `?${queryStr}` : ""}`
  );
  return response.data;
}

export async function fetchSqlObjectDetail(objectId: number): Promise<SqlObjectDetailResponse> {
  const response = await apiClient.get<SqlObjectDetailResponse>(
    `/modules/PROCEDURE_LOGIC/objects/${objectId}`
  );
  return response.data;
}

export async function exportLogicInconsistencies(params?: {
  severity?: string;
  rule_code?: string;
  search?: string;
}): Promise<void> {
  const queryParams = new URLSearchParams();
  if (params?.severity) queryParams.set("severity", params.severity);
  if (params?.rule_code) queryParams.set("rule_code", params.rule_code);
  if (params?.search) queryParams.set("search", params.search);

  const queryStr = queryParams.toString();
  const response = await apiClient.get(
    `/modules/PROCEDURE_LOGIC/export${queryStr ? `?${queryStr}` : ""}`,
    { responseType: "blob" }
  );

  const contentDisposition =
    response.headers["content-disposition"] || response.headers["Content-Disposition"];
  const filename = `sql_logic_inconsistencies_${(params?.severity || params?.rule_code || "all").toLowerCase()}.csv`;
  triggerBrowserDownload(response.data as Blob, filename, contentDisposition);
}

export const procedureLogicApi = {
  getOverview: fetchProcedureLogicOverview,
  getObjects: fetchSqlObjectsCatalog,
  getInconsistencies: fetchLogicInconsistencies,
  getObjectDetail: fetchSqlObjectDetail,
  exportInconsistencies: exportLogicInconsistencies,
};
