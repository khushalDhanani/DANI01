import React from "react";
import { render, screen } from "@testing-library/react-native";
import { PRCampaignOverviewTab } from "@/features/modules/daylite/campaign/PRCampaignOverviewTab";
import type { PRCampaignDetail } from "@/types/campaign.types";

const mockCampaignDetail: PRCampaignDetail = {
  CampID: 1,
  CampName: "Diwali - 2025",
  CampStatus: "Close",
  CampIsActive: true,
  TotalTransactions: 896,
  ApprovedCount: 864,
  PendingReviewCount: 0,
  RejectedCount: 32,
  DeliveredCount: 850,
  CampStartDate: "2025-10-11T11:36:23",
  CampCloseDate: "2025-10-18T11:38:01",
  Items: [
    {
      CampDetID: 1,
      CampID: 1,
      PRClassID: 1,
      PRClassName: "Grade I",
      ItemRefID: 22231,
      ItemName: "Gift Box Big",
      AdHocLimit: 50,
    },
    {
      CampDetID: 2,
      CampID: 1,
      PRClassID: 2,
      PRClassName: "Grade II",
      ItemRefID: 22232,
      ItemName: "Gift Box Small",
      AdHocLimit: null,
    },
  ],
  Events: [
    {
      ID: 1,
      CampID: 1,
      LocID: 8,
      DLEventID: 157531,
      EventSubject: "Diwali Celebration Event",
      EventFromDate: "2025-10-15T10:00:00",
    },
  ],
};

describe("PRCampaignOverviewTab Feature Component", () => {
  it("renders loading skeleton state when isLoading is true", async () => {
    const { toJSON } = await render(
      <PRCampaignOverviewTab campaign={undefined} isLoading={true} />
    );
    expect(toJSON()).toBeTruthy();
  });

  it("renders empty selection message when no campaign is provided", async () => {
    await render(<PRCampaignOverviewTab campaign={undefined} isLoading={false} />);
    expect(screen.getByText("No Campaign Selected")).toBeTruthy();
  });

  it("renders authoritative campaign scale metrics correctly", async () => {
    await render(
      <PRCampaignOverviewTab campaign={mockCampaignDetail} isLoading={false} />
    );
    expect(screen.getByText("896")).toBeTruthy();
    expect(screen.getByText("864")).toBeTruthy();
    expect(screen.getByText("850")).toBeTruthy();
    expect(screen.getByText("32")).toBeTruthy();
  });

  it("renders configured gift items per PR Grade without key collisions", async () => {
    await render(
      <PRCampaignOverviewTab campaign={mockCampaignDetail} isLoading={false} />
    );
    expect(screen.getByText("Gift Box Big")).toBeTruthy();
    expect(screen.getByText("Gift Box Small")).toBeTruthy();
    expect(screen.getByText("Grade I")).toBeTruthy();
    expect(screen.getByText("Grade II")).toBeTruthy();
  });
});
