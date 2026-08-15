import { campaignApi } from "@/api/campaign.api";
import { apiClient } from "@/api/client";

jest.mock("@/api/client", () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

describe("Campaign API Domain Client", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("calls getCampaigns with proper endpoint", async () => {
    const mockData = [{ CampID: 1, CampName: "Diwali 2025" }];
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockData });

    const result = await campaignApi.getCampaigns();
    expect(apiClient.get).toHaveBeenCalledWith("/campaigns");
    expect(result).toEqual(mockData);
  });

  it("calls getCampaignDetail with specific CampID", async () => {
    const mockDetail = { CampID: 2, CampName: "Ponk 2026", Items: [], Events: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockDetail });

    const result = await campaignApi.getCampaignDetail(2);
    expect(apiClient.get).toHaveBeenCalledWith("/campaigns/2");
    expect(result).toEqual(mockDetail);
  });

  it("serializes pagination and filter parameters in getPRTransactions", async () => {
    const mockRes = { total: 10, limit: 25, offset: 0, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockRes });

    const params = {
      camp_id: 3,
      review_status_id: 550,
      delivery_status_id: 555,
      search: "John",
      limit: 25,
      offset: 50,
    };

    const result = await campaignApi.getPRTransactions(params);
    expect(apiClient.get).toHaveBeenCalledWith(
      "/campaigns/transactions?camp_id=3&review_status_id=550&delivery_status_id=555&search=John&limit=25&offset=50"
    );
    expect(result).toEqual(mockRes);
  });

  it("serializes audit log parameters in getCampaignAuditLog", async () => {
    const mockLogs = { total: 5, limit: 10, offset: 0, items: [] };
    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockLogs });

    const params = { camp_id: 1, limit: 10, offset: 0 };
    const result = await campaignApi.getCampaignAuditLog(params);
    expect(apiClient.get).toHaveBeenCalledWith("/campaigns/audit-log?camp_id=1&limit=10&offset=0");
    expect(result).toEqual(mockLogs);
  });
});
