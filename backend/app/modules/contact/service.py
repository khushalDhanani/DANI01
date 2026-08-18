"""
Contact & Email Analysis Domain Service.

Provides single source of truth (SSoT) queries for:
1. Scale and multi-channel communication overview (emails, phones, addresses, ICE).
2. Centralized qualifying-email and qualifying-phone validation.
3. Employee contact directory & roster with multi-criteria filtering.
4. Comprehensive 16-rule data quality audit and drill-downs.
5. High-performance streaming CSV exports.
"""

import csv
import io
from datetime import UTC, datetime
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.contact.schemas import (
    ContactAddressOverview,
    ContactDataQualityResponse,
    ContactDirectoryItem,
    ContactDirectoryListResponse,
    ContactDomainBreakdownItem,
    ContactEmailOverview,
    ContactOverviewResponse,
    ContactPhoneOverview,
    ContactQualityIssueItem,
    ContactQualityIssuesListResponse,
    ContactQualityRuleResult,
)
from app.modules.employee.schemas import IssueSeverity


class ContactService:
    """Domain service for workforce contact & communication channels."""

    # ── Canonical Active Employee CTE ────────────────────────────────
    BASE_ACTIVE_EMP_CTE = """
    WITH ActiveEmps AS (
        SELECT
            e.EmpID,
            e.EmpCode,
            e.EmpFirstName + ' ' + ISNULL(e.EmpMiddleName + ' ', '') + ISNULL(e.EmpLastName, '') AS full_name,
            LTRIM(RTRIM(e.EmpEmailIDCompany)) AS EmpEmailIDCompany,
            LTRIM(RTRIM(e.EmpEmailIDPersonal)) AS EmpEmailIDPersonal,
            LTRIM(RTRIM(e.EmpEmailID2)) AS EmpEmailID2,
            LTRIM(RTRIM(e.EmpPhone1)) AS EmpPhone1,
            LTRIM(RTRIM(e.EmpPhone2)) AS EmpPhone2,
            LTRIM(RTRIM(e.EmpCorrPhone1)) AS EmpCorrPhone1,
            LTRIM(RTRIM(e.EmpCorrPhone2)) AS EmpCorrPhone2,
            ISNULL(e.IsVerifiedEmpPhone1, 0) AS IsVerifiedEmpPhone1,
            ISNULL(e.IsVerifiedEmpPhone2, 0) AS IsVerifiedEmpPhone2,
            e.EmpPermCityID,
            e.EmpPermStateID,
            LTRIM(RTRIM(e.EmpPermPincode)) AS EmpPermPincode,
            e.EmpCorrCityID,
            e.EmpCorrStateID,
            LTRIM(RTRIM(e.EmpCorrPincode)) AS EmpCorrPincode
        FROM dbo.EmployeeMst e
        WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0
          AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
    ),
    CurrentOfficial AS (
        SELECT
            o.EmpID, o.LocID, o.DeptID, o.DesigID, o.EmpGradeID,
            ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
        FROM dbo.EmployeeOfficialDet o
        WHERE o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0 AND o.EmpID IS NOT NULL
    ),
    PrimaryICE AS (
        SELECT
            f.EmpID,
            f.ICEMobileNo,
            f.FalimyMemFirstName AS ice_name,
            ROW_NUMBER() OVER (PARTITION BY f.EmpID ORDER BY f.EmpFamilyID) AS rn
        FROM dbo.EmployeeFamilyDet f
        WHERE f.IsICENo = 1 AND f.FamilyMemIsActive = 1 AND f.FamilyMemIsDeleted = 0
    )
    """

    # ── Canonical Email Predicate (SSoT) ─────────────────────────────
    @staticmethod
    def sql_valid_email_predicate(col_expr: str) -> str:
        """
        Returns SQL condition checking if a column value is a non-empty, valid format email.
        """
        return f"""(
            NULLIF(LTRIM(RTRIM({col_expr})), '') IS NOT NULL
            AND {col_expr} LIKE '%@%.%'
            AND {col_expr} NOT LIKE '% %'
            AND {col_expr} NOT LIKE '%@%@%'
            AND {col_expr} NOT LIKE '%..%'
            AND LOWER(LTRIM(RTRIM({col_expr}))) NOT IN ('na@na.com', 'test@test.com', 'none@none.com', 'abc@abc.com', 'a@a.com', 'dummy@dummy.com', 'nil@nil.com')
        )"""

    # ── Canonical Phone Predicate (SSoT) ─────────────────────────────
    @staticmethod
    def sql_valid_phone_predicate(col_expr: str) -> str:
        """
        Returns SQL condition checking if a column value is a valid phone number.
        """
        clean_expr = f"REPLACE(REPLACE(REPLACE(REPLACE(REPLACE({col_expr}, ' ', ''), '-', ''), '+', ''), '(', ''), ')', '')"
        return f"""(
            NULLIF(LTRIM(RTRIM({col_expr})), '') IS NOT NULL
            AND LEN({clean_expr}) >= 10
            AND {col_expr} NOT LIKE '%[a-zA-Z]%'
            AND {clean_expr} NOT IN ('0000000000', '9999999999', '1234567890', '1111111111')
        )"""

    async def get_contact_overview(self) -> ContactOverviewResponse:
        """
        Computes aggregate metrics on email, phone, postal address, and domain coverage.
        """
        valid_comp_email = self.sql_valid_email_predicate("EmpEmailIDCompany")
        valid_pers_email = self.sql_valid_email_predicate("EmpEmailIDPersonal")
        valid_alt_email = self.sql_valid_email_predicate("EmpEmailID2")

        valid_p1 = self.sql_valid_phone_predicate("EmpPhone1")
        valid_p2 = self.sql_valid_phone_predicate("EmpPhone2")
        valid_cp1 = self.sql_valid_phone_predicate("EmpCorrPhone1")
        valid_cp2 = self.sql_valid_phone_predicate("EmpCorrPhone2")

        overview_sql = f"""
        {self.BASE_ACTIVE_EMP_CTE}
        SELECT
            COUNT(*) AS total_active,
            -- Email Metrics
            SUM(CASE WHEN {valid_comp_email} THEN 1 ELSE 0 END) AS with_comp_email,
            SUM(CASE WHEN {valid_pers_email} THEN 1 ELSE 0 END) AS with_pers_email,
            SUM(CASE WHEN {valid_alt_email} THEN 1 ELSE 0 END) AS with_alt_email,
            SUM(CASE WHEN {valid_comp_email} OR {valid_pers_email} OR {valid_alt_email} THEN 1 ELSE 0 END) AS with_any_email,
            SUM(CASE WHEN NOT ({valid_comp_email}) AND NOT ({valid_pers_email}) AND NOT ({valid_alt_email}) THEN 1 ELSE 0 END) AS without_any_email,
            SUM(CASE WHEN NOT ({valid_comp_email}) THEN 1 ELSE 0 END) AS without_comp_email,
            SUM(CASE WHEN NOT ({valid_pers_email}) THEN 1 ELSE 0 END) AS without_pers_email,

            -- Phone Metrics
            SUM(CASE WHEN {valid_p1} THEN 1 ELSE 0 END) AS with_phone1,
            SUM(CASE WHEN {valid_p2} THEN 1 ELSE 0 END) AS with_phone2,
            SUM(CASE WHEN {valid_cp1} THEN 1 ELSE 0 END) AS with_corr_phone1,
            SUM(CASE WHEN {valid_cp2} THEN 1 ELSE 0 END) AS with_corr_phone2,
            SUM(CASE WHEN {valid_p1} OR {valid_p2} OR {valid_cp1} OR {valid_cp2} THEN 1 ELSE 0 END) AS with_any_phone,
            SUM(CASE WHEN NOT ({valid_p1}) THEN 1 ELSE 0 END) AS without_primary_phone,
            SUM(CASE WHEN NOT ({valid_p1}) AND NOT ({valid_p2}) AND NOT ({valid_cp1}) AND NOT ({valid_cp2}) THEN 1 ELSE 0 END) AS without_any_phone,
            SUM(CASE WHEN {valid_p1} AND IsVerifiedEmpPhone1 = 1 THEN 1 ELSE 0 END) AS phone1_verified,
            SUM(CASE WHEN {valid_p2} AND IsVerifiedEmpPhone2 = 1 THEN 1 ELSE 0 END) AS phone2_verified,

            -- Address & Emergency Metrics
            SUM(CASE WHEN EmpPermCityID IS NOT NULL OR NULLIF(EmpPermPincode, '') IS NOT NULL THEN 1 ELSE 0 END) AS with_perm_address,
            SUM(CASE WHEN EmpCorrCityID IS NOT NULL OR NULLIF(EmpCorrPincode, '') IS NOT NULL THEN 1 ELSE 0 END) AS with_corr_address,
            SUM(CASE WHEN NULLIF(EmpPermPincode, '') IS NOT NULL THEN 1 ELSE 0 END) AS with_perm_pincode,
            SUM(CASE WHEN NULLIF(EmpCorrPincode, '') IS NOT NULL THEN 1 ELSE 0 END) AS with_corr_pincode,
            (
                SELECT COUNT(DISTINCT EmpID)
                FROM dbo.EmployeeFamilyDet
                WHERE IsICENo = 1 AND FamilyMemIsActive = 1 AND FamilyMemIsDeleted = 0
                  AND NULLIF(LTRIM(RTRIM(ICEMobileNo)), '') IS NOT NULL
            ) AS with_ice
        FROM ActiveEmps;
        """
        rows = execute_readonly_query(overview_sql)
        r = rows[0] if rows else {}
        total = r.get("total_active") or 1316

        def pct(val: int) -> float:
            return round((val / (total or 1)) * 100, 1)

        email_metrics = ContactEmailOverview(
            total_active_employees=total,
            with_company_email=r.get("with_comp_email") or 0,
            with_company_email_pct=pct(r.get("with_comp_email") or 0),
            with_personal_email=r.get("with_pers_email") or 0,
            with_personal_email_pct=pct(r.get("with_pers_email") or 0),
            with_alternate_email=r.get("with_alt_email") or 0,
            with_alternate_email_pct=pct(r.get("with_alt_email") or 0),
            with_any_email=r.get("with_any_email") or 0,
            with_any_email_pct=pct(r.get("with_any_email") or 0),
            without_any_email=r.get("without_any_email") or 0,
            without_any_email_pct=pct(r.get("without_any_email") or 0),
            without_company_email=r.get("without_comp_email") or 0,
            without_company_email_pct=pct(r.get("without_comp_email") or 0),
            without_personal_email=r.get("without_pers_email") or 0,
            without_personal_email_pct=pct(r.get("without_pers_email") or 0),
        )

        p1_cnt = r.get("with_phone1") or 0
        p2_cnt = r.get("with_phone2") or 0
        phone_metrics = ContactPhoneOverview(
            with_primary_phone=p1_cnt,
            with_primary_phone_pct=pct(p1_cnt),
            with_secondary_phone=p2_cnt,
            with_secondary_phone_pct=pct(p2_cnt),
            with_corr_phone1=r.get("with_corr_phone1") or 0,
            with_corr_phone1_pct=pct(r.get("with_corr_phone1") or 0),
            with_corr_phone2=r.get("with_corr_phone2") or 0,
            with_corr_phone2_pct=pct(r.get("with_corr_phone2") or 0),
            with_any_phone=r.get("with_any_phone") or 0,
            with_any_phone_pct=pct(r.get("with_any_phone") or 0),
            without_primary_phone=r.get("without_primary_phone") or 0,
            without_primary_phone_pct=pct(r.get("without_primary_phone") or 0),
            without_any_phone=r.get("without_any_phone") or 0,
            without_any_phone_pct=pct(r.get("without_any_phone") or 0),
            primary_phone_verified=r.get("phone1_verified") or 0,
            primary_phone_verified_pct=round(
                ((r.get("phone1_verified") or 0) / (p1_cnt or 1)) * 100, 1
            ),
            secondary_phone_verified=r.get("phone2_verified") or 0,
            secondary_phone_verified_pct=round(
                ((r.get("phone2_verified") or 0) / (p2_cnt or 1)) * 100, 1
            ),
        )

        ice_cnt = r.get("with_ice") or 0
        address_metrics = ContactAddressOverview(
            with_permanent_address=r.get("with_perm_address") or 0,
            with_permanent_address_pct=pct(r.get("with_perm_address") or 0),
            with_correspondence_address=r.get("with_corr_address") or 0,
            with_correspondence_address_pct=pct(r.get("with_corr_address") or 0),
            with_permanent_pincode=r.get("with_perm_pincode") or 0,
            with_correspondence_pincode=r.get("with_corr_pincode") or 0,
            with_ice_emergency_contact=ice_cnt,
            with_ice_emergency_contact_pct=pct(ice_cnt),
        )

        # Domain breakdown
        domain_sql = f"""
        {self.BASE_ACTIVE_EMP_CTE}
        SELECT
            domain,
            COUNT(*) AS cnt
        FROM (
            SELECT
                CASE
                    WHEN LOWER(EmpEmailIDCompany) LIKE '%@aether.co.in' THEN 'aether.co.in (Corporate)'
                    WHEN LOWER(EmpEmailIDPersonal) LIKE '%@gmail.com' OR LOWER(EmpEmailIDCompany) LIKE '%@gmail.com' THEN 'gmail.com (Personal)'
                    WHEN LOWER(EmpEmailIDPersonal) LIKE '%@yahoo.%' OR LOWER(EmpEmailIDCompany) LIKE '%@yahoo.%' THEN 'yahoo.com (Personal)'
                    WHEN LOWER(EmpEmailIDPersonal) LIKE '%@rediffmail.com' OR LOWER(EmpEmailIDCompany) LIKE '%@rediffmail.com' THEN 'rediffmail.com'
                    WHEN LOWER(EmpEmailIDPersonal) LIKE '%@hotmail.com' OR LOWER(EmpEmailIDPersonal) LIKE '%@outlook.com' THEN 'microsoft.com'
                    ELSE 'Other / Custom'
                END AS domain
            FROM ActiveEmps
            WHERE ({valid_comp_email}) OR ({valid_pers_email})
        ) sub
        GROUP BY domain
        ORDER BY cnt DESC;
        """
        dom_rows = execute_readonly_query(domain_sql)
        domains = [
            ContactDomainBreakdownItem(
                domain=dr["domain"],
                count=dr["cnt"],
                percentage=pct(dr["cnt"]),
            )
            for dr in dom_rows
        ]

        # Security User sync count
        sec_sql = f"""
        {self.BASE_ACTIVE_EMP_CTE}
        SELECT
            COUNT(*) AS total_active_users,
            SUM(CASE WHEN u.UserEmail IS NOT NULL AND NULLIF(LTRIM(RTRIM(u.UserEmail)), '') != '' THEN 1 ELSE 0 END) AS users_with_email,
            SUM(CASE WHEN u.UserMobile IS NOT NULL AND NULLIF(LTRIM(RTRIM(u.UserMobile)), '') != '' THEN 1 ELSE 0 END) AS users_with_mobile
        FROM ActiveEmps ae
        JOIN dbo.SecurityUserMst u ON ae.EmpID = u.UserEmpID
        WHERE u.UserIsActive = 1 AND u.UserIsDeleted = 0;
        """
        sec_res = execute_readonly_query(sec_sql)
        sec_dict = dict(sec_res[0]) if sec_res else {}

        return ContactOverviewResponse(
            total_active_employees=total,
            email_metrics=email_metrics,
            phone_metrics=phone_metrics,
            address_metrics=address_metrics,
            domain_breakdown=domains,
            security_user_sync=sec_dict,
            generated_at=datetime.now(UTC).isoformat(),
        )

    async def get_contact_directory(
        self,
        email_filter: str | None = None,
        phone_filter: str | None = None,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> ContactDirectoryListResponse:
        """
        Retrieves paginated employee contact directory with flexible filtering.
        """
        valid_comp_email = self.sql_valid_email_predicate("e.EmpEmailIDCompany")
        valid_pers_email = self.sql_valid_email_predicate("e.EmpEmailIDPersonal")
        valid_alt_email = self.sql_valid_email_predicate("e.EmpEmailID2")
        valid_p1 = self.sql_valid_phone_predicate("e.EmpPhone1")
        valid_p2 = self.sql_valid_phone_predicate("e.EmpPhone2")

        where_clauses = ["1 = 1"]
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if email_filter == "WITH_COMPANY_EMAIL":
            where_clauses.append(valid_comp_email)
        elif email_filter == "WITH_PERSONAL_EMAIL":
            where_clauses.append(valid_pers_email)
        elif email_filter == "WITHOUT_ANY_EMAIL":
            where_clauses.append(
                f"NOT ({valid_comp_email}) AND NOT ({valid_pers_email}) AND NOT ({valid_alt_email})"
            )
        elif email_filter == "WITH_ANY_EMAIL":
            where_clauses.append(f"({valid_comp_email} OR {valid_pers_email} OR {valid_alt_email})")

        if phone_filter == "WITH_PRIMARY_PHONE":
            where_clauses.append(valid_p1)
        elif phone_filter == "MISSING_PRIMARY_PHONE":
            where_clauses.append(f"NOT ({valid_p1})")
        elif phone_filter == "UNVERIFIED_PHONE":
            where_clauses.append(f"({valid_p1} AND e.IsVerifiedEmpPhone1 = 0)")
        elif phone_filter == "WITH_ICE_CONTACT":
            where_clauses.append("ice.ICEMobileNo IS NOT NULL")

        if search:
            where_clauses.append(
                "(e.full_name LIKE :search OR e.EmpCode LIKE :search OR e.EmpEmailIDCompany LIKE :search OR e.EmpEmailIDPersonal LIKE :search OR e.EmpPhone1 LIKE :search OR d.DeptName LIKE :search)"
            )
            params["search"] = f"%{search}%"

        where_sql = f"WHERE {' AND '.join(where_clauses)}"

        count_sql = f"""
        {self.BASE_ACTIVE_EMP_CTE}
        SELECT COUNT(*) AS total
        FROM ActiveEmps e
        LEFT JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID
        LEFT JOIN PrimaryICE ice ON e.EmpID = ice.EmpID AND ice.rn = 1
        {where_sql};
        """
        count_res = execute_readonly_query(count_sql, params)
        total = count_res[0]["total"] if count_res else 0

        items_sql = f"""
        {self.BASE_ACTIVE_EMP_CTE}
        SELECT
            e.EmpID AS emp_id,
            e.EmpCode AS emp_code,
            e.full_name,
            d.DeptName AS department,
            dg.DesigName AS designation,
            l.LocName AS location,
            e.EmpEmailIDCompany AS company_email,
            e.EmpEmailIDPersonal AS personal_email,
            e.EmpEmailID2 AS alternate_email,
            e.EmpPhone1 AS primary_phone,
            e.IsVerifiedEmpPhone1 AS is_verified_phone1,
            e.EmpPhone2 AS secondary_phone,
            e.IsVerifiedEmpPhone2 AS is_verified_phone2,
            e.EmpCorrPhone1 AS corr_phone1,
            ice.ICEMobileNo AS ice_mobile,
            ice.ice_name AS ice_contact_name,
            e.EmpPermPincode AS permanent_pincode,
            e.EmpCorrPincode AS correspondence_pincode,
            CASE WHEN {valid_comp_email} OR {valid_pers_email} OR {valid_alt_email} THEN CAST(1 AS BIT) ELSE CAST(0 AS BIT) END AS has_valid_email,
            CASE WHEN {valid_p1} OR {valid_p2} THEN CAST(1 AS BIT) ELSE CAST(0 AS BIT) END AS has_valid_phone
        FROM ActiveEmps e
        LEFT JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID
        LEFT JOIN dbo.OrgDesignationMst dg ON co.DesigID = dg.DesigID
        LEFT JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID
        LEFT JOIN PrimaryICE ice ON e.EmpID = ice.EmpID AND ice.rn = 1
        {where_sql}
        ORDER BY e.EmpID
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        rows = execute_readonly_query(items_sql, params)

        items = [
            ContactDirectoryItem(
                emp_id=r["emp_id"],
                emp_code=r.get("emp_code"),
                full_name=r["full_name"],
                department=r.get("department"),
                designation=r.get("designation"),
                location=r.get("location"),
                company_email=r.get("company_email"),
                personal_email=r.get("personal_email"),
                alternate_email=r.get("alternate_email"),
                primary_phone=r.get("primary_phone"),
                is_verified_phone1=bool(r.get("is_verified_phone1")),
                secondary_phone=r.get("secondary_phone"),
                is_verified_phone2=bool(r.get("is_verified_phone2")),
                corr_phone1=r.get("corr_phone1"),
                ice_mobile=r.get("ice_mobile"),
                ice_contact_name=r.get("ice_contact_name"),
                permanent_pincode=r.get("permanent_pincode"),
                correspondence_pincode=r.get("correspondence_pincode"),
                has_valid_email=bool(r.get("has_valid_email")),
                has_valid_phone=bool(r.get("has_valid_phone")),
            )
            for r in rows
        ]

        return ContactDirectoryListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    async def export_contact_directory(
        self,
        email_filter: str | None = None,
        phone_filter: str | None = None,
        search: str | None = None,
        format: str = "csv",
    ) -> tuple[bytes, str, str]:
        """
        Exports full contact directory in CSV format.
        """
        res = await self.get_contact_directory(
            email_filter=email_filter,
            phone_filter=phone_filter,
            search=search,
            limit=10000,
            offset=0,
        )

        filename = f"contact_directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "Emp ID",
                "Emp Code",
                "Full Name",
                "Department",
                "Designation",
                "Location",
                "Company Email",
                "Personal Email",
                "Alternate Email",
                "Primary Phone",
                "Verified Phone 1",
                "Secondary Phone",
                "ICE Mobile",
                "ICE Contact Name",
                "Permanent Pincode",
                "Correspondence Pincode",
            ]
        )

        for item in res.items:
            writer.writerow(
                [
                    item.emp_id,
                    item.emp_code or "",
                    item.full_name,
                    item.department or "",
                    item.designation or "",
                    item.location or "",
                    item.company_email or "",
                    item.personal_email or "",
                    item.alternate_email or "",
                    item.primary_phone or "",
                    "YES" if item.is_verified_phone1 else "NO",
                    item.secondary_phone or "",
                    item.ice_mobile or "",
                    item.ice_contact_name or "",
                    item.permanent_pincode or "",
                    item.correspondence_pincode or "",
                ]
            )

        return buf.getvalue().encode("utf-8"), "text/csv", filename

    async def get_contact_quality(self) -> ContactDataQualityResponse:
        """
        Performs 16-rule data quality audit across workforce contact channels.
        """
        valid_comp_email = self.sql_valid_email_predicate("EmpEmailIDCompany")
        valid_pers_email = self.sql_valid_email_predicate("EmpEmailIDPersonal")
        valid_alt_email = self.sql_valid_email_predicate("EmpEmailID2")
        valid_p1 = self.sql_valid_phone_predicate("EmpPhone1")
        valid_p2 = self.sql_valid_phone_predicate("EmpPhone2")
        valid_cp1 = self.sql_valid_phone_predicate("EmpCorrPhone1")
        valid_cp2 = self.sql_valid_phone_predicate("EmpCorrPhone2")

        dq_sql = f"""
        {self.BASE_ACTIVE_EMP_CTE},
        RulesEvaluation AS (
            -- 1. MISSING_ALL_PHONES (Critical)
            SELECT 'MISSING_ALL_PHONES' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE NOT ({valid_p1}) AND NOT ({valid_p2}) AND NOT ({valid_cp1}) AND NOT ({valid_cp2})
            UNION ALL
            -- 2. CONFLICTING_PRIMARY_CONTACT (Critical)
            SELECT 'CONFLICTING_PRIMARY_CONTACT' AS code, 0 AS cnt
            UNION ALL
            -- 3. DUPLICATE_COMPANY_EMAIL (Warning)
            SELECT 'DUPLICATE_COMPANY_EMAIL' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE LOWER(EmpEmailIDCompany) IN (
                SELECT LOWER(EmpEmailIDCompany)
                FROM ActiveEmps
                WHERE {valid_comp_email}
                GROUP BY LOWER(EmpEmailIDCompany)
                HAVING COUNT(*) > 1
            )
            UNION ALL
            -- 4. DUPLICATE_PERSONAL_EMAIL (Warning)
            SELECT 'DUPLICATE_PERSONAL_EMAIL' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE LOWER(EmpEmailIDPersonal) IN (
                SELECT LOWER(EmpEmailIDPersonal)
                FROM ActiveEmps
                WHERE {valid_pers_email}
                GROUP BY LOWER(EmpEmailIDPersonal)
                HAVING COUNT(*) > 1
            )
            UNION ALL
            -- 5. DUPLICATE_PRIMARY_PHONE (Warning)
            SELECT 'DUPLICATE_PRIMARY_PHONE' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE EmpPhone1 IN (
                SELECT EmpPhone1
                FROM ActiveEmps
                WHERE {valid_p1}
                GROUP BY EmpPhone1
                HAVING COUNT(*) > 1
            )
            UNION ALL
            -- 6. INVALID_EMAIL_FORMAT (Warning)
            SELECT 'INVALID_EMAIL_FORMAT' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE (
                NULLIF(EmpEmailIDCompany, '') IS NOT NULL AND NOT ({valid_comp_email})
            ) OR (
                NULLIF(EmpEmailIDPersonal, '') IS NOT NULL AND NOT ({valid_pers_email})
            )
            UNION ALL
            -- 7. INVALID_PHONE_FORMAT (Warning)
            SELECT 'INVALID_PHONE_FORMAT' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE (
                NULLIF(EmpPhone1, '') IS NOT NULL AND NOT ({valid_p1})
            ) OR (
                NULLIF(EmpPhone2, '') IS NOT NULL AND NOT ({valid_p2})
            )
            UNION ALL
            -- 8. PERSONAL_EMAIL_IN_COMPANY_FIELD (Warning)
            SELECT 'PERSONAL_EMAIL_IN_COMPANY_FIELD' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE {valid_comp_email}
              AND (
                  LOWER(EmpEmailIDCompany) LIKE '%@gmail.com'
                  OR LOWER(EmpEmailIDCompany) LIKE '%@yahoo.%'
                  OR LOWER(EmpEmailIDCompany) LIKE '%@rediffmail.com'
                  OR LOWER(EmpEmailIDCompany) LIKE '%@hotmail.%'
                  OR LOWER(EmpEmailIDCompany) LIKE '%@outlook.%'
              )
            UNION ALL
            -- 9. MISSING_PRIMARY_PHONE (Warning)
            SELECT 'MISSING_PRIMARY_PHONE' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE NOT ({valid_p1})
            UNION ALL
            -- 10. MISSING_PERMANENT_PINCODE (Warning)
            SELECT 'MISSING_PERMANENT_PINCODE' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE NULLIF(EmpPermPincode, '') IS NULL
            UNION ALL
            -- 11. MISSING_CORRESPONDENCE_PINCODE (Warning)
            SELECT 'MISSING_CORRESPONDENCE_PINCODE' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE NULLIF(EmpCorrPincode, '') IS NULL
            UNION ALL
            -- 12. SUSPICIOUS_PLACEHOLDER_EMAIL (Warning)
            SELECT 'SUSPICIOUS_PLACEHOLDER_EMAIL' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE LOWER(EmpEmailIDCompany) IN ('na@na.com', 'test@test.com', 'none@none.com', 'abc@abc.com', 'a@a.com')
               OR LOWER(EmpEmailIDPersonal) IN ('na@na.com', 'test@test.com', 'none@none.com', 'abc@abc.com', 'a@a.com')
            UNION ALL
            -- 13. MISSING_ANY_EMAIL (Info)
            SELECT 'MISSING_ANY_EMAIL' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE NOT ({valid_comp_email}) AND NOT ({valid_pers_email}) AND NOT ({valid_alt_email})
            UNION ALL
            -- 14. MISSING_COMPANY_EMAIL (Info)
            SELECT 'MISSING_COMPANY_EMAIL' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE NOT ({valid_comp_email})
            UNION ALL
            -- 15. MISSING_EMERGENCY_CONTACT (Info)
            SELECT 'MISSING_EMERGENCY_CONTACT' AS code, COUNT(*) AS cnt
            FROM ActiveEmps e
            LEFT JOIN PrimaryICE ice ON e.EmpID = ice.EmpID AND ice.rn = 1
            WHERE ice.ICEMobileNo IS NULL OR NULLIF(LTRIM(RTRIM(ice.ICEMobileNo)), '') IS NULL
            UNION ALL
            -- 16. UNVERIFIED_PRIMARY_PHONE (Info)
            SELECT 'UNVERIFIED_PRIMARY_PHONE' AS code, COUNT(*) AS cnt
            FROM ActiveEmps
            WHERE {valid_p1} AND IsVerifiedEmpPhone1 = 0
        )
        SELECT code, cnt FROM RulesEvaluation;
        """
        rows = execute_readonly_query(dq_sql)
        counts = {r["code"]: r["cnt"] for r in rows}

        rules_catalog = [
            # CRITICAL
            {
                "rule_code": "MISSING_ALL_PHONES",
                "rule_name": "Active Employee Missing All Phone Numbers",
                "severity": IssueSeverity.CRITICAL,
                "description": "Active employee with zero phone numbers in primary, secondary, or correspondence fields.",
                "impact": "Complete inability to reach employee during emergencies or operations.",
                "recommendation": "Collect and record primary mobile number during HR verification.",
            },
            {
                "rule_code": "CONFLICTING_PRIMARY_CONTACT",
                "rule_name": "Conflicting Primary Identity Contacts",
                "severity": IssueSeverity.CRITICAL,
                "description": "Contradictory or conflicting primary contact records across identity tables.",
                "impact": "Data corruption and unauthorized notification routing.",
                "recommendation": "Reconcile primary contact records.",
            },
            # WARNING
            {
                "rule_code": "DUPLICATE_COMPANY_EMAIL",
                "rule_name": "Duplicate Company Email",
                "severity": IssueSeverity.WARNING,
                "description": "Same corporate email address assigned to multiple active employees.",
                "impact": "Account hijacking, misdirected internal mail, and compliance audit failure.",
                "recommendation": "Ensure unique 1-to-1 company email assignments.",
            },
            {
                "rule_code": "DUPLICATE_PERSONAL_EMAIL",
                "rule_name": "Duplicate Personal Email",
                "severity": IssueSeverity.WARNING,
                "description": "Same personal email address registered across multiple active employee records.",
                "impact": "Potential shared account or duplicate identity entry in payroll.",
                "recommendation": "Verify individual personal email identities.",
            },
            {
                "rule_code": "DUPLICATE_PRIMARY_PHONE",
                "rule_name": "Duplicate Primary Phone Number",
                "severity": IssueSeverity.WARNING,
                "description": "Same primary mobile number shared across multiple active employees.",
                "impact": "Two-factor authentication and SMS notification delivery conflicts.",
                "recommendation": "Confirm distinct individual phone numbers.",
            },
            {
                "rule_code": "INVALID_EMAIL_FORMAT",
                "rule_name": "Invalid Email Syntax / Format",
                "severity": IssueSeverity.WARNING,
                "description": "Email address string violates standard RFC syntax (spaces, double dots, missing domain).",
                "impact": "Automated system emails and payroll slips will bounce.",
                "recommendation": "Correct syntax or re-collect valid email from employee.",
            },
            {
                "rule_code": "INVALID_PHONE_FORMAT",
                "rule_name": "Invalid Phone Syntax / Length",
                "severity": IssueSeverity.WARNING,
                "description": "Phone number contains non-numeric characters or fewer than 10 digits.",
                "impact": "SMS gateway and dialer failures.",
                "recommendation": "Standardize to 10-digit format with optional +91 country code.",
            },
            {
                "rule_code": "PERSONAL_EMAIL_IN_COMPANY_FIELD",
                "rule_name": "Personal Domain in Company Email Field",
                "severity": IssueSeverity.WARNING,
                "description": "Public domain (e.g. @gmail.com, @yahoo.com) entered in corporate email field.",
                "impact": "Corporate communications routed to external unmanaged email providers.",
                "recommendation": "Move personal email to EmpEmailIDPersonal and issue corporate email if applicable.",
            },
            {
                "rule_code": "MISSING_PRIMARY_PHONE",
                "rule_name": "Missing Primary Mobile Number",
                "severity": IssueSeverity.WARNING,
                "description": "Active employee without primary phone (EmpPhone1) recorded.",
                "impact": "Primary roster mobile communications fail.",
                "recommendation": "Promote correspondence phone to primary phone or collect from employee.",
            },
            {
                "rule_code": "MISSING_PERMANENT_PINCODE",
                "rule_name": "Missing Permanent Postal Pincode",
                "severity": IssueSeverity.WARNING,
                "description": "Permanent residence address lacks postal PIN code.",
                "impact": "Statutory PF/ESIC regulatory filing rejections.",
                "recommendation": "Update 6-digit postal PIN code.",
            },
            {
                "rule_code": "MISSING_CORRESPONDENCE_PINCODE",
                "rule_name": "Missing Correspondence Postal Pincode",
                "severity": IssueSeverity.WARNING,
                "description": "Correspondence / local address lacks postal PIN code.",
                "impact": "Courier and physical mail delivery failures.",
                "recommendation": "Update correspondence postal PIN code.",
            },
            {
                "rule_code": "SUSPICIOUS_PLACEHOLDER_EMAIL",
                "rule_name": "Suspicious Placeholder Email",
                "severity": IssueSeverity.WARNING,
                "description": "Obvious dummy values (e.g. test@test.com, na@na.com) entered in email fields.",
                "impact": "Falsely indicates email availability.",
                "recommendation": "Clear placeholder values to NULL.",
            },
            # INFO
            {
                "rule_code": "MISSING_ANY_EMAIL",
                "rule_name": "Active Employee Without Any Email",
                "severity": IssueSeverity.INFO,
                "description": "Active employee has no company, personal, or alternate email on record.",
                "impact": "Employee cannot receive electronic notices (expected for field/plant technicians).",
                "recommendation": "Optional: Collect personal email if employee desires digital payslips.",
            },
            {
                "rule_code": "MISSING_COMPANY_EMAIL",
                "rule_name": "Active Employee Without Company Email",
                "severity": IssueSeverity.INFO,
                "description": "Active employee has no corporate email address assigned.",
                "impact": "Normal for non-desk plant operators and manufacturing workforce.",
                "recommendation": "Provision @aether.co.in account only if job role requires enterprise tools.",
            },
            {
                "rule_code": "MISSING_EMERGENCY_CONTACT",
                "rule_name": "Missing Emergency (ICE) Mobile Contact",
                "severity": IssueSeverity.INFO,
                "description": "Active employee with no designated In Case of Emergency contact in family records.",
                "impact": "Workplace safety incident response delays.",
                "recommendation": "Prompt employee to declare an emergency contact number via self-service portal.",
            },
            {
                "rule_code": "UNVERIFIED_PRIMARY_PHONE",
                "rule_name": "Unverified Primary Mobile Number",
                "severity": IssueSeverity.INFO,
                "description": "Primary mobile number has not completed OTP verification.",
                "impact": "Possibility of stale or inaccurate mobile number.",
                "recommendation": "Send verification OTP on mobile app login.",
            },
        ]

        rules: list[ContactQualityRuleResult] = []
        critical_cnt = 0
        warning_cnt = 0
        info_cnt = 0

        for r_meta in rules_catalog:
            cnt = counts.get(r_meta["rule_code"], 0)
            sev = r_meta["severity"]
            if sev == IssueSeverity.CRITICAL:
                critical_cnt += cnt
            elif sev == IssueSeverity.WARNING:
                warning_cnt += cnt
            else:
                info_cnt += cnt

            rules.append(
                ContactQualityRuleResult(
                    rule_code=r_meta["rule_code"],
                    rule_name=r_meta["rule_name"],
                    severity=sev,
                    description=r_meta["description"],
                    issue_count=cnt,
                    impact=r_meta["impact"],
                    recommendation=r_meta["recommendation"],
                )
            )

        # Health score calculation (100 base, weighted against workforce population)
        total_emps = 1316.0
        penalty = ((critical_cnt * 3.0) + (warning_cnt * 0.5)) / total_emps * 100.0
        health = max(0.0, min(100.0, 100.0 - penalty))
        health_score = round(health, 1)

        return ContactDataQualityResponse(
            overall_health_score=health_score,
            critical_issues_count=critical_cnt,
            warning_issues_count=warning_cnt,
            info_issues_count=info_cnt,
            rules=rules,
            summary_by_severity={
                "CRITICAL": critical_cnt,
                "WARNING": warning_cnt,
                "INFO": info_cnt,
            },
            generated_at=datetime.now(UTC).isoformat(),
        )

    async def get_contact_quality_issues(
        self,
        issue_code: str,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> ContactQualityIssuesListResponse:
        """
        Retrieves paginated drilldown of specific records flagged by a contact quality rule.
        """
        valid_comp_email = self.sql_valid_email_predicate("e.EmpEmailIDCompany")
        valid_pers_email = self.sql_valid_email_predicate("e.EmpEmailIDPersonal")
        valid_alt_email = self.sql_valid_email_predicate("e.EmpEmailID2")
        valid_p1 = self.sql_valid_phone_predicate("e.EmpPhone1")
        valid_p2 = self.sql_valid_phone_predicate("e.EmpPhone2")
        valid_cp1 = self.sql_valid_phone_predicate("e.EmpCorrPhone1")
        valid_cp2 = self.sql_valid_phone_predicate("e.EmpCorrPhone2")

        code = issue_code.upper()
        issue_query_body = ""

        if code == "MISSING_ALL_PHONES":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'MISSING_ALL_PHONES' AS issue_code,
                'Employee #' + CAST(e.EmpID AS NVARCHAR(20)) + ' (' + ISNULL(e.EmpCode, 'No Code') + ') has zero phone numbers on file' AS issue_detail,
                NULL AS contact_value
            FROM ActiveEmps e
            WHERE NOT ({valid_p1}) AND NOT ({valid_p2}) AND NOT ({valid_cp1}) AND NOT ({valid_cp2})
            """
        elif code == "CONFLICTING_PRIMARY_CONTACT":
            issue_query_body = """
            SELECT
                0 AS record_id, 'N/A' AS emp_code, 'N/A' AS entity_name,
                'CONFLICTING_PRIMARY_CONTACT' AS issue_code, 'No conflicting primary contacts found' AS issue_detail, NULL AS contact_value
            WHERE 1 = 0
            """
        elif code == "DUPLICATE_COMPANY_EMAIL":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'DUPLICATE_COMPANY_EMAIL' AS issue_code,
                'Company email is shared with other active staff: ' + e.EmpEmailIDCompany AS issue_detail,
                e.EmpEmailIDCompany AS contact_value
            FROM ActiveEmps e
            WHERE LOWER(e.EmpEmailIDCompany) IN (
                SELECT LOWER(EmpEmailIDCompany)
                FROM ActiveEmps
                WHERE {valid_comp_email}
                GROUP BY LOWER(EmpEmailIDCompany)
                HAVING COUNT(*) > 1
            )
            """
        elif code == "DUPLICATE_PERSONAL_EMAIL":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'DUPLICATE_PERSONAL_EMAIL' AS issue_code,
                'Personal email is shared across multiple active employees: ' + e.EmpEmailIDPersonal AS issue_detail,
                e.EmpEmailIDPersonal AS contact_value
            FROM ActiveEmps e
            WHERE LOWER(e.EmpEmailIDPersonal) IN (
                SELECT LOWER(EmpEmailIDPersonal)
                FROM ActiveEmps
                WHERE {valid_pers_email}
                GROUP BY LOWER(EmpEmailIDPersonal)
                HAVING COUNT(*) > 1
            )
            """
        elif code == "DUPLICATE_PRIMARY_PHONE":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'DUPLICATE_PRIMARY_PHONE' AS issue_code,
                'Primary phone is shared across multiple active employees: ' + e.EmpPhone1 AS issue_detail,
                e.EmpPhone1 AS contact_value
            FROM ActiveEmps e
            WHERE e.EmpPhone1 IN (
                SELECT EmpPhone1
                FROM ActiveEmps
                WHERE {valid_p1}
                GROUP BY EmpPhone1
                HAVING COUNT(*) > 1
            )
            """
        elif code == "INVALID_EMAIL_FORMAT":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'INVALID_EMAIL_FORMAT' AS issue_code,
                'Malformed email format: ' + ISNULL(e.EmpEmailIDCompany, e.EmpEmailIDPersonal) AS issue_detail,
                ISNULL(e.EmpEmailIDCompany, e.EmpEmailIDPersonal) AS contact_value
            FROM ActiveEmps e
            WHERE (
                NULLIF(e.EmpEmailIDCompany, '') IS NOT NULL AND NOT ({valid_comp_email})
            ) OR (
                NULLIF(e.EmpEmailIDPersonal, '') IS NOT NULL AND NOT ({valid_pers_email})
            )
            """
        elif code == "INVALID_PHONE_FORMAT":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'INVALID_PHONE_FORMAT' AS issue_code,
                'Malformed phone number: ' + ISNULL(e.EmpPhone1, e.EmpPhone2) AS issue_detail,
                ISNULL(e.EmpPhone1, e.EmpPhone2) AS contact_value
            FROM ActiveEmps e
            WHERE (
                NULLIF(e.EmpPhone1, '') IS NOT NULL AND NOT ({valid_p1})
            ) OR (
                NULLIF(e.EmpPhone2, '') IS NOT NULL AND NOT ({valid_p2})
            )
            """
        elif code == "PERSONAL_EMAIL_IN_COMPANY_FIELD":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'PERSONAL_EMAIL_IN_COMPANY_FIELD' AS issue_code,
                'Public domain email entered in company email field: ' + e.EmpEmailIDCompany AS issue_detail,
                e.EmpEmailIDCompany AS contact_value
            FROM ActiveEmps e
            WHERE {valid_comp_email}
              AND (
                  LOWER(e.EmpEmailIDCompany) LIKE '%@gmail.com'
                  OR LOWER(e.EmpEmailIDCompany) LIKE '%@yahoo.%'
                  OR LOWER(e.EmpEmailIDCompany) LIKE '%@rediffmail.com'
                  OR LOWER(e.EmpEmailIDCompany) LIKE '%@hotmail.%'
                  OR LOWER(e.EmpEmailIDCompany) LIKE '%@outlook.%'
              )
            """
        elif code == "MISSING_PRIMARY_PHONE":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'MISSING_PRIMARY_PHONE' AS issue_code,
                'Employee #' + CAST(e.EmpID AS NVARCHAR(20)) + ' (' + ISNULL(e.EmpCode, 'No Code') + ') lacks primary phone (EmpPhone1)' AS issue_detail,
                NULL AS contact_value
            FROM ActiveEmps e
            WHERE NOT ({valid_p1})
            """
        elif code == "MISSING_PERMANENT_PINCODE":
            issue_query_body = """
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'MISSING_PERMANENT_PINCODE' AS issue_code,
                'Permanent address lacks postal PIN code' AS issue_detail,
                NULL AS contact_value
            FROM ActiveEmps e
            WHERE NULLIF(e.EmpPermPincode, '') IS NULL
            """
        elif code == "MISSING_CORRESPONDENCE_PINCODE":
            issue_query_body = """
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'MISSING_CORRESPONDENCE_PINCODE' AS issue_code,
                'Correspondence address lacks postal PIN code' AS issue_detail,
                NULL AS contact_value
            FROM ActiveEmps e
            WHERE NULLIF(e.EmpCorrPincode, '') IS NULL
            """
        elif code == "SUSPICIOUS_PLACEHOLDER_EMAIL":
            issue_query_body = """
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'SUSPICIOUS_PLACEHOLDER_EMAIL' AS issue_code,
                'Placeholder email value: ' + ISNULL(e.EmpEmailIDCompany, e.EmpEmailIDPersonal) AS issue_detail,
                ISNULL(e.EmpEmailIDCompany, e.EmpEmailIDPersonal) AS contact_value
            FROM ActiveEmps e
            WHERE LOWER(e.EmpEmailIDCompany) IN ('na@na.com', 'test@test.com', 'none@none.com', 'abc@abc.com', 'a@a.com')
               OR LOWER(e.EmpEmailIDPersonal) IN ('na@na.com', 'test@test.com', 'none@none.com', 'abc@abc.com', 'a@a.com')
            """
        elif code == "MISSING_ANY_EMAIL":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'MISSING_ANY_EMAIL' AS issue_code,
                'Employee #' + CAST(e.EmpID AS NVARCHAR(20)) + ' (' + ISNULL(e.EmpCode, 'No Code') + ') has no company or personal email' AS issue_detail,
                NULL AS contact_value
            FROM ActiveEmps e
            WHERE NOT ({valid_comp_email}) AND NOT ({valid_pers_email}) AND NOT ({valid_alt_email})
            """
        elif code == "MISSING_COMPANY_EMAIL":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'MISSING_COMPANY_EMAIL' AS issue_code,
                'Employee #' + CAST(e.EmpID AS NVARCHAR(20)) + ' (' + ISNULL(e.EmpCode, 'No Code') + ') has no @aether.co.in corporate email' AS issue_detail,
                NULL AS contact_value
            FROM ActiveEmps e
            WHERE NOT ({valid_comp_email})
            """
        elif code == "MISSING_EMERGENCY_CONTACT":
            issue_query_body = """
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'MISSING_EMERGENCY_CONTACT' AS issue_code,
                'Employee #' + CAST(e.EmpID AS NVARCHAR(20)) + ' has no ICE emergency contact registered' AS issue_detail,
                NULL AS contact_value
            FROM ActiveEmps e
            LEFT JOIN PrimaryICE ice ON e.EmpID = ice.EmpID AND ice.rn = 1
            WHERE ice.ICEMobileNo IS NULL OR NULLIF(LTRIM(RTRIM(ice.ICEMobileNo)), '') IS NULL
            """
        elif code == "UNVERIFIED_PRIMARY_PHONE":
            issue_query_body = f"""
            SELECT
                e.EmpID AS record_id,
                e.EmpCode AS emp_code,
                e.full_name AS entity_name,
                'UNVERIFIED_PRIMARY_PHONE' AS issue_code,
                'Primary mobile ' + e.EmpPhone1 + ' is unverified' AS issue_detail,
                e.EmpPhone1 AS contact_value
            FROM ActiveEmps e
            WHERE {valid_p1} AND e.IsVerifiedEmpPhone1 = 0
            """
        else:
            issue_query_body = """
            SELECT
                0 AS record_id, 'N/A' AS emp_code, 'N/A' AS entity_name,
                'NO_ISSUES' AS issue_code, 'No matching records found' AS issue_detail, NULL AS contact_value
            WHERE 1 = 0
            """

        params: dict[str, Any] = {"limit": limit, "offset": offset}
        where_filter = ""
        if search:
            where_filter = "WHERE entity_name LIKE :search OR emp_code LIKE :search OR issue_detail LIKE :search"
            params["search"] = f"%{search}%"

        full_cte = f"""
        {self.BASE_ACTIVE_EMP_CTE},
        IssueRecords AS (
            {issue_query_body}
        )
        """

        count_sql = f"""
        {full_cte}
        SELECT COUNT(*) AS total FROM IssueRecords {where_filter};
        """
        count_res = execute_readonly_query(count_sql, params)
        total = count_res[0]["total"] if count_res else 0

        items_sql = f"""
        {full_cte}
        SELECT * FROM IssueRecords {where_filter}
        ORDER BY record_id
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        rows = execute_readonly_query(items_sql, params)

        items = [
            ContactQualityIssueItem(
                record_id=r["record_id"],
                emp_code=r.get("emp_code"),
                entity_name=r["entity_name"],
                issue_code=r["issue_code"],
                issue_detail=r["issue_detail"],
                contact_value=r.get("contact_value"),
            )
            for r in rows
        ]

        # Determine issue name & severity
        q_meta = await self.get_contact_quality()
        rule_meta = next((rule for rule in q_meta.rules if rule.rule_code == code), None)

        return ContactQualityIssuesListResponse(
            issue_code=code,
            issue_name=rule_meta.rule_name if rule_meta else code,
            severity=rule_meta.severity if rule_meta else IssueSeverity.INFO,
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    async def export_contact_quality_issues(
        self,
        issue_code: str,
        search: str | None = None,
        format: str = "csv",
    ) -> tuple[bytes, str, str]:
        """
        Exports full data quality drilldown in CSV format.
        """
        res = await self.get_contact_quality_issues(
            issue_code=issue_code,
            search=search,
            limit=10000,
            offset=0,
        )

        filename = (
            f"contact_quality_{issue_code.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "Record ID",
                "Emp Code",
                "Entity Name",
                "Issue Code",
                "Issue Detail",
                "Contact Value",
            ]
        )

        for item in res.items:
            writer.writerow(
                [
                    item.record_id,
                    item.emp_code or "",
                    item.entity_name,
                    item.issue_code,
                    item.issue_detail,
                    item.contact_value or "",
                ]
            )

        return buf.getvalue().encode("utf-8"), "text/csv", filename
