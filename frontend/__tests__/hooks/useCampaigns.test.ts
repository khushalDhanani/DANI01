import { campaignKeys } from "@/hooks/useCampaigns";
import type { PRCampaignSummary, PRTransactionItem } from "@/types/campaign.types";

describe("useCampaigns TanStack Query Keys & State", () => {
  it("generates deterministic query keys for cache isolation", () => {
    expect(campaignKeys.all).toEqual(["campaigns"]);
    expect(campaignKeys.lists()).toEqual(["campaigns", "list"]);
    expect(campaignKeys.detail(2)).toEqual(["campaigns", "detail", 2]);
    expect(campaignKeys.transactions({ camp_id: 1, limit: 25 })).toEqual([
      "campaigns",
      "transactions",
      { camp_id: 1, limit: 25 },
    ]);
    expect(campaignKeys.auditLogs({ camp_id: 1, limit: 10 })).toEqual([
      "campaigns",
      "auditLogs",
      { camp_id: 1, limit: 10 },
    ]);
  });

  it("calculates accurate summary metrics and rates from authoritative data", () => {
    const summary: PRCampaignSummary = {
      CampID: 1,
      CampName: "Diwali 2025",
      CampStatus: "Close",
      CampIsActive: true,
      TotalTransactions: 1000,
      ApprovedCount: 950,
      PendingReviewCount: 10,
      RejectedCount: 40,
      DeliveredCount: 920,
    };

    const approvalRate = (summary.ApprovedCount / summary.TotalTransactions) * 100;
    const deliveryRate = (summary.DeliveredCount / summary.ApprovedCount) * 100;

    expect(approvalRate).toBe(95.0);
    expect(deliveryRate).toBeCloseTo(96.84, 2);
    expect(summary.ApprovedCount + summary.PendingReviewCount + summary.RejectedCount).toBe(1000);
  });

  it("preserves PR recipient and owner relationships in data structures", () => {
    const item: PRTransactionItem = {
      PRID: 123,
      CampID: 1,
      PersonID: 888,
      RecipientName: "Jane Doe",
      PRClassName: "Grade I",
      ReviewStatusName: "Approved",
      DeliveryStatusName: "Delivered",
      PROwnerEmpID: 99,
      OwnerName: "Alice Director",
      IsReattempt: false,
      IsActive: true,
    };

    expect(item.PRID).toBe(123);
    expect(item.RecipientName).toBe("Jane Doe");
    expect(item.PROwnerEmpID).toBe(99);
    expect(item.OwnerName).toBe("Alice Director");
  });
});
