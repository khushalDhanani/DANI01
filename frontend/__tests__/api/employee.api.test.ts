import { employeeApi } from "@/api/employee.api";
import { apiClient } from "@/api/client";

jest.mock("@/api/client", () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

describe("Employee API Domain Client", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("calls getOverview with proper endpoint", async () => {
    const mockOverview = {
      status_counts: { total: 3091, active: 1316, inactive: 116, resigned: 1555, deleted: 104 },
    };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockOverview });

    const result = await employeeApi.getOverview();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/EMPLOYEE/overview");
    expect(result).toEqual(mockOverview);
  });

  it("calls getStructure with proper endpoint", async () => {
    const mockStructure = { master_table: "dbo.EmployeeMst", canonical_key: "EmpID", tables: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockStructure });

    const result = await employeeApi.getStructure();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/EMPLOYEE/structure");
    expect(result).toEqual(mockStructure);
  });

  it("calls getQuality with proper endpoint", async () => {
    const mockQuality = { overall_health_score: 88.5, critical_issues_count: 29, rules: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockQuality });

    const result = await employeeApi.getQuality();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/EMPLOYEE/quality");
    expect(result).toEqual(mockQuality);
  });

  it("calls getQualityIssues with issue code and search params", async () => {
    const mockIssues = { issue_code: "DUP_EMP_CODE", total: 20, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockIssues });

    const result = await employeeApi.getQualityIssues("DUP_EMP_CODE", "Kevin", 25, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/EMPLOYEE/quality/issues?issue=DUP_EMP_CODE&search=Kevin&limit=25&offset=0"
    );
    expect(result).toEqual(mockIssues);
  });

  it("calls getRecords with filter parameters", async () => {
    const mockRecords = { total: 100, active_count: 90, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockRecords });

    const result = await employeeApi.getRecords({ status: "ACTIVE", search: "Shah", limit: 25, offset: 0 });
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/EMPLOYEE/records?search=Shah&status=ACTIVE&limit=25&offset=0"
    );
    expect(result).toEqual(mockRecords);
  });

  it("calls getDetail with specific emp_id", async () => {
    const mockDetail = { emp_id: 3, full_name: "Kevin Shah" };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockDetail });

    const result = await employeeApi.getDetail(3);
    expect(apiClient.get).toHaveBeenCalledWith("/modules/EMPLOYEE/records/3");
    expect(result).toEqual(mockDetail);
  });
});
