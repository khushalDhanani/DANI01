import csv
import io
import logging
import re
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.procedure_logic.procedure_logic_schemas import (
    BusinessRuleConceptInfo,
    LogicInconsistenciesListResponse,
    LogicInconsistencyItem,
    ProcedureLogicOverviewResponse,
    SqlObjectDetailResponse,
    SqlObjectListResponse,
    SqlObjectMetadata,
)

logger = logging.getLogger(__name__)

BUSINESS_RULES_TAXONOMY = [
    {
        "code": "ACTIVE_EMPLOYEE",
        "name": "Active Employee Predicate",
        "category": "EMPLOYEE",
        "description": "SQL logic defining active workforce headcount and status.",
        "canonical": "WHERE EmpIsActive = 1 AND ISNULL(EmpIsDeleted, 0) = 0 AND (EmpResignDate IS NULL OR EmpResignDate > GETDATE())",
    },
    {
        "code": "OFFICIAL_ASSIGNMENT",
        "name": "Current Official Assignment",
        "category": "ORGANIZATION",
        "description": "SQL logic joining current department, designation, and location in EmployeeOfficialDet.",
        "canonical": "WHERE EmpOfficeDetIsActive = 1 AND ISNULL(EmpOfficeDetIsDeleted, 0) = 0 (Partitioned by ApplicableFrDate DESC)",
    },
    {
        "code": "REPORTING_LINE",
        "name": "Reporting Manager Hierarchy",
        "category": "ORGANIZATION",
        "description": "SQL logic joining reporting line managers in EmployeeReportingDet.",
        "canonical": "WHERE ReportingDetIsActive = 1 AND ISNULL(ReportingDetIsDeleted, 0) = 0 AND ReportingType = 'F'/'A'",
    },
    {
        "code": "SECURITY_LOGIN",
        "name": "Security Authentication Access",
        "category": "SECURITY",
        "description": "SQL logic validating user logins in SecurityUserMst.",
        "canonical": "WHERE UserIsActive = 1 AND ISNULL(UserIsDeleted, 0) = 0 AND UserEmpID = e.EmpID AND e.EmpIsActive = 1",
    },
    {
        "code": "ATTENDANCE_PUNCH",
        "name": "Time & Attendance Punches",
        "category": "ATTENDANCE",
        "description": "SQL logic joining daily punches and attendance records.",
        "canonical": "WHERE AttEmpID = e.EmpID AND e.EmpIsActive = 1 AND ISNULL(e.EmpIsDeleted, 0) = 0",
    },
    {
        "code": "LEAVE_APPLICATION",
        "name": "Leave Request & Balances",
        "category": "LEAVE",
        "description": "SQL logic querying leave applications and balances.",
        "canonical": "WHERE LeaveRequestByEmpID = e.EmpID AND ISNULL(LeaveCancel, 0) = 0 AND LeaveRequestIsDeleted = 0",
    },
    {
        "code": "PAYROLL_COMPUTATION",
        "name": "Payroll Salary Computation",
        "category": "PAYROLL",
        "description": "SQL logic computing monthly salary registers and net pay.",
        "canonical": "WHERE EarnedSalEmpID = e.EmpID AND ABS(NetPay - (TotalEarned - TotalDeduction)) <= 1.0",
    },
]


class ProcedureLogicService:
    """
    Centralized analyzer for Stored Procedures, Functions, Views, and Triggers in MSSQL.
    Extracts business logic predicates, detects logic discrepancies across procedures,
    and provides single-source-of-truth recommendations.
    """

    def _fetch_all_sql_objects(self) -> list[dict[str, Any]]:

        sql = """
        SELECT
            o.object_id,
            o.name AS object_name,
            o.type_desc AS object_type,
            m.definition
        FROM sys.objects o
        INNER JOIN sys.sql_modules m ON o.object_id = m.object_id
        WHERE o.type IN ('P', 'FN', 'IF', 'TF', 'V', 'TR')
          AND o.is_ms_shipped = 0
        ORDER BY o.name;
        """
        return execute_readonly_query(sql)

    def _clean_definition(self, definition: str) -> str:
        # Strip comments (-- and /* ... */)
        clean = re.sub(r"/\*.*?\*/", "", definition, flags=re.DOTALL)
        clean = re.sub(r"--.*$", "", clean, flags=re.MULTILINE)
        return clean

    def _analyze_single_object(self, r: dict[str, Any]) -> dict[str, Any]:
        obj_name = r["object_name"]
        obj_type = r["object_type"]
        raw_def = r["definition"] or ""
        clean_def = self._clean_definition(raw_def)

        emp_tables = [
            "EmployeeMst",
            "EmployeeOfficialDet",
            "EmployeeReportingDet",
            "SecurityUserMst",
            "PayAttendance",
            "PayPunchLog",
            "LeaveRequest",
            "PayEarnedSalary",
            "OrgDepartmentMst",
            "OrgDesignationMst",
            "OrgCompanyMst",
            "OrgLocationMst",
            "EmployeeFamilyDet",
            "EmployeeContactDet",
        ]

        used_tables = [
            t
            for t in emp_tables
            if re.search(r"\b" + re.escape(t) + r"\b", clean_def, re.IGNORECASE)
        ]

        dml_ops = ["SELECT"]
        if re.search(r"\bINSERT\s+INTO\b", clean_def, re.IGNORECASE):
            dml_ops.append("INSERT")
        if re.search(r"\bUPDATE\b\s+[\w\.\[\]]+\s+\bSET\b", clean_def, re.IGNORECASE):
            dml_ops.append("UPDATE")
        if re.search(r"\bDELETE\s+(FROM\b)?", clean_def, re.IGNORECASE):
            dml_ops.append("DELETE")
        if re.search(r"\bMERGE\s+INTO\b", clean_def, re.IGNORECASE):
            dml_ops.append("MERGE")

        joins_cnt = len(
            re.findall(r"\b(INNER|LEFT|RIGHT|FULL|CROSS)\s+JOIN\b", clean_def, re.IGNORECASE)
        )

        # Module classification
        related_module = "EMPLOYEE"
        if any(t in used_tables for t in ["PayAttendance", "PayPunchLog"]):
            related_module = "ATTENDANCE"
        elif any(t in used_tables for t in ["LeaveRequest"]):
            related_module = "LEAVE"
        elif any(t in used_tables for t in ["PayEarnedSalary"]):
            related_module = "PAYROLL"
        elif any(t in used_tables for t in ["SecurityUserMst"]):
            related_module = "SECURITY"
        elif any(
            t in used_tables for t in ["OrgDepartmentMst", "OrgDesignationMst", "OrgCompanyMst"]
        ):
            related_module = "ORGANIZATION"

        snippet_preview = clean_def[:220].replace("\n", " ").strip()

        return {
            "object_id": r["object_id"],
            "object_name": obj_name,
            "object_type": obj_type,
            "related_module": related_module,
            "used_tables": used_tables,
            "dml_operations": list(set(dml_ops)),
            "joins_count": joins_cnt,
            "has_active_emp_logic": "EmpIsActive" in clean_def,
            "has_active_deleted_logic": "EmpIsDeleted" in clean_def,
            "has_resign_logic": "EmpResignDate" in clean_def,
            "def_snippet": snippet_preview,
            "clean_def": clean_def,
            "raw_def": raw_def,
        }

    def get_procedure_logic_overview(self) -> ProcedureLogicOverviewResponse:
        raw_objects = self._fetch_all_sql_objects()
        emp_tables = [
            "EmployeeMst",
            "EmployeeOfficialDet",
            "EmployeeReportingDet",
            "SecurityUserMst",
            "PayAttendance",
            "LeaveRequest",
            "PayEarnedSalary",
        ]

        analyzed_list = []
        type_counts = {"P": 0, "FN": 0, "V": 0, "TR": 0}
        module_counts: dict[str, int] = {}

        for r in raw_objects:
            obj = self._analyze_single_object(r)
            if not obj["used_tables"]:
                continue
            analyzed_list.append(obj)

            ot = obj["object_type"]
            if "PROCEDURE" in ot:
                type_counts["P"] = type_counts.get("P", 0) + 1
            elif "FUNCTION" in ot:
                type_counts["FN"] = type_counts.get("FN", 0) + 1
            elif "VIEW" in ot:
                type_counts["V"] = type_counts.get("V", 0) + 1
            elif "TRIGGER" in ot:
                type_counts["TR"] = type_counts.get("TR", 0) + 1

            mod = obj["related_module"]
            module_counts[mod] = module_counts.get(mod, 0) + 1

        inconsistencies = self._detect_inconsistencies(analyzed_list)

        crit_cnt = sum(1 for i in inconsistencies if i.severity == "CRITICAL")
        warn_cnt = sum(1 for i in inconsistencies if i.severity == "WARNING")
        info_cnt = sum(1 for i in inconsistencies if i.severity == "INFO")

        # Business rules catalog
        rule_catalog = []
        for rdef in BUSINESS_RULES_TAXONOMY:
            code = rdef["code"]
            matching_objs = [o for o in analyzed_list if self._object_uses_rule(o, code)]
            matching_incons = [i for i in inconsistencies if i.rule_code == code]

            rule_catalog.append(
                BusinessRuleConceptInfo(
                    rule_code=code,
                    rule_name=rdef["name"],
                    category=rdef["category"],
                    description=rdef["description"],
                    canonical_recommendation=rdef["canonical"],
                    objects_count=len(matching_objs),
                    inconsistency_variants_count=len(matching_incons),
                )
            )

        return ProcedureLogicOverviewResponse(
            total_sql_objects=len(analyzed_list),
            total_stored_procedures=type_counts.get("P", 0),
            total_functions=type_counts.get("FN", 0),
            total_views=type_counts.get("V", 0),
            total_triggers=type_counts.get("TR", 0),
            total_inconsistencies=len(inconsistencies),
            critical_inconsistencies_count=crit_cnt,
            warning_inconsistencies_count=warn_cnt,
            info_inconsistencies_count=info_cnt,
            business_rules=rule_catalog,
            object_type_distribution=type_counts,
            module_distribution=module_counts,
        )

    def _object_uses_rule(self, obj: dict[str, Any], rule_code: str) -> bool:
        clean = obj["clean_def"]
        if rule_code == "ACTIVE_EMPLOYEE":
            return "EmpIsActive" in clean
        elif rule_code == "OFFICIAL_ASSIGNMENT":
            return "EmployeeOfficialDet" in clean
        elif rule_code == "REPORTING_LINE":
            return "EmployeeReportingDet" in clean
        elif rule_code == "SECURITY_LOGIN":
            return "SecurityUserMst" in clean
        elif rule_code == "ATTENDANCE_PUNCH":
            return "PayAttendance" in clean or "PayPunchLog" in clean
        elif rule_code == "LEAVE_APPLICATION":
            return "LeaveRequest" in clean
        elif rule_code == "PAYROLL_COMPUTATION":
            return "PayEarnedSalary" in clean
        return False

    def _detect_inconsistencies(
        self, analyzed_objects: list[dict[str, Any]]
    ) -> list[LogicInconsistencyItem]:
        inconsistencies: list[LogicInconsistencyItem] = []

        # 1. ACTIVE_EMPLOYEE Predicate Variants
        active_emp_objs = [o for o in analyzed_objects if "EmpIsActive" in o["clean_def"]]
        variant_groups: dict[str, list[str]] = {}

        for o in active_emp_objs:
            clean = o["clean_def"]
            lines = [l.strip() for l in clean.split("\n") if "EmpIsActive" in l]
            snip = " ".join(lines[:2])
            norm = re.sub(r"\s+", " ", snip).upper()
            if norm not in variant_groups:
                variant_groups[norm] = []
            variant_groups[norm].append(o["object_name"])

        canonical_active = "WHERE EmpIsActive = 1 AND ISNULL(EmpIsDeleted, 0) = 0 AND (EmpResignDate IS NULL OR EmpResignDate > GETDATE())"

        idx = 1
        for pred, objs in variant_groups.items():
            # Classify severity & risk
            if "EMPRESIGNDATE" not in pred and "EMPISDELETED" not in pred:
                sev = "CRITICAL"
                diff = "Predicate checks ONLY EmpIsActive=1, omitting soft-deleted flag (EmpIsDeleted=0) and historical resignation date (EmpResignDate > GETDATE())."
                risk = (
                    "High risk of reporting terminated/resigned staff in active headcount metrics."
                )
            elif "EMPRESIGNDATE" not in pred:
                sev = "WARNING"
                diff = "Predicate checks EmpIsActive=1 AND EmpIsDeleted=0, but omits resignation date comparison (EmpResignDate > GETDATE())."
                risk = "Risk of counting employees with historical resignation dates as active."
            else:
                sev = "INFO"
                diff = "Predicate includes active, deleted, and resignation filters with non-standard formatting."
                risk = "Minor formatting variation across stored procedures."

            inconsistencies.append(
                LogicInconsistencyItem(
                    inconsistency_id=f"INCONS-ACT-{idx}",
                    rule_code="ACTIVE_EMPLOYEE",
                    rule_name="Active Employee Predicate Conflict",
                    severity=sev,
                    confidence="CONFIRMED",
                    affected_objects_count=len(objs),
                    sample_objects=objs[:5],
                    predicate_used=pred[:150],
                    difference_analysis=diff,
                    business_risk=risk,
                    canonical_recommendation=canonical_active,
                )
            )
            idx += 1

        # 2. OFFICIAL_ASSIGNMENT Active Flags Conflict
        off_objs = [o for o in analyzed_objects if "EmployeeOfficialDet" in o["clean_def"]]
        missing_off_flags = [
            o["object_name"] for o in off_objs if "EmpOfficeDetIsActive" not in o["clean_def"]
        ]
        if missing_off_flags:
            inconsistencies.append(
                LogicInconsistencyItem(
                    inconsistency_id="INCONS-OFF-1",
                    rule_code="OFFICIAL_ASSIGNMENT",
                    rule_name="Missing EmployeeOfficialDet Active Status Filter",
                    severity="CRITICAL",
                    confidence="CONFIRMED",
                    affected_objects_count=len(missing_off_flags),
                    sample_objects=missing_off_flags[:5],
                    predicate_used="JOIN dbo.EmployeeOfficialDet o ON e.EmpID = o.EmpID (No EmpOfficeDetIsActive=1 check)",
                    difference_analysis="Query joins EmployeeOfficialDet without filtering EmpOfficeDetIsActive=1 AND EmpOfficeDetIsDeleted=0.",
                    business_risk="Returns historical or transferred department/designation postings alongside current posting.",
                    canonical_recommendation="WHERE EmpOfficeDetIsActive = 1 AND ISNULL(EmpOfficeDetIsDeleted, 0) = 0 (Partitioned by ApplicableFrDate DESC)",
                )
            )

        # 3. REPORTING_LINE Active Flags Conflict
        rep_objs = [o for o in analyzed_objects if "EmployeeReportingDet" in o["clean_def"]]
        missing_rep_flags = [
            o["object_name"] for o in rep_objs if "ReportingDetIsActive" not in o["clean_def"]
        ]
        if missing_rep_flags:
            inconsistencies.append(
                LogicInconsistencyItem(
                    inconsistency_id="INCONS-REP-1",
                    rule_code="REPORTING_LINE",
                    rule_name="Missing EmployeeReportingDet Active Status Filter",
                    severity="WARNING",
                    confidence="CONFIRMED",
                    affected_objects_count=len(missing_rep_flags),
                    sample_objects=missing_rep_flags[:5],
                    predicate_used="JOIN dbo.EmployeeReportingDet r ON e.EmpID = r.EmpID (No ReportingDetIsActive=1 check)",
                    difference_analysis="Query joins EmployeeReportingDet without filtering ReportingDetIsActive=1.",
                    business_risk="Returns obsolete reporting managers alongside active reporting line.",
                    canonical_recommendation="WHERE ReportingDetIsActive = 1 AND ISNULL(ReportingDetIsDeleted, 0) = 0",
                )
            )

        # 4. SECURITY_LOGIN Active Employee Check
        sec_objs = [o for o in analyzed_objects if "SecurityUserMst" in o["clean_def"]]
        missing_sec_emp = [
            o["object_name"] for o in sec_objs if "EmpIsActive" not in o["clean_def"]
        ]
        if missing_sec_emp:
            inconsistencies.append(
                LogicInconsistencyItem(
                    inconsistency_id="INCONS-SEC-1",
                    rule_code="SECURITY_LOGIN",
                    rule_name="Security Login Omits Employee Active Status Check",
                    severity="CRITICAL",
                    confidence="CONFIRMED",
                    affected_objects_count=len(missing_sec_emp),
                    sample_objects=missing_sec_emp[:5],
                    predicate_used="WHERE UserIsActive = 1 (No EmployeeMst.EmpIsActive check)",
                    difference_analysis="Security user query checks UserIsActive=1 but fails to verify if linked Employee is active/resigned.",
                    business_risk="Terminated or resigned employees retain active security login permissions.",
                    canonical_recommendation="WHERE UserIsActive = 1 AND ISNULL(UserIsDeleted, 0) = 0 AND e.EmpIsActive = 1 AND (e.EmpResignDate IS NULL OR e.EmpResignDate > GETDATE())",
                )
            )

        return inconsistencies

    def get_sql_objects_catalog(
        self,
        object_type: str | None = None,
        module: str | None = None,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> SqlObjectListResponse:
        raw_objects = self._fetch_all_sql_objects()

        filtered: list[SqlObjectMetadata] = []

        for r in raw_objects:
            obj = self._analyze_single_object(r)
            if not obj["used_tables"]:
                continue

            if object_type and object_type.upper() not in obj["object_type"].upper():
                continue
            if module and module.upper() != obj["related_module"].upper():
                continue
            if search and search.strip():
                s = search.strip().lower()
                if (
                    s not in obj["object_name"].lower()
                    and s not in obj["related_module"].lower()
                    and not any(s in t.lower() for t in obj["used_tables"])
                ):
                    continue

            filtered.append(
                SqlObjectMetadata(
                    object_id=obj["object_id"],
                    object_name=obj["object_name"],
                    object_type=obj["object_type"],
                    related_module=obj["related_module"],
                    used_tables=obj["used_tables"],
                    dml_operations=obj["dml_operations"],
                    joins_count=obj["joins_count"],
                    has_active_emp_logic=obj["has_active_emp_logic"],
                    has_active_deleted_logic=obj["has_active_deleted_logic"],
                    has_resign_logic=obj["has_resign_logic"],
                    def_snippet=obj["def_snippet"],
                )
            )

        total = len(filtered)
        paginated = filtered[offset : offset + limit]

        return SqlObjectListResponse(
            items=paginated,
            total=total,
            limit=limit,
            offset=offset,
            object_type=object_type,
            module=module,
            search=search,
        )

    def get_inconsistencies(
        self,
        severity: str | None = None,
        rule_code: str | None = None,
        search: str | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> LogicInconsistenciesListResponse:
        overview = self.get_procedure_logic_overview()
        raw_objects = self._fetch_all_sql_objects()
        analyzed_list = [self._analyze_single_object(r) for r in raw_objects]
        analyzed_list = [o for o in analyzed_list if o["used_tables"]]

        all_inconsistencies = self._detect_inconsistencies(analyzed_list)

        filtered = []
        for item in all_inconsistencies:
            if severity and severity.upper() != item.severity.upper():
                continue
            if rule_code and rule_code.upper() != item.rule_code.upper():
                continue
            if search and search.strip():
                s = search.strip().lower()
                if (
                    s not in item.rule_name.lower()
                    and s not in item.predicate_used.lower()
                    and s not in item.difference_analysis.lower()
                    and not any(s in obj.lower() for obj in item.sample_objects)
                ):
                    continue
            filtered.append(item)

        total = len(filtered)
        paginated = filtered[offset : offset + limit]

        return LogicInconsistenciesListResponse(
            items=paginated,
            total=total,
            limit=limit,
            offset=offset,
            severity=severity,
            rule_code=rule_code,
            search=search,
        )

    def get_sql_object_detail(self, object_id: int) -> SqlObjectDetailResponse | None:
        sql = """
        SELECT
            o.object_id,
            o.name AS object_name,
            o.type_desc AS object_type,
            m.definition
        FROM sys.objects o
        INNER JOIN sys.sql_modules m ON o.object_id = m.object_id
        WHERE o.object_id = :object_id;
        """
        rows = execute_readonly_query(sql, {"object_id": object_id})
        if not rows:
            return None

        obj = self._analyze_single_object(rows[0])
        overview = self.get_procedure_logic_overview()
        raw_objects = self._fetch_all_sql_objects()
        analyzed_list = [self._analyze_single_object(r) for r in raw_objects]
        analyzed_list = [o for o in analyzed_list if o["used_tables"]]
        all_incons = self._detect_inconsistencies(analyzed_list)

        rel_incons = [i for i in all_incons if obj["object_name"] in i.sample_objects]

        return SqlObjectDetailResponse(
            object_id=obj["object_id"],
            object_name=obj["object_name"],
            object_type=obj["object_type"],
            definition=obj["raw_def"],
            used_tables=obj["used_tables"],
            dml_operations=obj["dml_operations"],
            inconsistencies=rel_incons,
        )

    def download_inconsistencies_export(
        self,
        severity: str | None = None,
        rule_code: str | None = None,
        search: str | None = None,
    ) -> bytes:
        incons_resp = self.get_inconsistencies(
            severity=severity,
            rule_code=rule_code,
            search=search,
            limit=10000,
            offset=0,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Inconsistency ID",
                "Business Rule Code",
                "Business Rule Name",
                "Severity",
                "Confidence",
                "Affected Objects Count",
                "Sample Objects",
                "Predicate Used",
                "Difference Analysis",
                "Business Risk",
                "Canonical Recommendation",
            ]
        )

        for item in incons_resp.items:
            writer.writerow(
                [
                    item.inconsistency_id,
                    item.rule_code,
                    item.rule_name,
                    item.severity,
                    item.confidence,
                    item.affected_objects_count,
                    "; ".join(item.sample_objects),
                    item.predicate_used,
                    item.difference_analysis,
                    item.business_risk,
                    item.canonical_recommendation,
                ]
            )

        return output.getvalue().encode("utf-8")
