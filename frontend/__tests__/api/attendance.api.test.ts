import {
  fetchAttendanceDirectory,
  fetchAttendanceOverview,
  fetchAttendanceQuality,
  fetchAttendanceQualityIssues,
  fetchLeaveApplications,
  fetchLeaveBalances,
  fetchLeaveOverview,
} from "../../src/api/attendance.api";
import { apiClient } from "../../src/api/client";

jest.mock("../../src/api/client", () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

describe("Attendance API Client", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("fetches attendance overview", async () => {
    const mockData = {
      attendance_metrics: { total_attendance_records: 100 },
      punch_metrics: { total_punches_logged: 200 },
      shift_distribution: [],
    };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockData });

    const result = await fetchAttendanceOverview();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/ATTENDANCE/overview");
    expect(result.attendance_metrics.total_attendance_records).toBe(100);
  });

  it("fetches attendance directory logs", async () => {
    const mockData = { total: 1, limit: 20, offset: 0, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockData });

    const result = await fetchAttendanceDirectory("PRESENT", "John", 20, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/ATTENDANCE/directory",
      { params: { status: "PRESENT", search: "John", limit: 20, offset: 0 } }
    );
    expect(result.total).toBe(1);
  });

  it("fetches leave overview", async () => {
    const mockData = { total_leave_requests: 10, approved_requests: 8 };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockData });

    const result = await fetchLeaveOverview();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/ATTENDANCE/leave/overview");
    expect(result.approved_requests).toBe(8);
  });

  it("fetches leave applications", async () => {
    const mockData = { total: 0, limit: 20, offset: 0, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockData });

    const result = await fetchLeaveApplications("APPROVED", undefined, 20, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/ATTENDANCE/leave/applications",
      { params: { status: "APPROVED", limit: 20, offset: 0 } }
    );
    expect(result.total).toBe(0);
  });

  it("fetches leave balances", async () => {
    const mockData = { total: 0, limit: 20, offset: 0, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockData });

    const result = await fetchLeaveBalances("202607", undefined, 20, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/ATTENDANCE/leave/balances",
      { params: { year_month: "202607", limit: 20, offset: 0 } }
    );
    expect(result.total).toBe(0);
  });

  it("fetches attendance quality audit", async () => {
    const mockData = { overall_health_score: 95.0, rules: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockData });

    const result = await fetchAttendanceQuality();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/ATTENDANCE/quality");
    expect(result.overall_health_score).toBe(95.0);
  });

  it("fetches attendance quality issues drilldown", async () => {
    const mockData = { issue_code: "PUNCH_OUT_BEFORE_IN", total: 0, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockData });

    const result = await fetchAttendanceQualityIssues("PUNCH_OUT_BEFORE_IN", undefined, 20, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/ATTENDANCE/quality/issues",
      { params: { issue: "PUNCH_OUT_BEFORE_IN", limit: 20, offset: 0 } }
    );
    expect(result.issue_code).toBe("PUNCH_OUT_BEFORE_IN");
  });

});
