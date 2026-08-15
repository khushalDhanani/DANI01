import React from "react";
import { render, screen } from "@testing-library/react-native";
import { PRCampaignAuditLogTab } from "@/features/modules/daylite/campaign/PRCampaignAuditLogTab";

jest.mock("@/hooks/useCampaigns", () => ({
  useCampaignAuditLog: () => ({
    data: {
      total: 2,
      limit: 25,
      offset: 0,
      items: [
        {
          TransactionID: 1,
          CampID: 2,
          CampName: "Ponk - 20252026",
          PRID: 969,
          TransactionStatusID: 551,
          StatusName: "Reject",
          TransactionDesc: "Reject",
          ModuleName: "PRReviewStatus",
          EntUser: "Rohan Desai",
          EntDt: "2025-11-22T11:42:12",
          CorrelationId: "45C83C57-AF8D-42B7-B0AB-41DC174265A2",
          Severity: 2,
        },
        {
          TransactionID: 2,
          CampID: 2,
          CampName: "Ponk - 20252026",
          PRID: 1659,
          TransactionStatusID: 550,
          StatusName: "Approved",
          TransactionDesc: "Approved",
          ModuleName: "PRReviewStatus",
          EntUser: "Alice Smith",
          EntDt: "2025-11-22T11:45:00",
          CorrelationId: "12360FF4-0C77-4081-BE39-147AEAF5D333",
          Severity: 1,
        },
      ],
    },
    isLoading: false,
    isError: false,
    refetch: jest.fn(),
  }),
}));

describe("PRCampaignAuditLogTab Feature Component", () => {
  it("renders audit trail entries with user signatures and correlation IDs", async () => {
    await render(<PRCampaignAuditLogTab campId={2} />);
    expect(screen.getByText("Rohan Desai")).toBeTruthy();
    expect(screen.getByText("Alice Smith")).toBeTruthy();
    expect(screen.getByText("PR #969")).toBeTruthy();
    expect(screen.getByText("PR #1659")).toBeTruthy();
  });
});
