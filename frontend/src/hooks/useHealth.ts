import { useQuery } from "@tanstack/react-query";
import { healthApi } from "@/api/health.api";

export const useHealth = () => {
  return useQuery({
    queryKey: ["health", "api"],
    queryFn: healthApi.getHealth,
    staleTime: 10 * 1000,
    retry: 2,
  });
};

export const useDatabaseHealth = () => {
  return useQuery({
    queryKey: ["health", "database"],
    queryFn: healthApi.getDatabaseHealth,
    staleTime: 10 * 1000,
    retry: 2,
  });
};
