export interface PRCampaignItem {
  CampDetID: number;
  CampID: number;
  PRClassID: number;
  PRClassName?: string | null;
  ItemRefID?: number | null;
  ItemName?: string | null;
  AdHocLimit?: number | null;
}

export interface PRCampaignEventMapping {
  ID: number;
  CampID: number;
  LocID?: number | null;
  DLEventID?: number | null;
  EventSubject?: string | null;
  EventFromDate?: string | null;
  EventToDate?: string | null;
}

export interface PRCampaignSummary {
  CampID: number;
  CampName: string;
  CampStartDate?: string | null;
  CampReviewCutOfDate?: string | null;
  CampDelReminderDate?: string | null;
  TransCutOffDate?: string | null;
  CampCloseDate?: string | null;
  CampStatusID?: number | null;
  CampStatus?: string | null;
  CampIsActive: boolean;
  CreatedBy?: string | null;
  CreatedAt?: string | null;
  TotalTransactions: number;
  ApprovedCount: number;
  PendingReviewCount: number;
  RejectedCount: number;
  DeliveredCount: number;
}

export interface PRCampaignDetail extends PRCampaignSummary {
  Items: PRCampaignItem[];
  Events: PRCampaignEventMapping[];
}

export interface PRTransactionItem {
  PRID: number;
  CampID: number;
  CampName?: string | null;
  PersonID: number;
  RecipientName?: string | null;
  PersonTitle?: string | null;
  PersonDepartment?: string | null;
  PersonPRClassID?: number | null;
  PRClassName?: string | null;
  PRTypeID?: number | null;
  PRTypeName?: string | null;
  CampReviewStatusID?: number | null;
  ReviewStatusName?: string | null;
  DeliveryTypeID?: number | null;
  DeliveryTypeName?: string | null;
  DeliveryStatusID?: number | null;
  DeliveryStatusName?: string | null;
  PROwnerEmpID?: number | null;
  OwnerName?: string | null;
  OwnerDepartment?: string | null;
  GiftOrderedDt?: string | null;
  IsReattempt: boolean;
  IsActive: boolean;
}

export interface PRTransactionPageResponse {
  total: number;
  limit: number;
  offset: number;
  items: PRTransactionItem[];
}

export interface PRTransactionLogItem {
  TransactionID: number;
  CampID?: number | null;
  CampName?: string | null;
  PRID?: number | null;
  TransactionStatusID?: number | null;
  StatusName?: string | null;
  TransactionDesc?: string | null;
  ModuleName?: string | null;
  TransactionMessage?: string | null;
  EntUser?: string | null;
  EntDt?: string | null;
  CorrelationId?: string | null;
  Severity?: number | null;
}

export interface PRTransactionLogPageResponse {
  total: number;
  limit: number;
  offset: number;
  items: PRTransactionLogItem[];
}

export interface PRTransactionsQueryParams {
  camp_id?: number;
  review_status_id?: number;
  delivery_status_id?: number;
  search?: string;
  limit?: number;
  offset?: number;
}

export interface PRAuditLogsQueryParams {
  camp_id?: number;
  limit?: number;
  offset?: number;
}
