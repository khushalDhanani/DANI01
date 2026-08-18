import { apiClient } from "@/api/client";
import {
  fetchContactDirectory,
  fetchContactOverview,
  fetchContactQuality,
  fetchContactQualityIssues,
} from "@/api/contact.api";

jest.mock("@/api/client", () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

describe("Contact API client", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("fetchContactOverview calls /modules/CONTACT/overview", async () => {
    const mockOverview = { total_active_employees: 1316 };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockOverview });

    const result = await fetchContactOverview();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/CONTACT/overview");
    expect(result).toEqual(mockOverview);
  });

  it("fetchContactDirectory passes query parameters properly", async () => {
    const mockDirectory = { total: 10, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockDirectory });

    const result = await fetchContactDirectory("WITH_COMPANY_EMAIL", "WITH_PRIMARY_PHONE", "John", 25, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/CONTACT/directory?email_filter=WITH_COMPANY_EMAIL&phone_filter=WITH_PRIMARY_PHONE&search=John&limit=25&offset=0"
    );
    expect(result).toEqual(mockDirectory);
  });

  it("fetchContactQuality calls /modules/CONTACT/quality", async () => {
    const mockQuality = { overall_health_score: 91.7, rules: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockQuality });

    const result = await fetchContactQuality();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/CONTACT/quality");
    expect(result).toEqual(mockQuality);
  });

  it("fetchContactQualityIssues calls /modules/CONTACT/quality/issues", async () => {
    const mockIssues = { issue_code: "MISSING_ALL_PHONES", total: 17, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockIssues });

    const result = await fetchContactQualityIssues("MISSING_ALL_PHONES", "1001", 25, 0);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/CONTACT/quality/issues?issue=MISSING_ALL_PHONES&search=1001&limit=25&offset=0"
    );
    expect(result).toEqual(mockIssues);
  });
});
