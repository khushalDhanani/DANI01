import { apiClient } from "@/api/client";
import {
  fetchOrgHierarchy,
  fetchOrgOverview,
  fetchOrgQuality,
  fetchOrgQualityIssues,
  fetchOrgReportingTree,
  fetchOrgUnits,
} from "@/api/organization.api";

jest.mock("@/api/client", () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

describe("Organization API client", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("fetchOrgOverview calls /modules/ORGANIZATION/overview", async () => {
    const mockOverview = { active_employee_total: 1316 };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockOverview });

    const result = await fetchOrgOverview();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/ORGANIZATION/overview");
    expect(result).toEqual(mockOverview);
  });

  it("fetchOrgHierarchy calls /modules/ORGANIZATION/hierarchy", async () => {
    const mockHierarchy = { companies: [], total_active_employees: 1316 };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockHierarchy });

    const result = await fetchOrgHierarchy();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/ORGANIZATION/hierarchy");
    expect(result).toEqual(mockHierarchy);
  });

  it("fetchOrgUnits passes query parameters properly", async () => {
    const mockUnits = { total: 10, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockUnits });

    const result = await fetchOrgUnits("COMPANY", "Aether", 1, 20, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/ORGANIZATION/units?unit_type=COMPANY&search=Aether&comp_id=1&limit=20&offset=0"
    );
    expect(result).toEqual(mockUnits);
  });

  it("fetchOrgReportingTree calls /modules/ORGANIZATION/reporting", async () => {
    const mockTree = { roots: [], total_assigned_managers: 12 };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockTree });

    const result = await fetchOrgReportingTree();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/ORGANIZATION/reporting");
    expect(result).toEqual(mockTree);
  });

  it("fetchOrgQuality calls /modules/ORGANIZATION/quality", async () => {
    const mockQuality = { overall_health_score: 95.0, rules: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockQuality });

    const result = await fetchOrgQuality();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/ORGANIZATION/quality");
    expect(result).toEqual(mockQuality);
  });

  it("fetchOrgQualityIssues calls /modules/ORGANIZATION/quality/issues", async () => {
    const mockIssues = { total: 4, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockIssues });

    const result = await fetchOrgQualityIssues("EMPTY_LOCATIONS", "Site", 25, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/ORGANIZATION/quality/issues?issue=EMPTY_LOCATIONS&search=Site&limit=25&offset=0"
    );
    expect(result).toEqual(mockIssues);
  });
});
