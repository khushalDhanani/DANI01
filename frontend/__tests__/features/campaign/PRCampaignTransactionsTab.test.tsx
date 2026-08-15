import React from "react";
import { render, screen } from "@testing-library/react-native";
import { PRCampaignTransactionsTab } from "@/features/modules/daylite/campaign/PRCampaignTransactionsTab";

// Mock expo-router
jest.mock("expo-router", () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock usePRTransactions hook
jest.mock("@/hooks/useCampaigns", () => ({
  usePRTransactions: () => ({
    data: {
      total: 2,
      limit: 25,
      offset: 0,
      items: [
        {
          PRID: 1,
          CampID: 1,
          PersonID: 725850,
          RecipientName: "John Doe",
          PersonTitle: "Director",
          PersonDepartment: "Operations",
          PRClassName: "Grade I",
          PRTypeName: "Campaign",
          CampReviewStatusID: 550,
          ReviewStatusName: "Approved",
          DeliveryTypeID: 553,
          DeliveryTypeName: "Courier",
          DeliveryStatusID: 555,
          DeliveryStatusName: "Delivered",
          PROwnerEmpID: 844,
          OwnerName: "Alice Smith",
          GiftOrderedDt: "2025-10-13T18:20:23",
          IsReattempt: false,
          IsActive: true,
        },
        {
          PRID: 2,
          CampID: 1,
          PersonID: 726434,
          RecipientName: "Jane Miller",
          PersonTitle: "Manager",
          PersonDepartment: "Finance",
          PRClassName: "Grade II",
          PRTypeName: "Campaign",
          CampReviewStatusID: 548,
          ReviewStatusName: "Pending",
          DeliveryTypeID: null,
          DeliveryTypeName: null,
          DeliveryStatusID: 554,
          DeliveryStatusName: "Pending",
          PROwnerEmpID: null,
          OwnerName: null,
          GiftOrderedDt: null,
          IsReattempt: false,
          IsActive: true,
        },
      ],
    },
    isLoading: false,
    isError: false,
    refetch: jest.fn(),
  }),
}));

describe("PRCampaignTransactionsTab Feature Component", () => {
  it("renders recipient transactions directory list", async () => {
    await render(<PRCampaignTransactionsTab campId={1} />);
    expect(screen.getByText("John Doe")).toBeTruthy();
    expect(screen.getByText("Jane Miller")).toBeTruthy();
    expect(screen.getByText("Alice Smith")).toBeTruthy();
    expect(screen.getByText("Unassigned PR Owner")).toBeTruthy();
  });

  it("renders review and delivery status badges with correct text", async () => {
    await render(<PRCampaignTransactionsTab campId={1} />);
    expect(screen.getByText("Review: Approved")).toBeTruthy();
    expect(screen.getByText("Review: Pending")).toBeTruthy();
    expect(screen.getByText("Delivery: Delivered")).toBeTruthy();
  });
});
