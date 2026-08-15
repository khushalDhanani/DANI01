import logging
from typing import Any

from app.db.mssql import execute_readonly_query
from app.schemas.campaign import (
    PRCampaignDetail,
    PRCampaignEventMapping,
    PRCampaignItem,
    PRCampaignSummary,
    PRTransactionItem,
    PRTransactionLogItem,
    PRTransactionLogPageResponse,
    PRTransactionPageResponse,
)

logger = logging.getLogger(__name__)


class CampaignService:
    """Read-only service for PR Campaign analytics, recipient directory, and audit logs."""

    @staticmethod
    def get_campaign_summaries() -> list[PRCampaignSummary]:
        """Returns overview summaries of all PR Campaigns."""
        query = """
        SELECT
            c.CampID,
            c.CampName,
            c.CampStartDate,
            c.CampReviewCutOfDate,
            c.CampDelReminderDate,
            c.TransCutOffDate,
            c.CampCloseDate,
            c.CampStatusID,
            s.StatusDesc AS CampStatus,
            c.CampIsActive,
            c.EntUser AS CreatedBy,
            c.EntDt AS CreatedAt,
            COUNT(t.PRID) AS TotalTransactions,
            COUNT(CASE WHEN t.CampReviewStatusID = 550 THEN 1 END) AS ApprovedCount,
            COUNT(CASE WHEN t.CampReviewStatusID = 548 THEN 1 END) AS PendingReviewCount,
            COUNT(CASE WHEN t.CampReviewStatusID = 551 THEN 1 END) AS RejectedCount,
            COUNT(CASE WHEN t.DeliveryStatusID = 555 THEN 1 END) AS DeliveredCount
        FROM dbo.PRCampaignMst c
        LEFT JOIN dbo.TransactionStatusMst s ON c.CampStatusID = s.StatusID
        LEFT JOIN dbo.PRTransactionDetails t ON c.CampID = t.CampID
        GROUP BY
            c.CampID, c.CampName, c.CampStartDate, c.CampReviewCutOfDate,
            c.CampDelReminderDate, c.TransCutOffDate, c.CampCloseDate,
            c.CampStatusID, s.StatusDesc, c.CampIsActive, c.EntUser, c.EntDt
        ORDER BY c.CampID DESC;
        """
        rows = execute_readonly_query(query)
        result = []
        for r in rows:
            result.append(
                PRCampaignSummary(
                    CampID=r["CampID"],
                    CampName=r["CampName"] or f"Campaign #{r['CampID']}",
                    CampStartDate=r["CampStartDate"],
                    CampReviewCutOfDate=r["CampReviewCutOfDate"],
                    CampDelReminderDate=r["CampDelReminderDate"],
                    TransCutOffDate=r["TransCutOffDate"],
                    CampCloseDate=r["CampCloseDate"],
                    CampStatusID=r["CampStatusID"],
                    CampStatus=r["CampStatus"],
                    CampIsActive=bool(r["CampIsActive"]) if r["CampIsActive"] is not None else True,
                    CreatedBy=r["CreatedBy"],
                    CreatedAt=r["CreatedAt"],
                    TotalTransactions=r["TotalTransactions"] or 0,
                    ApprovedCount=r["ApprovedCount"] or 0,
                    PendingReviewCount=r["PendingReviewCount"] or 0,
                    RejectedCount=r["RejectedCount"] or 0,
                    DeliveredCount=r["DeliveredCount"] or 0,
                )
            )
        return result

    @staticmethod
    def get_campaign_detail(camp_id: int) -> PRCampaignDetail | None:
        """Returns campaign detailed information including configured items and event mappings."""
        summaries = CampaignService.get_campaign_summaries()
        target = next((s for s in summaries if s.CampID == camp_id), None)
        if not target:
            return None

        # Fetch Items per PR Grade
        item_query = """
        SELECT
            d.CampDetID,
            d.CampID,
            d.PRClassID,
            cls.PRClassName,
            d.ItemRefID,
            COALESCE(m.RowMaterialName, 'Item #' + CAST(d.ItemRefID AS VARCHAR)) AS ItemName,
            d.AdHocLimit
        FROM dbo.PRCampaignDet d
        LEFT JOIN dbo.PRClassMst cls ON d.PRClassID = cls.PRClassID
        OUTER APPLY (
            SELECT TOP 1 RowMaterialName
            FROM dbo.CntRowMaterialMst
            WHERE ItemRefID = d.ItemRefID OR CntRowMaterialId = d.ItemRefID
            ORDER BY CntRowMaterialId
        ) m
        WHERE d.CampID = :camp_id
        ORDER BY cls.PRClassID;
        """
        item_rows = execute_readonly_query(item_query, {"camp_id": camp_id})
        items = [
            PRCampaignItem(
                CampDetID=r["CampDetID"],
                CampID=r["CampID"],
                PRClassID=r["PRClassID"],
                PRClassName=r["PRClassName"],
                ItemRefID=r["ItemRefID"],
                ItemName=r["ItemName"],
                AdHocLimit=r["AdHocLimit"],
            )
            for r in item_rows
        ]

        # Fetch Event Mappings
        event_query = """
        SELECT
            m.ID,
            m.CampID,
            m.LocID,
            m.DLEventID,
            e.EventSubject,
            e.EventFromDate,
            e.EventToDate
        FROM dbo.PRCampaignEventMap m
        LEFT JOIN dbo.DLEvent e ON m.DLEventID = e.DLEventID
        WHERE m.CampID = :camp_id;
        """
        event_rows = execute_readonly_query(event_query, {"camp_id": camp_id})
        events = [
            PRCampaignEventMapping(
                ID=r["ID"],
                CampID=r["CampID"],
                LocID=r["LocID"],
                DLEventID=r["DLEventID"],
                EventSubject=r["EventSubject"],
                EventFromDate=r["EventFromDate"],
                EventToDate=r["EventToDate"],
            )
            for r in event_rows
        ]

        return PRCampaignDetail(
            **target.model_dump(),
            Items=items,
            Events=events,
        )

    @staticmethod
    def get_pr_transactions(
        camp_id: int | None = None,
        review_status_id: int | None = None,
        delivery_status_id: int | None = None,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> PRTransactionPageResponse:
        """Returns paginated PR Transaction recipient directory."""
        where_clauses: list[str] = []
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if camp_id is not None:
            where_clauses.append("t.CampID = :camp_id")
            params["camp_id"] = camp_id

        if review_status_id is not None:
            where_clauses.append("t.CampReviewStatusID = :review_status_id")
            params["review_status_id"] = review_status_id

        if delivery_status_id is not None:
            where_clauses.append("t.DeliveryStatusID = :delivery_status_id")
            params["delivery_status_id"] = delivery_status_id

        if search and search.strip():
            clean_search = search.strip()
            params["search_pattern"] = f"%{clean_search}%"
            where_clauses.append(
                "(p.PersonFirstName LIKE :search_pattern OR "
                "p.PersonLastName LIKE :search_pattern OR "
                "o.PersonFirstName LIKE :search_pattern OR "
                "o.PersonLastName LIKE :search_pattern OR "
                "c.CampName LIKE :search_pattern)"
            )

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        count_sql = f"""
        SELECT COUNT_BIG(1) AS total
        FROM dbo.PRTransactionDetails t
        LEFT JOIN dbo.PRCampaignMst c ON t.CampID = c.CampID
        LEFT JOIN dbo.DLPersonMst p ON t.PersonID = p.PersonID
        LEFT JOIN dbo.DLPersonMst o ON t.PROwnerEmpID = o.EmpID
        {where_sql};
        """
        total_res = execute_readonly_query(count_sql, params)
        total = total_res[0]["total"] if total_res else 0

        items_sql = f"""
        SELECT
            t.PRID,
            t.CampID,
            c.CampName,
            t.PersonID,
            RTRIM(ISNULL(p.PersonFirstName, '') + ' ' + ISNULL(p.PersonLastName, '')) AS RecipientName,
            p.PersonTitle,
            p.PersonDepartment,
            t.PersonPRClassID,
            cls.PRClassName,
            t.PRTypeID,
            type_st.StatusDesc AS PRTypeName,
            t.CampReviewStatusID,
            rev_st.StatusDesc AS ReviewStatusName,
            t.DeliveryTypeID,
            del_type.StatusDesc AS DeliveryTypeName,
            t.DeliveryStatusID,
            del_st.StatusDesc AS DeliveryStatusName,
            t.PROwnerEmpID,
            RTRIM(ISNULL(o.PersonFirstName, '') + ' ' + ISNULL(o.PersonLastName, '')) AS OwnerName,
            o.PersonDepartment AS OwnerDepartment,
            t.GiftOrderedDt,
            t.IsReattempt,
            t.IsActive
        FROM dbo.PRTransactionDetails t
        LEFT JOIN dbo.PRCampaignMst c ON t.CampID = c.CampID
        LEFT JOIN dbo.DLPersonMst p ON t.PersonID = p.PersonID
        LEFT JOIN dbo.PRClassMst cls ON t.PersonPRClassID = cls.PRClassID
        LEFT JOIN dbo.TransactionStatusMst type_st ON t.PRTypeID = type_st.StatusID
        LEFT JOIN dbo.TransactionStatusMst rev_st ON t.CampReviewStatusID = rev_st.StatusID
        LEFT JOIN dbo.TransactionStatusMst del_type ON t.DeliveryTypeID = del_type.StatusID
        LEFT JOIN dbo.TransactionStatusMst del_st ON t.DeliveryStatusID = del_st.StatusID
        LEFT JOIN dbo.DLPersonMst o ON t.PROwnerEmpID = o.EmpID
        {where_sql}
        ORDER BY t.PRID DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        rows = execute_readonly_query(items_sql, params)
        items = []
        for r in rows:
            rec_name = r["RecipientName"].strip() if r["RecipientName"] else None
            owner_name = r["OwnerName"].strip() if r["OwnerName"] else None
            items.append(
                PRTransactionItem(
                    PRID=r["PRID"],
                    CampID=r["CampID"],
                    CampName=r["CampName"],
                    PersonID=r["PersonID"],
                    RecipientName=rec_name if rec_name else f"Person #{r['PersonID']}",
                    PersonTitle=r["PersonTitle"],
                    PersonDepartment=r["PersonDepartment"],
                    PersonPRClassID=r["PersonPRClassID"],
                    PRClassName=r["PRClassName"],
                    PRTypeID=r["PRTypeID"],
                    PRTypeName=r["PRTypeName"],
                    CampReviewStatusID=r["CampReviewStatusID"],
                    ReviewStatusName=r["ReviewStatusName"],
                    DeliveryTypeID=r["DeliveryTypeID"],
                    DeliveryTypeName=r["DeliveryTypeName"],
                    DeliveryStatusID=r["DeliveryStatusID"],
                    DeliveryStatusName=r["DeliveryStatusName"],
                    PROwnerEmpID=r["PROwnerEmpID"],
                    OwnerName=owner_name if owner_name else None,
                    OwnerDepartment=r["OwnerDepartment"],
                    GiftOrderedDt=r["GiftOrderedDt"],
                    IsReattempt=bool(r["IsReattempt"]) if r["IsReattempt"] is not None else False,
                    IsActive=bool(r["IsActive"]) if r["IsActive"] is not None else True,
                )
            )

        return PRTransactionPageResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    @staticmethod
    def get_pr_audit_logs(
        camp_id: int | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> PRTransactionLogPageResponse:
        """Returns audit trail history logs for review and status events."""
        where_clauses: list[str] = []
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if camp_id is not None:
            where_clauses.append("l.CampID = :camp_id")
            params["camp_id"] = camp_id

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        count_sql = f"SELECT COUNT_BIG(1) AS total FROM dbo.PRTransactionLog l {where_sql};"
        total_res = execute_readonly_query(count_sql, params)
        total = total_res[0]["total"] if total_res else 0

        items_sql = f"""
        SELECT
            l.TransactionID,
            l.CampID,
            c.CampName,
            l.PRID,
            l.TransactionStatusID,
            st.StatusDesc AS StatusName,
            l.TransactionDesc,
            l.ModuleName,
            l.TransactionMessage,
            l.EntUser,
            l.EntDt,
            CAST(l.CorrelationId AS VARCHAR(36)) AS CorrelationIdStr,
            l.Severity
        FROM dbo.PRTransactionLog l
        LEFT JOIN dbo.PRCampaignMst c ON l.CampID = c.CampID
        LEFT JOIN dbo.TransactionStatusMst st ON l.TransactionStatusID = st.StatusID
        {where_sql}
        ORDER BY l.TransactionID DESC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        rows = execute_readonly_query(items_sql, params)
        items = [
            PRTransactionLogItem(
                TransactionID=r["TransactionID"],
                CampID=r["CampID"],
                CampName=r["CampName"],
                PRID=r["PRID"],
                TransactionStatusID=r["TransactionStatusID"],
                StatusName=r["StatusName"],
                TransactionDesc=r["TransactionDesc"],
                ModuleName=r["ModuleName"],
                TransactionMessage=r["TransactionMessage"],
                EntUser=r["EntUser"],
                EntDt=r["EntDt"],
                CorrelationId=r["CorrelationIdStr"],
                Severity=r["Severity"],
            )
            for r in rows
        ]

        return PRTransactionLogPageResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )
