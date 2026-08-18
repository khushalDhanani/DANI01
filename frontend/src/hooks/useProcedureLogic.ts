import { useQuery } from "@tanstack/react-query";
import { procedureLogicApi } from "@/api/procedure_logic.api";
import { QUERY_KEYS } from "@/constants/config";
import type {
  LogicInconsistenciesListResponse,
  ProcedureLogicOverviewResponse,
  SqlObjectDetailResponse,
  SqlObjectListResponse,
} from "@/types/procedure_logic.types";

export function useProcedureLogicOverview() {
  return useQuery<ProcedureLogicOverviewResponse>({
    queryKey: QUERY_KEYS.PROCEDURE_LOGIC.OVERVIEW,
    queryFn: () => procedureLogicApi.getOverview(),
    staleTime: 30000,
  });
}

export function useSqlObjectsCatalog(params?: {
  objectType?: string;
  module?: string;
  search?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery<SqlObjectListResponse>({
    queryKey: QUERY_KEYS.PROCEDURE_LOGIC.OBJECTS(
      params?.objectType,
      params?.module,
      params?.search,
      params?.limit,
      params?.offset
    ),
    queryFn: () =>
      procedureLogicApi.getObjects({
        object_type: params?.objectType,
        module: params?.module,
        search: params?.search,
        limit: params?.limit,
        offset: params?.offset,
      }),
    staleTime: 30000,
  });
}

export function useLogicInconsistencies(params?: {
  severity?: string;
  ruleCode?: string;
  search?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery<LogicInconsistenciesListResponse>({
    queryKey: QUERY_KEYS.PROCEDURE_LOGIC.INCONSISTENCIES(
      params?.severity,
      params?.ruleCode,
      params?.search,
      params?.limit,
      params?.offset
    ),
    queryFn: () =>
      procedureLogicApi.getInconsistencies({
        severity: params?.severity,
        rule_code: params?.ruleCode,
        search: params?.search,
        limit: params?.limit,
        offset: params?.offset,
      }),
    staleTime: 30000,
  });
}

export function useSqlObjectDetail(objectId: number | null) {
  return useQuery<SqlObjectDetailResponse>({
    queryKey: QUERY_KEYS.PROCEDURE_LOGIC.OBJECT_DETAIL(objectId ?? 0),
    queryFn: () => procedureLogicApi.getObjectDetail(objectId!),
    enabled: Boolean(objectId),
  });
}
