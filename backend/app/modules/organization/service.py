import csv
import io
import logging
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.employee.schemas import IssueSeverity
from app.modules.organization.schemas import (
    OrgDataQualityResponse,
    OrgHeadcountItem,
    OrgHierarchyNode,
    OrgHierarchyResponse,
    OrgOverviewResponse,
    OrgQualityIssueRecord,
    OrgQualityIssuesListResponse,
    OrgQualityRuleResult,
    OrgReportingNode,
    OrgReportingTreeResponse,
    OrgScaleCounts,
    OrgUnitListItem,
    OrgUnitListResponse,
    OrgUnitType,
)

logger = logging.getLogger(__name__)


class OrganizationService:
    """
    Centralized domain service for Organization Structure, Entity Catalogs,
    Multi-Tier Hierarchy Aggregations, Leadership Trees, and Data Quality Audits.
    All business rules and queries are centralized here as the Single Source of Truth (SSoT).
    """

    # ══════════════════════════════════════════════════════════════════════════════
    # 1. OVERVIEW & SCALE METRICS
    # ══════════════════════════════════════════════════════════════════════════════

    async def get_org_overview(self) -> OrgOverviewResponse:
        """
        Calculates authoritative scale counts, unit distributions, and headcount allocations.
        """
        scale_sql = """
        SELECT
            (SELECT COUNT(*) FROM dbo.OrgCompanyMst) AS total_companies,
            (SELECT COUNT(*) FROM dbo.OrgCompanyMst WHERE CompIsActive = 1 AND CompIsDeleted = 0) AS active_companies,
            (SELECT COUNT(*) FROM dbo.OrgLocationMst) AS total_locations,
            (SELECT COUNT(*) FROM dbo.OrgLocationMst WHERE LocIsActive = 1 AND LocIsDeleted = 0) AS active_locations,
            (SELECT COUNT(*) FROM dbo.OrgMainDepartmentMst) AS total_main_depts,
            (SELECT COUNT(*) FROM dbo.OrgMainDepartmentMst WHERE IsActive = 1) AS active_main_depts,
            (SELECT COUNT(*) FROM dbo.OrgDepartmentMst) AS total_departments,
            (SELECT COUNT(*) FROM dbo.OrgDepartmentMst WHERE DeptIsActive = 1 AND DeptIsDeleted = 0) AS active_departments,
            (SELECT COUNT(*) FROM dbo.OrgDesignationMst) AS total_designations,
            (SELECT COUNT(*) FROM dbo.OrgDesignationMst WHERE DesigIsActive = 1 AND DesigIsDeleted = 0) AS active_designations,
            (SELECT COUNT(*) FROM dbo.EmployeeGradeMst) AS total_grades,
            (SELECT COUNT(*) FROM dbo.EmployeeGradeMst WHERE EmpGradeIsActive = 1 AND EmpGradeIsDeleted = 0) AS active_grades;
        """
        scale_rows = execute_readonly_query(scale_sql)
        sr = scale_rows[0] if scale_rows else {}

        active_units_sum = (
            (sr.get("active_companies") or 0)
            + (sr.get("active_locations") or 0)
            + (sr.get("active_main_depts") or 0)
            + (sr.get("active_departments") or 0)
            + (sr.get("active_designations") or 0)
            + (sr.get("active_grades") or 0)
        )
        total_units_sum = (
            (sr.get("total_companies") or 0)
            + (sr.get("total_locations") or 0)
            + (sr.get("total_main_depts") or 0)
            + (sr.get("total_departments") or 0)
            + (sr.get("total_designations") or 0)
            + (sr.get("total_grades") or 0)
        )

        scale_counts = OrgScaleCounts(
            total_companies=sr.get("total_companies") or 0,
            active_companies=sr.get("active_companies") or 0,
            total_locations=sr.get("total_locations") or 0,
            active_locations=sr.get("active_locations") or 0,
            total_main_depts=sr.get("total_main_depts") or 0,
            active_main_depts=sr.get("active_main_depts") or 0,
            total_departments=sr.get("total_departments") or 0,
            active_departments=sr.get("active_departments") or 0,
            total_designations=sr.get("total_designations") or 0,
            active_designations=sr.get("active_designations") or 0,
            total_grades=sr.get("total_grades") or 0,
            active_grades=sr.get("active_grades") or 0,
            total_active_units=active_units_sum,
            total_inactive_units=max(0, total_units_sum - active_units_sum),
        )

        # Canonical Active Employee CTE for Headcount Aggregation
        active_cte = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID, o.LocID, o.DeptID, o.DesigID, o.EmpGradeID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
        ),
        ActiveEmps AS (
            SELECT e.EmpID
            FROM dbo.EmployeeMst e
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
        )
        """

        # 1. Company Distribution
        comp_sql = f"""
        {active_cte}
        SELECT
            ISNULL(c.CompID, 0) AS id,
            ISNULL(c.CompName, 'Unassigned Company') AS name,
            c.CompCode AS code,
            COUNT(ae.EmpID) AS count
        FROM ActiveEmps ae
        JOIN CurrentOfficial co ON ae.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID
        LEFT JOIN dbo.OrgCompanyMst c ON l.CompID = c.CompID
        GROUP BY c.CompID, c.CompName, c.CompCode
        ORDER BY count DESC;
        """
        comp_rows = execute_readonly_query(comp_sql)

        # 2. Location Distribution
        loc_sql = f"""
        {active_cte}
        SELECT
            ISNULL(l.LocID, 0) AS id,
            ISNULL(l.LocName, 'Unassigned Location') AS name,
            l.ShortName AS code,
            COUNT(ae.EmpID) AS count
        FROM ActiveEmps ae
        LEFT JOIN CurrentOfficial co ON ae.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID
        GROUP BY l.LocID, l.LocName, l.ShortName
        ORDER BY count DESC;
        """
        loc_rows = execute_readonly_query(loc_sql)

        # 3. Top Departments Distribution
        dept_sql = f"""
        {active_cte}
        SELECT TOP 15
            ISNULL(d.DeptID, 0) AS id,
            ISNULL(d.DeptName, 'Unassigned Department') AS name,
            d.CosecDeptId AS code,
            COUNT(ae.EmpID) AS count
        FROM ActiveEmps ae
        LEFT JOIN CurrentOfficial co ON ae.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID
        GROUP BY d.DeptID, d.DeptName, d.CosecDeptId
        ORDER BY count DESC;
        """
        dept_rows = execute_readonly_query(dept_sql)

        # 4. Grade Distribution
        grade_sql = f"""
        {active_cte}
        SELECT
            ISNULL(g.EmpGradeID, 0) AS id,
            ISNULL(g.EmpGradeDesc, 'Unassigned Grade') AS name,
            NULL AS code,
            COUNT(ae.EmpID) AS count
        FROM ActiveEmps ae
        LEFT JOIN CurrentOfficial co ON ae.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.EmployeeGradeMst g ON co.EmpGradeID = g.EmpGradeID
        GROUP BY g.EmpGradeID, g.EmpGradeDesc
        ORDER BY g.EmpGradeID ASC;
        """
        grade_rows = execute_readonly_query(grade_sql)

        total_active_sql = """
        SELECT COUNT(*) AS total
        FROM dbo.EmployeeMst
        WHERE EmpIsActive = 1 AND EmpIsDeleted = 0 AND (EmpResignDate IS NULL OR EmpResignDate > GETDATE());
        """
        total_active_res = execute_readonly_query(total_active_sql)
        total_active = total_active_res[0]["total"] if total_active_res else 1316

        def map_items(rows: list[dict[str, Any]]) -> list[OrgHeadcountItem]:
            items = []
            for r in rows:
                cnt = r.get("count") or 0
                pct = round((cnt / (total_active or 1)) * 100, 1)
                items.append(
                    OrgHeadcountItem(
                        id=r.get("id") or 0,
                        name=r.get("name") or "Unknown",
                        code=str(r["code"]) if r.get("code") is not None else None,
                        count=cnt,
                        percentage=pct,
                    )
                )
            return items

        return OrgOverviewResponse(
            scale_counts=scale_counts,
            headcount_by_company=map_items(comp_rows),
            headcount_by_location=map_items(loc_rows),
            headcount_by_top_departments=map_items(dept_rows),
            headcount_by_grade=map_items(grade_rows),
            active_employee_total=total_active,
        )

    # ══════════════════════════════════════════════════════════════════════════════
    # 2. MULTI-LEVEL HIERARCHY TREE MAP
    # ══════════════════════════════════════════════════════════════════════════════

    async def get_org_hierarchy_map(self) -> OrgHierarchyResponse:
        """
        Builds recursive multi-tier tree:
        Company -> Location -> Main Dept -> Operational Dept -> Designation
        reflecting the actual database foreign keys and employee posting mappings.
        """
        sql = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID, o.LocID, o.DeptID, o.DesigID, o.EmpGradeID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
        ),
        ActiveEmps AS (
            SELECT e.EmpID
            FROM dbo.EmployeeMst e
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
        )
        SELECT
            c.CompID,
            c.CompName,
            c.CompCode,
            l.LocID,
            l.LocName,
            l.ShortName AS LocShortName,
            l.SOSSiteHeadEmpID,
            she.EmpCode AS site_head_code,
            she.EmpFirstName + ' ' + ISNULL(she.EmpLastName, '') AS site_head_name,
            md.MainDeptID,
            md.DeptName AS MainDeptName,
            d.DeptID,
            d.DeptName,
            d.DeptHeadEmpID,
            he.EmpCode AS dept_head_code,
            he.EmpFirstName + ' ' + ISNULL(he.EmpLastName, '') AS dept_head_name,
            dg.DesigID,
            dg.DesigName,
            COUNT(ae.EmpID) AS headcount
        FROM ActiveEmps ae
        JOIN CurrentOfficial co ON ae.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID
        LEFT JOIN dbo.OrgCompanyMst c ON l.CompID = c.CompID
        LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID
        LEFT JOIN dbo.OrgMainDepartmentMst md ON d.MainDeptID = md.MainDeptID
        LEFT JOIN dbo.OrgDesignationMst dg ON co.DesigID = dg.DesigID
        LEFT JOIN dbo.EmployeeMst she ON l.SOSSiteHeadEmpID = she.EmpID
        LEFT JOIN dbo.EmployeeMst he ON d.DeptHeadEmpID = he.EmpID
        GROUP BY
            c.CompID, c.CompName, c.CompCode,
            l.LocID, l.LocName, l.ShortName, l.SOSSiteHeadEmpID,
            she.EmpCode, she.EmpFirstName, she.EmpLastName,
            md.MainDeptID, md.DeptName,
            d.DeptID, d.DeptName, d.DeptHeadEmpID,
            he.EmpCode, he.EmpFirstName, he.EmpLastName,
            dg.DesigID, dg.DesigName
        ORDER BY c.CompID, l.LocID, d.DeptName, dg.DesigName;
        """
        rows = execute_readonly_query(sql)

        # Build nested tree: Company -> Location -> Department -> Designation
        companies_map: dict[int, OrgHierarchyNode] = {}
        locations_map: dict[str, OrgHierarchyNode] = {}
        depts_map: dict[str, OrgHierarchyNode] = {}

        total_emps = 0
        total_paths = len(rows)

        for r in rows:
            comp_id = r.get("CompID") or 0
            comp_name = r.get("CompName") or "Unassigned Company"
            comp_code = r.get("CompCode")
            loc_id = r.get("LocID") or 0
            loc_name = r.get("LocName") or "Unassigned Location"
            loc_code = r.get("LocShortName")
            dept_id = r.get("DeptID") or 0
            dept_name = r.get("DeptName") or "Unassigned Department"
            desig_id = r.get("DesigID") or 0
            desig_name = r.get("DesigName") or "Unassigned Designation"
            cnt = r.get("headcount") or 0
            total_emps += cnt

            # 1. Company Node
            if comp_id not in companies_map:
                companies_map[comp_id] = OrgHierarchyNode(
                    id=comp_id,
                    name=comp_name,
                    code=comp_code,
                    level="COMPANY",
                    headcount=0,
                    children=[],
                )
            companies_map[comp_id].headcount += cnt

            # 2. Location Node (keyed by comp_id + loc_id)
            loc_key = f"{comp_id}_{loc_id}"
            if loc_key not in locations_map:
                loc_node = OrgHierarchyNode(
                    id=loc_id,
                    name=loc_name,
                    code=loc_code,
                    level="LOCATION",
                    headcount=0,
                    head_emp_id=r.get("SOSSiteHeadEmpID"),
                    head_name=r.get("site_head_name"),
                    head_code=r.get("site_head_code"),
                    children=[],
                )
                locations_map[loc_key] = loc_node
                companies_map[comp_id].children.append(loc_node)
            locations_map[loc_key].headcount += cnt

            # 3. Department Node (keyed by loc_key + dept_id)
            dept_key = f"{loc_key}_{dept_id}"
            if dept_key not in depts_map:
                dept_node = OrgHierarchyNode(
                    id=dept_id,
                    name=dept_name,
                    code=r.get("MainDeptName"),
                    level="DEPARTMENT",
                    headcount=0,
                    head_emp_id=r.get("DeptHeadEmpID"),
                    head_name=r.get("dept_head_name"),
                    head_code=r.get("dept_head_code"),
                    children=[],
                )
                depts_map[dept_key] = dept_node
                locations_map[loc_key].children.append(dept_node)
            depts_map[dept_key].headcount += cnt

            # 4. Designation Leaf Node
            desig_node = OrgHierarchyNode(
                id=desig_id,
                name=desig_name,
                level="DESIGNATION",
                headcount=cnt,
                children=[],
            )
            depts_map[dept_key].children.append(desig_node)

        return OrgHierarchyResponse(
            companies=list(companies_map.values()),
            total_active_employees=total_emps,
            total_hierarchical_paths=total_paths,
        )

    # ══════════════════════════════════════════════════════════════════════════════
    # 3. ORGANIZATIONAL UNITS CATALOG
    # ══════════════════════════════════════════════════════════════════════════════

    async def get_org_units(
        self,
        unit_type: OrgUnitType | None = None,
        search: str | None = None,
        comp_id: int | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> OrgUnitListResponse:
        """
        Retrieves unified catalog of organizational units across all levels.
        """
        queries = []

        # Active employee mapping CTE for count calculation

        # 1. Company
        if unit_type is None or unit_type == OrgUnitType.COMPANY:
            queries.append("""
            SELECT
                c.CompID AS unit_id,
                'COMPANY' AS unit_type,
                CAST(c.CompCode AS NVARCHAR(50)) AS unit_code,
                CAST(c.CompName AS NVARCHAR(200)) AS unit_name,
                CAST(NULL AS BIGINT) AS parent_id,
                CAST(NULL AS NVARCHAR(200)) AS parent_name,
                CAST(NULL AS BIGINT) AS head_emp_id,
                CAST(NULL AS NVARCHAR(200)) AS head_name,
                CAST(NULL AS NVARCHAR(50)) AS head_code,
                (
                    SELECT COUNT(*)
                    FROM dbo.EmployeeOfficialDet o
                    JOIN dbo.EmployeeMst em ON o.EmpID = em.EmpID
                    JOIN dbo.OrgLocationMst l ON o.LocID = l.LocID
                    WHERE l.CompID = c.CompID
                      AND o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
                      AND em.EmpIsActive = 1 AND em.EmpIsDeleted = 0 AND (em.EmpResignDate IS NULL OR em.EmpResignDate > GETDATE())
                ) AS active_headcount,
                c.CompIsActive AS is_active,
                c.CompIsDeleted AS is_deleted
            FROM dbo.OrgCompanyMst c
            """)

        # 2. Location
        if unit_type is None or unit_type == OrgUnitType.LOCATION:
            queries.append("""
            SELECT
                l.LocID AS unit_id,
                'LOCATION' AS unit_type,
                CAST(l.ShortName AS NVARCHAR(50)) AS unit_code,
                CAST(l.LocName AS NVARCHAR(200)) AS unit_name,
                CAST(l.CompID AS BIGINT) AS parent_id,
                CAST(c.CompName AS NVARCHAR(200)) AS parent_name,
                CAST(l.SOSSiteHeadEmpID AS BIGINT) AS head_emp_id,
                CAST(he.EmpFirstName + ' ' + ISNULL(he.EmpLastName, '') AS NVARCHAR(200)) AS head_name,
                CAST(he.EmpCode AS NVARCHAR(50)) AS head_code,
                (
                    SELECT COUNT(*)
                    FROM dbo.EmployeeOfficialDet o
                    JOIN dbo.EmployeeMst em ON o.EmpID = em.EmpID
                    WHERE o.LocID = l.LocID
                      AND o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
                      AND em.EmpIsActive = 1 AND em.EmpIsDeleted = 0 AND (em.EmpResignDate IS NULL OR em.EmpResignDate > GETDATE())
                ) AS active_headcount,
                l.LocIsActive AS is_active,
                l.LocIsDeleted AS is_deleted
            FROM dbo.OrgLocationMst l
            LEFT JOIN dbo.OrgCompanyMst c ON l.CompID = c.CompID
            LEFT JOIN dbo.EmployeeMst he ON l.SOSSiteHeadEmpID = he.EmpID
            """)

        # 3. Main Department
        if unit_type is None or unit_type == OrgUnitType.MAIN_DEPT:
            queries.append("""
            SELECT
                md.MainDeptID AS unit_id,
                'MAIN_DEPT' AS unit_type,
                CAST(NULL AS NVARCHAR(50)) AS unit_code,
                CAST(md.DeptName AS NVARCHAR(200)) AS unit_name,
                CAST(NULL AS BIGINT) AS parent_id,
                CAST(NULL AS NVARCHAR(200)) AS parent_name,
                CAST(NULL AS BIGINT) AS head_emp_id,
                CAST(NULL AS NVARCHAR(200)) AS head_name,
                CAST(NULL AS NVARCHAR(50)) AS head_code,
                (
                    SELECT COUNT(*)
                    FROM dbo.EmployeeOfficialDet o
                    JOIN dbo.EmployeeMst em ON o.EmpID = em.EmpID
                    JOIN dbo.OrgDepartmentMst d ON o.DeptID = d.DeptID
                    WHERE d.MainDeptID = md.MainDeptID
                      AND o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
                      AND em.EmpIsActive = 1 AND em.EmpIsDeleted = 0 AND (em.EmpResignDate IS NULL OR em.EmpResignDate > GETDATE())
                ) AS active_headcount,
                md.IsActive AS is_active,
                CAST(0 AS BIT) AS is_deleted
            FROM dbo.OrgMainDepartmentMst md
            """)

        # 4. Department
        if unit_type is None or unit_type == OrgUnitType.DEPARTMENT:
            queries.append("""
            SELECT
                d.DeptID AS unit_id,
                'DEPARTMENT' AS unit_type,
                CAST(d.CosecDeptId AS NVARCHAR(50)) AS unit_code,
                CAST(d.DeptName AS NVARCHAR(200)) AS unit_name,
                CAST(d.MainDeptID AS BIGINT) AS parent_id,
                CAST(md.DeptName AS NVARCHAR(200)) AS parent_name,
                CAST(d.DeptHeadEmpID AS BIGINT) AS head_emp_id,
                CAST(he.EmpFirstName + ' ' + ISNULL(he.EmpLastName, '') AS NVARCHAR(200)) AS head_name,
                CAST(he.EmpCode AS NVARCHAR(50)) AS head_code,
                (
                    SELECT COUNT(*)
                    FROM dbo.EmployeeOfficialDet o
                    JOIN dbo.EmployeeMst em ON o.EmpID = em.EmpID
                    WHERE o.DeptID = d.DeptID
                      AND o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
                      AND em.EmpIsActive = 1 AND em.EmpIsDeleted = 0 AND (em.EmpResignDate IS NULL OR em.EmpResignDate > GETDATE())
                ) AS active_headcount,
                d.DeptIsActive AS is_active,
                d.DeptIsDeleted AS is_deleted
            FROM dbo.OrgDepartmentMst d
            LEFT JOIN dbo.OrgMainDepartmentMst md ON d.MainDeptID = md.MainDeptID
            LEFT JOIN dbo.EmployeeMst he ON d.DeptHeadEmpID = he.EmpID
            """)

        # 5. Designation
        if unit_type is None or unit_type == OrgUnitType.DESIGNATION:
            queries.append("""
            SELECT
                dg.DesigID AS unit_id,
                'DESIGNATION' AS unit_type,
                CAST(dg.DesigType AS NVARCHAR(50)) AS unit_code,
                CAST(dg.DesigName AS NVARCHAR(200)) AS unit_name,
                CAST(dg.DeptID AS BIGINT) AS parent_id,
                CAST(d.DeptName AS NVARCHAR(200)) AS parent_name,
                CAST(NULL AS BIGINT) AS head_emp_id,
                CAST(NULL AS NVARCHAR(200)) AS head_name,
                CAST(NULL AS NVARCHAR(50)) AS head_code,
                (
                    SELECT COUNT(*)
                    FROM dbo.EmployeeOfficialDet o
                    JOIN dbo.EmployeeMst em ON o.EmpID = em.EmpID
                    WHERE o.DesigID = dg.DesigID
                      AND o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
                      AND em.EmpIsActive = 1 AND em.EmpIsDeleted = 0 AND (em.EmpResignDate IS NULL OR em.EmpResignDate > GETDATE())
                ) AS active_headcount,
                dg.DesigIsActive AS is_active,
                dg.DesigIsDeleted AS is_deleted
            FROM dbo.OrgDesignationMst dg
            LEFT JOIN dbo.OrgDepartmentMst d ON dg.DeptID = d.DeptID
            """)

        # 6. Grade
        if unit_type is None or unit_type == OrgUnitType.GRADE:
            queries.append("""
            SELECT
                g.EmpGradeID AS unit_id,
                'GRADE' AS unit_type,
                CAST(NULL AS NVARCHAR(50)) AS unit_code,
                CAST(g.EmpGradeDesc AS NVARCHAR(200)) AS unit_name,
                CAST(NULL AS BIGINT) AS parent_id,
                CAST(NULL AS NVARCHAR(200)) AS parent_name,
                CAST(NULL AS BIGINT) AS head_emp_id,
                CAST(NULL AS NVARCHAR(200)) AS head_name,
                CAST(NULL AS NVARCHAR(50)) AS head_code,
                (
                    SELECT COUNT(*)
                    FROM dbo.EmployeeOfficialDet o
                    JOIN dbo.EmployeeMst em ON o.EmpID = em.EmpID
                    WHERE o.EmpGradeID = g.EmpGradeID
                      AND o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
                      AND em.EmpIsActive = 1 AND em.EmpIsDeleted = 0 AND (em.EmpResignDate IS NULL OR em.EmpResignDate > GETDATE())
                ) AS active_headcount,
                g.EmpGradeIsActive AS is_active,
                g.EmpGradeIsDeleted AS is_deleted
            FROM dbo.EmployeeGradeMst g
            """)

        full_union = " UNION ALL ".join(queries)

        where_clauses = []
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if search:
            where_clauses.append(
                "(unit_name LIKE :search OR unit_code LIKE :search OR parent_name LIKE :search)"
            )
            params["search"] = f"%{search}%"

        where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        count_sql = f"""
        WITH AllUnits AS (
            {full_union}
        )
        SELECT COUNT(*) AS total FROM AllUnits {where_str};
        """
        count_res = execute_readonly_query(count_sql, params)
        total_count = count_res[0]["total"] if count_res else 0

        items_sql = f"""
        WITH AllUnits AS (
            {full_union}
        )
        SELECT * FROM AllUnits {where_str}
        ORDER BY unit_type, active_headcount DESC, unit_name
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        items_res = execute_readonly_query(items_sql, params)

        items = [
            OrgUnitListItem(
                unit_id=r["unit_id"],
                unit_type=OrgUnitType(r["unit_type"]),
                unit_code=r.get("unit_code"),
                unit_name=r["unit_name"],
                parent_id=r.get("parent_id"),
                parent_name=r.get("parent_name"),
                head_emp_id=r.get("head_emp_id"),
                head_name=r.get("head_name"),
                head_code=r.get("head_code"),
                active_headcount=r.get("active_headcount") or 0,
                is_active=bool(r.get("is_active")),
                is_deleted=bool(r.get("is_deleted")),
            )
            for r in items_res
        ]

        return OrgUnitListResponse(
            total=total_count,
            limit=limit,
            offset=offset,
            items=items,
        )

    # ══════════════════════════════════════════════════════════════════════════════
    # 4. EXECUTIVE REPORTING HIERARCHY
    # ══════════════════════════════════════════════════════════════════════════════

    async def get_reporting_hierarchy(self) -> OrgReportingTreeResponse:
        """
        Constructs leadership tree starting from Top Executives (MD / Technical Director)
        down to Functional Leads and Team Members.
        """
        sql = """
        WITH CurrentOfficial AS (
            SELECT
                o.EmpID, o.LocID, o.DeptID, o.DesigID, o.EmpGradeID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
        ),
        ActiveEmps AS (
            SELECT
                e.EmpID,
                e.EmpCode,
                e.EmpFirstName + ' ' + ISNULL(e.EmpMiddleName + ' ', '') + ISNULL(e.EmpLastName, '') AS full_name
            FROM dbo.EmployeeMst e
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
        ),
        FunctionalMgr AS (
            SELECT
                r.EmpID,
                r.ReportingEmpID,
                ROW_NUMBER() OVER (PARTITION BY r.EmpID ORDER BY r.EmpReportingDetID DESC) AS rn
            FROM dbo.EmployeeReportingDet r
            LEFT JOIN dbo.OrgDesignationReportingDet odr
                ON r.DesigID = odr.DesigID AND r.ReportingDesigID = odr.ReportingDesigID AND odr.ReportingIsActive = 1 AND odr.ReportingIsDeleted = 0
            WHERE r.ReportingDetIsActive = 1 AND r.ReportingDetIsDeleted = 0
              AND (odr.ReportingType = 'F' OR odr.ReportingType IS NULL)
        )
        SELECT
            ae.EmpID,
            ae.EmpCode,
            ae.full_name,
            dg.DesigName,
            d.DeptName,
            l.LocName,
            g.EmpGradeDesc,
            fm.ReportingEmpID,
            (SELECT COUNT(*) FROM FunctionalMgr m WHERE m.ReportingEmpID = ae.EmpID AND m.rn = 1) AS direct_reports_count
        FROM ActiveEmps ae
        JOIN CurrentOfficial co ON ae.EmpID = co.EmpID AND co.rn = 1
        LEFT JOIN dbo.OrgDesignationMst dg ON co.DesigID = dg.DesigID
        LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID
        LEFT JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID
        LEFT JOIN dbo.EmployeeGradeMst g ON co.EmpGradeID = g.EmpGradeID
        LEFT JOIN FunctionalMgr fm ON ae.EmpID = fm.EmpID AND fm.rn = 1
        ORDER BY g.EmpGradeID ASC, direct_reports_count DESC, ae.full_name;
        """
        rows = execute_readonly_query(sql)

        # Build tree: Employees with no manager or Grade I are roots
        nodes_by_id: dict[int, OrgReportingNode] = {}
        parent_child_map: dict[int, list[int]] = {}

        for r in rows:
            emp_id = r["EmpID"]
            mgr_id = r.get("ReportingEmpID")
            grade = r.get("EmpGradeDesc") or ""
            desig = r.get("DesigName") or ""

            role_type = "STAFF"
            if "Managing Director" in desig or "Founder" in desig or grade == "Grade I":
                role_type = "EXECUTIVE"
            elif "Director" in desig or grade == "Grade II":
                role_type = "DIRECTOR"
            elif (r.get("direct_reports_count") or 0) > 0:
                role_type = "HOD"

            node = OrgReportingNode(
                emp_id=emp_id,
                emp_code=r.get("EmpCode"),
                full_name=r["full_name"],
                designation=desig,
                department=r.get("DeptName"),
                location=r.get("LocName"),
                role_type=role_type,
                direct_reports_count=r.get("direct_reports_count") or 0,
                subordinates=[],
            )
            nodes_by_id[emp_id] = node

            if mgr_id and mgr_id != emp_id:
                if mgr_id not in parent_child_map:
                    parent_child_map[mgr_id] = []
                parent_child_map[mgr_id].append(emp_id)

        # Link children to parents
        for mgr_id, child_ids in parent_child_map.items():
            if mgr_id in nodes_by_id:
                nodes_by_id[mgr_id].subordinates = [
                    nodes_by_id[cid] for cid in child_ids if cid in nodes_by_id
                ]

        # Roots are executives or top employees without an active manager in this list
        roots = []
        for emp_id, node in nodes_by_id.items():
            mgr_id = next((r.get("ReportingEmpID") for r in rows if r["EmpID"] == emp_id), None)
            if (not mgr_id or mgr_id not in nodes_by_id or node.role_type == "EXECUTIVE") and (
                node.direct_reports_count > 0 or node.role_type == "EXECUTIVE"
            ):
                roots.append(node)

        # Sort roots by direct reports descending
        roots.sort(key=lambda x: (x.role_type != "EXECUTIVE", -x.direct_reports_count))

        total_mgrs = sum(1 for r in rows if (r.get("direct_reports_count") or 0) > 0)

        return OrgReportingTreeResponse(
            roots=roots,
            total_assigned_managers=total_mgrs,
        )

    # ══════════════════════════════════════════════════════════════════════════════
    # 5. DATA QUALITY AUDIT & RULES EVALUATION
    # ══════════════════════════════════════════════════════════════════════════════

    async def get_org_quality(self) -> OrgDataQualityResponse:
        """
        Evaluates 14 canonical data quality rules against the organization structure.
        """
        dq_sql = """
        WITH ActiveEmps AS (
            SELECT EmpID, EmpCode, EmpFirstName + ' ' + ISNULL(EmpLastName, '') AS full_name
            FROM dbo.EmployeeMst
            WHERE EmpIsActive = 1 AND EmpIsDeleted = 0 AND (EmpResignDate IS NULL OR EmpResignDate > GETDATE())
        ),
        CurrentOfficial AS (
            SELECT
                o.EmpID, o.LocID, o.DeptID, o.DesigID, o.EmpGradeID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
        )
        SELECT 'MISSING_OFFICIAL_RECORD' AS code, COUNT(*) AS cnt FROM ActiveEmps e LEFT JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 WHERE co.EmpID IS NULL
        UNION ALL
        SELECT 'MISSING_LOCATION', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 WHERE co.LocID IS NULL OR co.LocID = 0
        UNION ALL
        SELECT 'MISSING_DEPARTMENT', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 WHERE co.DeptID IS NULL OR co.DeptID = 0
        UNION ALL
        SELECT 'MISSING_DESIGNATION', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 WHERE co.DesigID IS NULL OR co.DesigID = 0
        UNION ALL
        SELECT 'MISSING_COMPANY', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 LEFT JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID LEFT JOIN dbo.OrgCompanyMst c ON l.CompID = c.CompID WHERE c.CompID IS NULL
        UNION ALL
        SELECT 'ORPHAN_LOCATION_ID', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 LEFT JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID WHERE co.LocID IS NOT NULL AND co.LocID > 0 AND l.LocID IS NULL
        UNION ALL
        SELECT 'ORPHAN_DEPT_ID', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID WHERE co.DeptID IS NOT NULL AND co.DeptID > 0 AND d.DeptID IS NULL
        UNION ALL
        SELECT 'ORPHAN_DESIG_ID', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 LEFT JOIN dbo.OrgDesignationMst dg ON co.DesigID = dg.DesigID WHERE co.DesigID IS NOT NULL AND co.DesigID > 0 AND dg.DesigID IS NULL
        UNION ALL
        SELECT 'LINKED_TO_INACTIVE_LOCATION', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID WHERE l.LocIsActive = 0 OR l.LocIsDeleted = 1
        UNION ALL
        SELECT 'LINKED_TO_INACTIVE_DEPARTMENT', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID WHERE d.DeptIsActive = 0 OR d.DeptIsDeleted = 1
        UNION ALL
        SELECT 'LINKED_TO_INACTIVE_DESIGNATION', COUNT(*) FROM ActiveEmps e JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1 JOIN dbo.OrgDesignationMst dg ON co.DesigID = dg.DesigID WHERE dg.DesigIsActive = 0 OR dg.DesigIsDeleted = 1
        UNION ALL
        SELECT 'DEPT_WITHOUT_MAIN_DEPT', COUNT(*) FROM dbo.OrgDepartmentMst d LEFT JOIN dbo.OrgMainDepartmentMst md ON d.MainDeptID = md.MainDeptID WHERE d.DeptIsActive = 1 AND d.DeptIsDeleted = 0 AND (d.MainDeptID IS NULL OR md.MainDeptID IS NULL)
        UNION ALL
        SELECT 'LOCATION_WITHOUT_COMPANY', COUNT(*) FROM dbo.OrgLocationMst l LEFT JOIN dbo.OrgCompanyMst c ON l.CompID = c.CompID WHERE l.LocIsActive = 1 AND l.LocIsDeleted = 0 AND (l.CompID IS NULL OR c.CompID IS NULL)
        UNION ALL
        SELECT 'EMPTY_LOCATIONS', COUNT(*) FROM dbo.OrgLocationMst l WHERE l.LocIsActive = 1 AND l.LocIsDeleted = 0 AND l.LocID NOT IN (SELECT DISTINCT LocID FROM CurrentOfficial WHERE LocID IS NOT NULL)
        UNION ALL
        SELECT 'EMPTY_DEPARTMENTS', COUNT(*) FROM dbo.OrgDepartmentMst d WHERE d.DeptIsActive = 1 AND d.DeptIsDeleted = 0 AND d.DeptID NOT IN (SELECT DISTINCT DeptID FROM CurrentOfficial WHERE DeptID IS NOT NULL)
        UNION ALL
        SELECT 'EMPTY_DESIGNATIONS', COUNT(*) FROM dbo.OrgDesignationMst dg WHERE dg.DesigIsActive = 1 AND dg.DesigIsDeleted = 0 AND dg.DesigID NOT IN (SELECT DISTINCT DesigID FROM CurrentOfficial WHERE DesigID IS NOT NULL)
        UNION ALL
        SELECT 'MULTIPLE_ACTIVE_POSITIONS', COUNT(*) FROM (SELECT EmpID FROM dbo.EmployeeOfficialDet WHERE EmpOfficeDetIsActive = 1 AND EmpOfficeDetIsDeleted = 0 AND EmpID IS NOT NULL GROUP BY EmpID HAVING COUNT(*) > 1) sub
        UNION ALL
        SELECT 'INACTIVE_ORGANIZATION_UNITS', (SELECT COUNT(*) FROM dbo.OrgLocationMst WHERE LocIsActive = 0 OR LocIsDeleted = 1) + (SELECT COUNT(*) FROM dbo.OrgDepartmentMst WHERE DeptIsActive = 0 OR DeptIsDeleted = 1) + (SELECT COUNT(*) FROM dbo.OrgDesignationMst WHERE DesigIsActive = 0 OR DesigIsDeleted = 1);
        """
        dq_rows = execute_readonly_query(dq_sql)
        counts = {r["code"]: r["cnt"] for r in dq_rows}

        rules_catalog = [
            # CRITICAL
            {
                "rule_code": "MISSING_OFFICIAL_RECORD",
                "rule_name": "Active Employee Missing Official Record",
                "severity": IssueSeverity.CRITICAL,
                "description": "Active employees with no job position record in EmployeeOfficialDet.",
                "impact": "Employee is excluded from department payroll, reporting lines, and access policies.",
                "recommendation": "Assign an active posting record in EmployeeOfficialDet.",
            },
            {
                "rule_code": "MULTIPLE_ACTIVE_POSITIONS",
                "rule_name": "Multiple Current Position Records",
                "severity": IssueSeverity.CRITICAL,
                "description": "Employee has multiple concurrent position records marked as active.",
                "impact": "Causes duplicate counting and ambiguous organizational mapping.",
                "recommendation": "Deactivate superseded position records so only the latest is active.",
            },
            {
                "rule_code": "ORPHAN_LOCATION_ID",
                "rule_name": "Invalid / Orphan Location ID",
                "severity": IssueSeverity.CRITICAL,
                "description": "Employee position references a non-existent LocID.",
                "impact": "Broken foreign key preventing site-based rollups and access control.",
                "recommendation": "Remap position to a valid LocID from OrgLocationMst.",
            },
            {
                "rule_code": "ORPHAN_DEPT_ID",
                "rule_name": "Invalid / Orphan Department ID",
                "severity": IssueSeverity.CRITICAL,
                "description": "Employee position references a non-existent DeptID.",
                "impact": "Department rollups and budgeting calculations fail.",
                "recommendation": "Remap position to a valid DeptID from OrgDepartmentMst.",
            },
            {
                "rule_code": "ORPHAN_DESIG_ID",
                "rule_name": "Invalid / Orphan Designation ID",
                "severity": IssueSeverity.CRITICAL,
                "description": "Employee position references a non-existent DesigID.",
                "impact": "Job titles and grade structures cannot be resolved.",
                "recommendation": "Remap position to a valid DesigID from OrgDesignationMst.",
            },
            # WARNING
            {
                "rule_code": "LINKED_TO_INACTIVE_LOCATION",
                "rule_name": "Employee Linked to Inactive Location",
                "severity": IssueSeverity.WARNING,
                "description": "Active employee assigned to a deactivated or deleted facility/site.",
                "impact": "Staff mapped to closed plants or legacy facilities.",
                "recommendation": "Transfer active staff to an active operational location.",
            },
            {
                "rule_code": "LINKED_TO_INACTIVE_DEPARTMENT",
                "rule_name": "Employee Linked to Inactive Department",
                "severity": IssueSeverity.WARNING,
                "description": "Active employee assigned to a deactivated department.",
                "impact": "Staff mapped to disbanded functional groups.",
                "recommendation": "Reassign staff to an active operational department.",
            },
            {
                "rule_code": "LINKED_TO_INACTIVE_DESIGNATION",
                "rule_name": "Employee Linked to Inactive Designation",
                "severity": IssueSeverity.WARNING,
                "description": "Active employee assigned to a retired job title.",
                "impact": "Outdated job role definitions.",
                "recommendation": "Update employee position to current active designation.",
            },
            {
                "rule_code": "EMPTY_LOCATIONS",
                "rule_name": "Empty Active Locations (0 Staff)",
                "severity": IssueSeverity.WARNING,
                "description": "Active locations or plants with zero currently assigned active employees.",
                "impact": "Unused site masters cluttering location selectors.",
                "recommendation": "Review whether these sites should be deactivated or populated.",
            },
            {
                "rule_code": "EMPTY_DEPARTMENTS",
                "rule_name": "Empty Active Departments (0 Staff)",
                "severity": IssueSeverity.WARNING,
                "description": "Active departments with zero currently assigned active employees.",
                "impact": "Orphan operational units without active workforce.",
                "recommendation": "Audit and deactivate obsolete departments.",
            },
            {
                "rule_code": "EMPTY_DESIGNATIONS",
                "rule_name": "Empty Active Designations (0 Staff)",
                "severity": IssueSeverity.WARNING,
                "description": "Active job designations with zero currently assigned active employees.",
                "impact": "Redundant designations inflating organization catalogs.",
                "recommendation": "Retire unused job titles.",
            },
            {
                "rule_code": "DEPT_WITHOUT_MAIN_DEPT",
                "rule_name": "Department without Valid Main Division",
                "severity": IssueSeverity.WARNING,
                "description": "Active department missing or referencing invalid MainDeptID.",
                "impact": "Breaks division-level rollups in executive analytics.",
                "recommendation": "Assign a valid MainDeptID to the department.",
            },
            {
                "rule_code": "LOCATION_WITHOUT_COMPANY",
                "rule_name": "Location without Valid Company",
                "severity": IssueSeverity.WARNING,
                "description": "Active location missing or referencing invalid CompID.",
                "impact": "Location cannot be resolved to a legal entity.",
                "recommendation": "Link location to a valid company master record.",
            },
            # INFO
            {
                "rule_code": "INACTIVE_ORGANIZATION_UNITS",
                "rule_name": "Inactive / Decommissioned Units in Master",
                "severity": IssueSeverity.INFO,
                "description": "Decommissioned or soft-deleted locations, departments, and designations preserved for audit history.",
                "impact": "Historical records preserved safely.",
                "recommendation": "No action required; preserve historical traces.",
            },
        ]

        evaluated_rules = []
        crit_count = 0
        warn_count = 0
        info_count = 0

        for r in rules_catalog:
            code = r["rule_code"]
            cnt = counts.get(code, 0)
            sev = r["severity"]

            if sev == IssueSeverity.CRITICAL:
                crit_count += cnt
            elif sev == IssueSeverity.WARNING:
                warn_count += cnt
            elif sev == IssueSeverity.INFO:
                info_count += cnt

            evaluated_rules.append(
                OrgQualityRuleResult(
                    rule_code=code,
                    rule_name=r["rule_name"],
                    severity=sev,
                    description=r["description"],
                    issue_count=cnt,
                    impact=r["impact"],
                    recommendation=r["recommendation"],
                )
            )

        # Health score calculation
        penalty = (crit_count * 5.0) + (warn_count * 0.5)
        overall_health = max(0.0, min(100.0, round(100.0 - penalty, 1)))

        return OrgDataQualityResponse(
            overall_health_score=overall_health,
            critical_issues_count=crit_count,
            warning_issues_count=warn_count,
            info_issues_count=info_count,
            rules=evaluated_rules,
            summary_by_severity={
                "CRITICAL": crit_count,
                "WARNING": warn_count,
                "INFO": info_count,
            },
        )

    # ══════════════════════════════════════════════════════════════════════════════
    # 6. DRILLDOWN OF FLAGGED QUALITY ISSUE RECORDS
    # ══════════════════════════════════════════════════════════════════════════════

    async def get_org_quality_issues(
        self,
        issue_code: str,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> OrgQualityIssuesListResponse:
        """
        Retrieves paginated drilldown of specific records flagged by a data quality rule.
        """
        active_cte = """
        WITH ActiveEmps AS (
            SELECT
                e.EmpID,
                e.EmpCode,
                e.EmpFirstName + ' ' + ISNULL(e.EmpMiddleName + ' ', '') + ISNULL(e.EmpLastName, '') AS full_name
            FROM dbo.EmployeeMst e
            WHERE e.EmpIsActive = 1 AND e.EmpIsDeleted = 0 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())
        ),
        CurrentOfficial AS (
            SELECT
                o.EmpID, o.LocID, o.DeptID, o.DesigID, o.EmpGradeID,
                ROW_NUMBER() OVER (PARTITION BY o.EmpID ORDER BY o.ApplicableFrDate DESC, o.EmpOfficeDetID DESC) AS rn
            FROM dbo.EmployeeOfficialDet o
            WHERE o.EmpOfficeDetIsActive = 1 AND o.EmpOfficeDetIsDeleted = 0
        )
        """

        code = issue_code.upper()
        issue_query_body = ""

        if code == "MISSING_OFFICIAL_RECORD":
            issue_query_body = """
            SELECT
                e.EmpID AS record_id,
                'EMPLOYEE' AS entity_type,
                e.full_name AS entity_name,
                'MISSING_OFFICIAL_RECORD' AS issue_code,
                'Employee #' + CAST(e.EmpID AS NVARCHAR(20)) + ' (' + ISNULL(e.EmpCode, 'No Code') + ') has no posting record in EmployeeOfficialDet' AS issue_detail
            FROM ActiveEmps e
            LEFT JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
            WHERE co.EmpID IS NULL
            """
        elif code == "MULTIPLE_ACTIVE_POSITIONS":
            issue_query_body = """
            SELECT
                sub.EmpID AS record_id,
                'EMPLOYEE' AS entity_type,
                e.EmpFirstName + ' ' + ISNULL(e.EmpLastName, '') AS entity_name,
                'MULTIPLE_ACTIVE_POSITIONS' AS issue_code,
                'Employee has ' + CAST(sub.cnt AS NVARCHAR(10)) + ' concurrent active position records in EmployeeOfficialDet' AS issue_detail
            FROM (
                SELECT EmpID, COUNT(*) AS cnt
                FROM dbo.EmployeeOfficialDet
                WHERE EmpOfficeDetIsActive = 1 AND EmpOfficeDetIsDeleted = 0 AND EmpID IS NOT NULL
                GROUP BY EmpID
                HAVING COUNT(*) > 1
            ) sub
            JOIN dbo.EmployeeMst e ON sub.EmpID = e.EmpID
            """
        elif code == "ORPHAN_LOCATION_ID":
            issue_query_body = """
            SELECT
                co.EmpID AS record_id,
                'POSITION' AS entity_type,
                e.full_name AS entity_name,
                'ORPHAN_LOCATION_ID' AS issue_code,
                'Position references non-existent LocID ' + CAST(co.LocID AS NVARCHAR(10)) AS issue_detail
            FROM CurrentOfficial co
            JOIN ActiveEmps e ON co.EmpID = e.EmpID
            LEFT JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID
            WHERE co.rn = 1 AND co.LocID IS NOT NULL AND l.LocID IS NULL
            """
        elif code == "ORPHAN_DEPT_ID":
            issue_query_body = """
            SELECT
                co.EmpID AS record_id,
                'POSITION' AS entity_type,
                e.full_name AS entity_name,
                'ORPHAN_DEPT_ID' AS issue_code,
                'Position references non-existent DeptID ' + CAST(co.DeptID AS NVARCHAR(10)) AS issue_detail
            FROM CurrentOfficial co
            JOIN ActiveEmps e ON co.EmpID = e.EmpID
            LEFT JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID
            WHERE co.rn = 1 AND co.DeptID IS NOT NULL AND d.DeptID IS NULL
            """
        elif code == "ORPHAN_DESIG_ID":
            issue_query_body = """
            SELECT
                co.EmpID AS record_id,
                'POSITION' AS entity_type,
                e.full_name AS entity_name,
                'ORPHAN_DESIG_ID' AS issue_code,
                'Position references non-existent DesigID ' + CAST(co.DesigID AS NVARCHAR(10)) AS issue_detail
            FROM CurrentOfficial co
            JOIN ActiveEmps e ON co.EmpID = e.EmpID
            LEFT JOIN dbo.OrgDesignationMst dg ON co.DesigID = dg.DesigID
            WHERE co.rn = 1 AND co.DesigID IS NOT NULL AND dg.DesigID IS NULL
            """
        elif code == "LINKED_TO_INACTIVE_LOCATION":
            issue_query_body = """
            SELECT
                e.EmpID AS record_id,
                'EMPLOYEE' AS entity_type,
                e.full_name AS entity_name,
                'LINKED_TO_INACTIVE_LOCATION' AS issue_code,
                'Assigned to inactive/deleted site: ' + ISNULL(l.LocName, 'LocID ' + CAST(co.LocID AS NVARCHAR(10))) AS issue_detail
            FROM ActiveEmps e
            JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
            JOIN dbo.OrgLocationMst l ON co.LocID = l.LocID
            WHERE l.LocIsActive = 0 OR l.LocIsDeleted = 1
            """
        elif code == "LINKED_TO_INACTIVE_DEPARTMENT":
            issue_query_body = """
            SELECT
                e.EmpID AS record_id,
                'EMPLOYEE' AS entity_type,
                e.full_name AS entity_name,
                'LINKED_TO_INACTIVE_DEPARTMENT' AS issue_code,
                'Assigned to inactive/deleted department: ' + ISNULL(d.DeptName, 'DeptID ' + CAST(co.DeptID AS NVARCHAR(10))) AS issue_detail
            FROM ActiveEmps e
            JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
            JOIN dbo.OrgDepartmentMst d ON co.DeptID = d.DeptID
            WHERE d.DeptIsActive = 0 OR d.DeptIsDeleted = 1
            """
        elif code == "LINKED_TO_INACTIVE_DESIGNATION":
            issue_query_body = """
            SELECT
                e.EmpID AS record_id,
                'EMPLOYEE' AS entity_type,
                e.full_name AS entity_name,
                'LINKED_TO_INACTIVE_DESIGNATION' AS issue_code,
                'Assigned to inactive/deleted designation: ' + ISNULL(dg.DesigName, 'DesigID ' + CAST(co.DesigID AS NVARCHAR(10))) AS issue_detail
            FROM ActiveEmps e
            JOIN CurrentOfficial co ON e.EmpID = co.EmpID AND co.rn = 1
            JOIN dbo.OrgDesignationMst dg ON co.DesigID = dg.DesigID
            WHERE dg.DesigIsActive = 0 OR dg.DesigIsDeleted = 1
            """
        elif code == "EMPTY_LOCATIONS":
            issue_query_body = """
            SELECT
                l.LocID AS record_id,
                'LOCATION' AS entity_type,
                l.LocName AS entity_name,
                'EMPTY_LOCATIONS' AS issue_code,
                'Active location "' + l.LocName + '" has 0 assigned active employees' AS issue_detail
            FROM dbo.OrgLocationMst l
            WHERE l.LocIsActive = 1 AND l.LocIsDeleted = 0
              AND l.LocID NOT IN (SELECT DISTINCT LocID FROM CurrentOfficial WHERE LocID IS NOT NULL)
            """
        elif code == "EMPTY_DEPARTMENTS":
            issue_query_body = """
            SELECT
                d.DeptID AS record_id,
                'DEPARTMENT' AS entity_type,
                d.DeptName AS entity_name,
                'EMPTY_DEPARTMENTS' AS issue_code,
                'Active department "' + d.DeptName + '" has 0 assigned active employees' AS issue_detail
            FROM dbo.OrgDepartmentMst d
            WHERE d.DeptIsActive = 1 AND d.DeptIsDeleted = 0
              AND d.DeptID NOT IN (SELECT DISTINCT DeptID FROM CurrentOfficial WHERE DeptID IS NOT NULL)
            """
        elif code == "EMPTY_DESIGNATIONS":
            issue_query_body = """
            SELECT
                dg.DesigID AS record_id,
                'DESIGNATION' AS entity_type,
                dg.DesigName AS entity_name,
                'EMPTY_DESIGNATIONS' AS issue_code,
                'Active designation "' + dg.DesigName + '" has 0 assigned active employees' AS issue_detail
            FROM dbo.OrgDesignationMst dg
            WHERE dg.DesigIsActive = 1 AND dg.DesigIsDeleted = 0
              AND dg.DesigID NOT IN (SELECT DISTINCT DesigID FROM CurrentOfficial WHERE DesigID IS NOT NULL)
            """
        elif code == "DEPT_WITHOUT_MAIN_DEPT":
            issue_query_body = """
            SELECT
                d.DeptID AS record_id,
                'DEPARTMENT' AS entity_type,
                d.DeptName AS entity_name,
                'DEPT_WITHOUT_MAIN_DEPT' AS issue_code,
                'Active department "' + d.DeptName + '" is not linked to any valid Main Division' AS issue_detail
            FROM dbo.OrgDepartmentMst d
            LEFT JOIN dbo.OrgMainDepartmentMst md ON d.MainDeptID = md.MainDeptID
            WHERE d.DeptIsActive = 1 AND d.DeptIsDeleted = 0 AND (d.MainDeptID IS NULL OR md.MainDeptID IS NULL)
            """
        elif code == "LOCATION_WITHOUT_COMPANY":
            issue_query_body = """
            SELECT
                l.LocID AS record_id,
                'LOCATION' AS entity_type,
                l.LocName AS entity_name,
                'LOCATION_WITHOUT_COMPANY' AS issue_code,
                'Active location "' + l.LocName + '" is not linked to any valid Company' AS issue_detail
            FROM dbo.OrgLocationMst l
            LEFT JOIN dbo.OrgCompanyMst c ON l.CompID = c.CompID
            WHERE l.LocIsActive = 1 AND l.LocIsDeleted = 0 AND (l.CompID IS NULL OR c.CompID IS NULL)
            """
        elif code == "INACTIVE_ORGANIZATION_UNITS":
            issue_query_body = """
            SELECT
                l.LocID AS record_id,
                'LOCATION' AS entity_type,
                l.LocName AS entity_name,
                'INACTIVE_ORGANIZATION_UNITS' AS issue_code,
                'Deactivated / deleted location site master' AS issue_detail
            FROM dbo.OrgLocationMst l
            WHERE l.LocIsActive = 0 OR l.LocIsDeleted = 1
            UNION ALL
            SELECT
                d.DeptID AS record_id,
                'DEPARTMENT' AS entity_type,
                d.DeptName AS entity_name,
                'INACTIVE_ORGANIZATION_UNITS' AS issue_code,
                'Deactivated / deleted department master' AS issue_detail
            FROM dbo.OrgDepartmentMst d
            WHERE d.DeptIsActive = 0 OR d.DeptIsDeleted = 1
            UNION ALL
            SELECT
                dg.DesigID AS record_id,
                'DESIGNATION' AS entity_type,
                dg.DesigName AS entity_name,
                'INACTIVE_ORGANIZATION_UNITS' AS issue_code,
                'Deactivated / deleted designation master' AS issue_detail
            FROM dbo.OrgDesignationMst dg
            WHERE dg.DesigIsActive = 0 OR dg.DesigIsDeleted = 1
            """
        else:
            # Fallback empty query
            issue_query_body = """
            SELECT
                0 AS record_id, 'UNKNOWN' AS entity_type, 'N/A' AS entity_name,
                'NO_ISSUES' AS issue_code, 'No matching records found' AS issue_detail
            WHERE 1 = 0
            """

        params: dict[str, Any] = {"limit": limit, "offset": offset}
        where_filter = ""
        if search:
            where_filter = "WHERE entity_name LIKE :search OR issue_detail LIKE :search"
            params["search"] = f"%{search}%"

        full_cte_query = f"""
        {active_cte},
        IssueRecords AS (
            {issue_query_body}
        )
        """

        count_sql = f"""
        {full_cte_query}
        SELECT COUNT(*) AS total FROM IssueRecords {where_filter};
        """
        count_res = execute_readonly_query(count_sql, params)
        total = count_res[0]["total"] if count_res else 0

        items_sql = f"""
        {full_cte_query}
        SELECT * FROM IssueRecords {where_filter}
        ORDER BY record_id
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """
        items_res = execute_readonly_query(items_sql, params)

        items = [
            OrgQualityIssueRecord(
                record_id=r["record_id"],
                entity_type=r["entity_type"],
                entity_name=r["entity_name"],
                issue_code=r["issue_code"],
                issue_detail=r["issue_detail"],
            )
            for r in items_res
        ]

        return OrgQualityIssuesListResponse(
            issue_code=code,
            issue_name=code.replace("_", " ").title(),
            severity=IssueSeverity.WARNING,
            total=total,
            limit=limit,
            offset=offset,
            items=items,
        )

    # ══════════════════════════════════════════════════════════════════════════════
    # 7. EXPORTS
    # ══════════════════════════════════════════════════════════════════════════════

    async def export_org_units(
        self,
        unit_type: OrgUnitType | None = None,
        search: str | None = None,
        format: str = "csv",
    ) -> tuple[bytes, str, str]:
        """
        Exports all matching organizational units to CSV.
        """
        res = await self.get_org_units(
            unit_type=unit_type,
            search=search,
            limit=10000,
            offset=0,
        )
        type_str = unit_type.value.lower() if unit_type else "all_units"
        filename = f"organization_{type_str}_{format.lower()}"

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Unit ID",
                "Unit Type",
                "Unit Code",
                "Unit Name",
                "Parent Name",
                "Head / Leader",
                "Head Badge",
                "Active Headcount",
                "Active",
                "Deleted",
            ]
        )

        for item in res.items:
            writer.writerow(
                [
                    item.unit_id,
                    item.unit_type.value,
                    item.unit_code or "",
                    item.unit_name,
                    item.parent_name or "",
                    item.head_name or "",
                    item.head_code or "",
                    item.active_headcount,
                    "YES" if item.is_active else "NO",
                    "YES" if item.is_deleted else "NO",
                ]
            )

        csv_bytes = output.getvalue().encode("utf-8")
        return csv_bytes, "text/csv", f"{filename}.csv"

    async def export_org_quality_issues(
        self,
        issue_code: str,
        search: str | None = None,
        format: str = "csv",
    ) -> tuple[bytes, str, str]:
        """
        Exports flagged quality issue records to CSV.
        """
        res = await self.get_org_quality_issues(
            issue_code=issue_code,
            search=search,
            limit=10000,
            offset=0,
        )
        filename = f"org_quality_issue_{issue_code.lower()}"

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Record ID",
                "Entity Type",
                "Entity Name",
                "Issue Code",
                "Issue Detail",
            ]
        )

        for item in res.items:
            writer.writerow(
                [
                    item.record_id,
                    item.entity_type,
                    item.entity_name,
                    item.issue_code,
                    item.issue_detail,
                ]
            )

        csv_bytes = output.getvalue().encode("utf-8")
        return csv_bytes, "text/csv", f"{filename}.csv"
