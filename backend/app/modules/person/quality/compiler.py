"""
compiler.py

Generic SQL query compiler for Daylite Person Quality rules.
Dynamically compiles summary aggregations, drilldowns, and duplicate anomaly clusters.
"""

from typing import Any

from app.modules.person.quality.common import (
    ACTIVE_PERSON_WHERE_SQL,
    CLASSIFIED_CONTACTS_CTE_SQL,
    PERSON_NAME_SQL,
)
from app.modules.person.quality.models import (
    ContactQualityIssueType,
    IssueCountUnit,
    QualityRule,
)
from app.modules.person.quality.registry import QUALITY_RULES_REGISTRY


def resolve_order_clause(
    sort_by: str = "PersonID",
    sort_order: str = "desc",
    default_clause: str = "p.PersonID DESC",
) -> str:
    direction = "ASC" if sort_order.lower().strip() == "asc" else "DESC"
    col = sort_by.lower().strip()

    if col in ("personid", "id"):
        return f"p.PersonID {direction}"
    elif col in ("personname", "name"):
        return (
            f"ISNULL(p.PersonFirstName, '') {direction}, ISNULL(p.PersonLastName, '') {direction}"
        )
    elif col in ("currentvalue", "value"):
        return f"CurrentValue {direction}, p.PersonID {direction}"
    return default_clause


def compile_summary_query() -> str:
    """
    Dynamically generates the 37-rule master summary query CTE and subquery expressions.
    Includes COUNT(DISTINCT PersonID) evaluation for Critical, Warning, and Any-Defect profiles.
    """
    rule_subqueries: list[str] = []
    crit_clauses: list[str] = []
    warn_clauses: list[str] = []

    for rule in QUALITY_RULES_REGISTRY.values():
        field_name = rule.summary_field
        pred = rule.predicate_sql

        if rule.count_unit == IssueCountUnit.DUPLICATE_GROUP:
            if rule.target_entity == "CONTACT":
                if "HAVING COUNT(DISTINCT PersonID) > 1" in pred:
                    # Shared across multiple persons -> group by offending value
                    subq = f"""
                    (SELECT COUNT_BIG(1) FROM (
                        SELECT {rule.value_expr_sql} AS GroupVal
                        FROM ClassifiedContacts c
                        WHERE {pred}
                        GROUP BY {rule.value_expr_sql}
                    ) t) AS {field_name}
                    """.strip()
                else:
                    # Duplicate within same person -> group by (PersonID, value)
                    subq = f"""
                    (SELECT COUNT_BIG(1) FROM (
                        SELECT c.PersonID, {rule.value_expr_sql} AS GroupVal
                        FROM ClassifiedContacts c
                        WHERE {pred}
                        GROUP BY c.PersonID, {rule.value_expr_sql}
                    ) t) AS {field_name}
                    """.strip()
            elif rule.target_entity == "ADDRESS":
                subq = f"""
                (SELECT COUNT_BIG(1) FROM (
                    SELECT a.PersonID, LOWER(LTRIM(RTRIM(a.Street))) AS StrVal, ISNULL(LOWER(LTRIM(RTRIM(a.CityName))), '') AS CityVal
                    FROM dbo.DLPersonAddressDet a
                    JOIN dbo.DLPersonMst p ON p.PersonID = a.PersonID
                    WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
                    GROUP BY a.PersonID, LOWER(LTRIM(RTRIM(a.Street))), ISNULL(LOWER(LTRIM(RTRIM(a.CityName))), '')
                ) t) AS {field_name}
                """.strip()
            elif rule.target_entity == "COMPANY_LINK":
                subq = f"""
                (SELECT COUNT_BIG(1) FROM (
                    SELECT l.PersonID, l.DLCompID
                    FROM dbo.DLPersonCompanyLinkDet l
                    JOIN dbo.DLPersonMst p ON p.PersonID = l.PersonID
                    WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
                    GROUP BY l.PersonID, l.DLCompID
                ) t) AS {field_name}
                """.strip()
            elif rule.target_entity == "EXTRA_FIELD":
                subq = f"""
                (SELECT COUNT_BIG(1) FROM (
                    SELECT e.PersonID, e.ExtraFieldID
                    FROM dbo.DLPersonExtraFieldValueDet e
                    JOIN dbo.DLPersonMst p ON p.PersonID = e.PersonID
                    WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
                    GROUP BY e.PersonID, e.ExtraFieldID
                ) t) AS {field_name}
                """.strip()
            else:
                subq = f"(SELECT 0) AS {field_name}"
        elif rule.target_entity == "CONTACT":
            if rule.code == ContactQualityIssueType.MULTIPLE_PRIMARY:
                subq = f"""
                (SELECT COUNT_BIG(1) FROM (
                    SELECT c.PersonID
                    FROM ClassifiedContacts c
                    WHERE c.IsPrimary = 1
                    GROUP BY c.PersonID
                    HAVING COUNT_BIG(1) > 1
                ) t) AS {field_name}
                """.strip()
            else:
                subq = f"""
                (SELECT COUNT_BIG(1) FROM ClassifiedContacts c WHERE {pred}) AS {field_name}
                """.strip()
        elif rule.target_entity == "ADDRESS":
            subq = f"""
            (SELECT COUNT_BIG(1) FROM dbo.DLPersonAddressDet a JOIN dbo.DLPersonMst p ON p.PersonID = a.PersonID WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}) AS {field_name}
            """.strip()
        elif rule.target_entity == "COMPANY_LINK":
            subq = f"""
            (SELECT COUNT_BIG(1) FROM dbo.DLPersonCompanyLinkDet l JOIN dbo.DLPersonMst p ON l.PersonID = p.PersonID WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}) AS {field_name}
            """.strip()
        elif rule.target_entity == "EXTRA_FIELD":
            subq = f"""
            (SELECT COUNT_BIG(1) FROM dbo.DLPersonExtraFieldValueDet e JOIN dbo.DLPersonMst p ON e.PersonID = p.PersonID WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}) AS {field_name}
            """.strip()
        else:  # PERSON
            active_clause = (
                f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}"
                if rule.requires_active_person
                else f"WHERE {pred}"
            )
            subq = f"""
            (SELECT COUNT_BIG(1) FROM dbo.DLPersonMst p {active_clause}) AS {field_name}
            """.strip()

        rule_subqueries.append(subq)

        # Build high-performance UNION subquery for Critical and Warning persons CTEs
        if rule.target_entity == "CONTACT":
            if rule.code == ContactQualityIssueType.DUPLICATE_EMAIL_CROSS:
                defect_select = "SELECT c.PersonID FROM ClassifiedContacts c JOIN DuplicateEmailsCross dup ON c.NormalizedEmail = dup.NormalizedEmail WHERE c.ContactCategory = 'EMAIL'"
            elif rule.code == ContactQualityIssueType.DUPLICATE_PHONE_CROSS:
                defect_select = "SELECT c.PersonID FROM ClassifiedContacts c JOIN DuplicatePhonesCross dup ON c.NormalizedPhone = dup.NormalizedPhone WHERE c.ContactCategory = 'PHONE'"
            else:
                defect_select = f"SELECT c.PersonID FROM ClassifiedContacts c WHERE {pred}"
        elif rule.target_entity == "ADDRESS":
            defect_select = f"SELECT a.PersonID FROM dbo.DLPersonAddressDet a JOIN dbo.DLPersonMst p ON a.PersonID = p.PersonID WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}"
        elif rule.target_entity == "COMPANY_LINK":
            defect_select = f"SELECT l.PersonID FROM dbo.DLPersonCompanyLinkDet l JOIN dbo.DLPersonMst p ON l.PersonID = p.PersonID WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}"
        elif rule.target_entity == "EXTRA_FIELD":
            defect_select = f"SELECT e.PersonID FROM dbo.DLPersonExtraFieldValueDet e JOIN dbo.DLPersonMst p ON e.PersonID = p.PersonID WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}"
        else:  # PERSON
            if (
                "NOT EXISTS (SELECT 1 FROM ClassifiedContacts c WHERE c.PersonID = p.PersonID AND c.ContactCategory = 'EMAIL'"
                in pred
            ):
                defect_select = f"SELECT p.PersonID FROM dbo.DLPersonMst p WHERE {ACTIVE_PERSON_WHERE_SQL} AND p.PersonID NOT IN (SELECT PersonID FROM ClassifiedContacts WHERE ContactCategory = 'EMAIL' AND TypeValue IS NOT NULL AND LTRIM(RTRIM(TypeValue)) <> '')"
            elif (
                "NOT EXISTS (SELECT 1 FROM ClassifiedContacts c WHERE c.PersonID = p.PersonID AND c.ContactCategory = 'PHONE'"
                in pred
            ):
                defect_select = f"SELECT p.PersonID FROM dbo.DLPersonMst p WHERE {ACTIVE_PERSON_WHERE_SQL} AND p.PersonID NOT IN (SELECT PersonID FROM ClassifiedContacts WHERE ContactCategory = 'PHONE' AND TypeValue IS NOT NULL AND LTRIM(RTRIM(TypeValue)) <> '')"
            else:
                active_clause = (
                    f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}"
                    if rule.requires_active_person
                    else f"WHERE {pred}"
                )
                defect_select = f"SELECT p.PersonID FROM dbo.DLPersonMst p {active_clause}"

        if rule.severity == "CRITICAL":
            crit_clauses.append(defect_select)
        elif rule.severity == "WARNING":
            warn_clauses.append(defect_select)

    projections = ",\n            ".join(rule_subqueries)
    crit_union = "\n        UNION\n        ".join(crit_clauses)
    warn_union = "\n        UNION\n        ".join(warn_clauses)

    return f"""
    {CLASSIFIED_CONTACTS_CTE_SQL},
    DuplicateEmailsCross AS (
        SELECT NormalizedEmail
        FROM ClassifiedContacts
        WHERE ContactCategory = 'EMAIL' AND TypeValue IS NOT NULL AND LTRIM(RTRIM(TypeValue)) <> ''
        GROUP BY NormalizedEmail
        HAVING COUNT(DISTINCT PersonID) > 1
    ),
    DuplicatePhonesCross AS (
        SELECT NormalizedPhone
        FROM ClassifiedContacts
        WHERE ContactCategory = 'PHONE' AND TypeValue IS NOT NULL AND LTRIM(RTRIM(TypeValue)) <> ''
        GROUP BY NormalizedPhone
        HAVING COUNT(DISTINCT PersonID) > 1
    ),
    CriticalPersons AS (
        {crit_union}
    ),
    WarningPersons AS (
        {warn_union}
    ),
    AllDefectPersons AS (
        SELECT PersonID FROM CriticalPersons
        UNION
        SELECT PersonID FROM WarningPersons
    )
    SELECT
        (SELECT COUNT_BIG(1) FROM dbo.DLPersonMst p WHERE {ACTIVE_PERSON_WHERE_SQL}) AS total_persons_evaluated,
        (SELECT COUNT_BIG(1) FROM dbo.DLPersonMst p WHERE p.PersonIsActive = 0 AND ISNULL(p.PersonIsDeleted, 0) = 0) AS total_inactive_persons,
        (SELECT COUNT_BIG(1) FROM dbo.DLPersonMst p WHERE p.PersonIsDeleted = 1) AS total_deleted_persons,
        (SELECT COUNT_BIG(1) FROM CriticalPersons) AS persons_with_critical_issues,
        (SELECT COUNT_BIG(1) FROM WarningPersons) AS persons_with_warning_issues,
        (SELECT COUNT_BIG(1) FROM AllDefectPersons) AS persons_with_any_issue,
        {projections};
    """


# =====================================================================
# Parallel Query Compilers (Performance Optimization)
# =====================================================================


def _build_defect_select(rule: "QualityRule") -> str:
    """
    Builds a SELECT PersonID statement for a single rule.
    Used to construct CriticalPersons/WarningPersons UNION chains.
    """
    pred = rule.predicate_sql

    if rule.target_entity == "CONTACT":
        if rule.code == ContactQualityIssueType.DUPLICATE_EMAIL_CROSS:
            return (
                "SELECT c.PersonID FROM ClassifiedContacts c "
                "JOIN DuplicateEmailsCross dup ON c.NormalizedEmail = dup.NormalizedEmail "
                "WHERE c.ContactCategory = 'EMAIL'"
            )
        elif rule.code == ContactQualityIssueType.DUPLICATE_PHONE_CROSS:
            return (
                "SELECT c.PersonID FROM ClassifiedContacts c "
                "JOIN DuplicatePhonesCross dup ON c.NormalizedPhone = dup.NormalizedPhone "
                "WHERE c.ContactCategory = 'PHONE'"
            )
        else:
            return f"SELECT c.PersonID FROM ClassifiedContacts c WHERE {pred}"
    elif rule.target_entity == "ADDRESS":
        return (
            f"SELECT a.PersonID FROM dbo.DLPersonAddressDet a "
            f"JOIN dbo.DLPersonMst p ON a.PersonID = p.PersonID "
            f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}"
        )
    elif rule.target_entity == "COMPANY_LINK":
        return (
            f"SELECT l.PersonID FROM dbo.DLPersonCompanyLinkDet l "
            f"JOIN dbo.DLPersonMst p ON l.PersonID = p.PersonID "
            f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}"
        )
    elif rule.target_entity == "EXTRA_FIELD":
        return (
            f"SELECT e.PersonID FROM dbo.DLPersonExtraFieldValueDet e "
            f"JOIN dbo.DLPersonMst p ON e.PersonID = p.PersonID "
            f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}"
        )
    else:  # PERSON
        if (
            "NOT EXISTS (SELECT 1 FROM ClassifiedContacts c "
            "WHERE c.PersonID = p.PersonID AND c.ContactCategory = 'EMAIL'"
        ) in pred:
            return (
                f"SELECT p.PersonID FROM dbo.DLPersonMst p "
                f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND p.PersonID NOT IN "
                f"(SELECT PersonID FROM ClassifiedContacts "
                f"WHERE ContactCategory = 'EMAIL' AND TypeValue IS NOT NULL "
                f"AND LTRIM(RTRIM(TypeValue)) <> '')"
            )
        elif (
            "NOT EXISTS (SELECT 1 FROM ClassifiedContacts c "
            "WHERE c.PersonID = p.PersonID AND c.ContactCategory = 'PHONE'"
        ) in pred:
            return (
                f"SELECT p.PersonID FROM dbo.DLPersonMst p "
                f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND p.PersonID NOT IN "
                f"(SELECT PersonID FROM ClassifiedContacts "
                f"WHERE ContactCategory = 'PHONE' AND TypeValue IS NOT NULL "
                f"AND LTRIM(RTRIM(TypeValue)) <> '')"
            )
        else:
            active_clause = (
                f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}"
                if rule.requires_active_person
                else f"WHERE {pred}"
            )
            return f"SELECT p.PersonID FROM dbo.DLPersonMst p {active_clause}"


def compile_base_counts_query() -> str:
    """
    Query 1: Base person population counts (no CTE, trivial).
    Returns total_persons_evaluated, total_inactive_persons, total_deleted_persons.
    """
    return f"""
    SELECT
        (SELECT COUNT_BIG(1) FROM dbo.DLPersonMst p WHERE {ACTIVE_PERSON_WHERE_SQL}) AS total_persons_evaluated,
        (SELECT COUNT_BIG(1) FROM dbo.DLPersonMst p WHERE p.PersonIsActive = 0 AND (p.PersonIsDeleted = 0 OR p.PersonIsDeleted IS NULL)) AS total_inactive_persons,
        (SELECT COUNT_BIG(1) FROM dbo.DLPersonMst p WHERE p.PersonIsDeleted = 1) AS total_deleted_persons;
    """


def compile_contact_rules_query() -> str:
    """
    Query 2: All CONTACT-entity rules.
    Uses conditional aggregation (SUM CASE WHEN) for simple count rules to scan
    the ClassifiedContacts CTE exactly ONCE. GROUP BY rules remain as scalar subqueries.
    """
    cond_agg_cases: list[str] = []
    scalar_subqueries: list[str] = []

    for rule in QUALITY_RULES_REGISTRY.values():
        if rule.target_entity != "CONTACT":
            continue

        fn = rule.summary_field
        pred = rule.predicate_sql

        if rule.count_unit == IssueCountUnit.DUPLICATE_GROUP:
            if "HAVING COUNT(DISTINCT PersonID) > 1" in pred:
                scalar_subqueries.append(
                    f"(SELECT COUNT_BIG(1) FROM ("
                    f"SELECT {rule.value_expr_sql} AS GroupVal "
                    f"FROM ClassifiedContacts c "
                    f"WHERE {pred} "
                    f"GROUP BY {rule.value_expr_sql}"
                    f") t) AS {fn}"
                )
            else:
                scalar_subqueries.append(
                    f"(SELECT COUNT_BIG(1) FROM ("
                    f"SELECT c.PersonID, {rule.value_expr_sql} AS GroupVal "
                    f"FROM ClassifiedContacts c "
                    f"WHERE {pred} "
                    f"GROUP BY c.PersonID, {rule.value_expr_sql}"
                    f") t) AS {fn}"
                )
        elif rule.code == ContactQualityIssueType.MULTIPLE_PRIMARY:
            scalar_subqueries.append(
                f"(SELECT COUNT_BIG(1) FROM ("
                f"SELECT c.PersonID "
                f"FROM ClassifiedContacts c "
                f"WHERE c.IsPrimary = 1 "
                f"GROUP BY c.PersonID "
                f"HAVING COUNT_BIG(1) > 1"
                f") t) AS {fn}"
            )
        else:
            cond_agg_cases.append(f"ISNULL(SUM(CASE WHEN {pred} THEN 1 ELSE 0 END), 0) AS {fn}")

    all_cols = cond_agg_cases + scalar_subqueries
    projections = ",\n            ".join(all_cols)

    if cond_agg_cases:
        return f"""
    {CLASSIFIED_CONTACTS_CTE_SQL}
    SELECT
            {projections}
    FROM ClassifiedContacts c;
        """
    else:
        return f"""
    {CLASSIFIED_CONTACTS_CTE_SQL}
    SELECT
            {projections};
        """


def compile_address_rules_query() -> str:
    """
    Query 3: All ADDRESS-entity rules.
    Uses conditional aggregation for simple counts against DLPersonAddressDet.
    DUPLICATE_GROUP rules remain as scalar subqueries.
    """
    cond_agg_cases: list[str] = []
    scalar_subqueries: list[str] = []

    for rule in QUALITY_RULES_REGISTRY.values():
        if rule.target_entity != "ADDRESS":
            continue

        fn = rule.summary_field
        pred = rule.predicate_sql

        if rule.count_unit == IssueCountUnit.DUPLICATE_GROUP:
            scalar_subqueries.append(
                f"(SELECT COUNT_BIG(1) FROM ("
                f"SELECT a.PersonID, LOWER(LTRIM(RTRIM(a.Street))) AS StrVal, "
                f"ISNULL(LOWER(LTRIM(RTRIM(a.CityName))), '') AS CityVal "
                f"FROM dbo.DLPersonAddressDet a "
                f"JOIN dbo.DLPersonMst p ON p.PersonID = a.PersonID "
                f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred} "
                f"GROUP BY a.PersonID, LOWER(LTRIM(RTRIM(a.Street))), "
                f"ISNULL(LOWER(LTRIM(RTRIM(a.CityName))), '')"
                f") t) AS {fn}"
            )
        else:
            cond_agg_cases.append(f"ISNULL(SUM(CASE WHEN {pred} THEN 1 ELSE 0 END), 0) AS {fn}")

    all_cols = cond_agg_cases + scalar_subqueries
    projections = ",\n            ".join(all_cols)

    return f"""
    SELECT
            {projections}
    FROM dbo.DLPersonAddressDet a
    JOIN dbo.DLPersonMst p ON p.PersonID = a.PersonID
    WHERE {ACTIVE_PERSON_WHERE_SQL};
    """


def compile_person_rules_query() -> str:
    """
    Query 4: All PERSON-entity rules using conditional aggregation.
    Scans DLPersonMst once. Active-only rules have the active guard embedded
    in the CASE WHEN expression. Includes ClassifiedContacts CTE only when
    MISSING_EMAIL / MISSING_PHONE rules require it.
    """
    needs_cte = False
    case_expressions: list[str] = []
    scalar_subqueries: list[str] = []

    for rule in QUALITY_RULES_REGISTRY.values():
        if rule.target_entity != "PERSON":
            continue

        fn = rule.summary_field
        pred = rule.predicate_sql

        if "ClassifiedContacts" in pred or "EXISTS" in pred.upper():
            needs_cte = True
            if rule.requires_active_person:
                scalar_subqueries.append(
                    f"(SELECT COUNT_BIG(1) FROM dbo.DLPersonMst p "
                    f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND ({pred})) AS {fn}"
                )
            else:
                scalar_subqueries.append(
                    f"(SELECT COUNT_BIG(1) FROM dbo.DLPersonMst p WHERE {pred}) AS {fn}"
                )
        else:
            if rule.requires_active_person:
                case_expressions.append(
                    f"ISNULL(SUM(CASE WHEN {ACTIVE_PERSON_WHERE_SQL} "
                    f"AND ({pred}) THEN 1 ELSE 0 END), 0) AS {fn}"
                )
            else:
                case_expressions.append(
                    f"ISNULL(SUM(CASE WHEN {pred} THEN 1 ELSE 0 END), 0) AS {fn}"
                )

    all_cols = case_expressions + scalar_subqueries
    projections = ",\n            ".join(all_cols)
    cte_prefix = f"{CLASSIFIED_CONTACTS_CTE_SQL}\n    " if needs_cte else ""

    return f"""
    {cte_prefix}SELECT
            {projections}
    FROM dbo.DLPersonMst p;
    """


def compile_entity_link_rules_query() -> str:
    """
    Query 5: COMPANY_LINK and EXTRA_FIELD entity rules as scalar subqueries.
    These tables are typically small, so scalar subqueries are sufficient.
    """
    subqueries: list[str] = []

    for rule in QUALITY_RULES_REGISTRY.values():
        fn = rule.summary_field
        pred = rule.predicate_sql

        if rule.target_entity == "COMPANY_LINK":
            if rule.count_unit == IssueCountUnit.DUPLICATE_GROUP:
                subqueries.append(
                    f"(SELECT COUNT_BIG(1) FROM ("
                    f"SELECT l.PersonID, l.DLCompID "
                    f"FROM dbo.DLPersonCompanyLinkDet l "
                    f"JOIN dbo.DLPersonMst p ON p.PersonID = l.PersonID "
                    f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred} "
                    f"GROUP BY l.PersonID, l.DLCompID"
                    f") t) AS {fn}"
                )
            else:
                subqueries.append(
                    f"(SELECT COUNT_BIG(1) FROM dbo.DLPersonCompanyLinkDet l "
                    f"JOIN dbo.DLPersonMst p ON l.PersonID = p.PersonID "
                    f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}) AS {fn}"
                )

        elif rule.target_entity == "EXTRA_FIELD":
            if rule.count_unit == IssueCountUnit.DUPLICATE_GROUP:
                subqueries.append(
                    f"(SELECT COUNT_BIG(1) FROM ("
                    f"SELECT e.PersonID, e.ExtraFieldID "
                    f"FROM dbo.DLPersonExtraFieldValueDet e "
                    f"JOIN dbo.DLPersonMst p ON p.PersonID = e.PersonID "
                    f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred} "
                    f"GROUP BY e.PersonID, e.ExtraFieldID"
                    f") t) AS {fn}"
                )
            else:
                subqueries.append(
                    f"(SELECT COUNT_BIG(1) FROM dbo.DLPersonExtraFieldValueDet e "
                    f"JOIN dbo.DLPersonMst p ON e.PersonID = p.PersonID "
                    f"WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}) AS {fn}"
                )

    if not subqueries:
        return "SELECT 0 AS _placeholder;"

    projections = ",\n            ".join(subqueries)
    return f"""
    SELECT
            {projections};
    """


def compile_defect_persons_query() -> str:
    """
    Query 6: Critical / Warning / Any defect person counts.
    Builds UNION chains of PersonID selects grouped by severity.
    """
    crit_clauses: list[str] = []
    warn_clauses: list[str] = []

    for rule in QUALITY_RULES_REGISTRY.values():
        defect_select = _build_defect_select(rule)

        if rule.severity == "CRITICAL":
            crit_clauses.append(defect_select)
        elif rule.severity == "WARNING":
            warn_clauses.append(defect_select)

    crit_union = (
        "\n        UNION\n        ".join(crit_clauses)
        if crit_clauses
        else "SELECT NULL AS PersonID WHERE 1=0"
    )
    warn_union = (
        "\n        UNION\n        ".join(warn_clauses)
        if warn_clauses
        else "SELECT NULL AS PersonID WHERE 1=0"
    )

    return f"""
    {CLASSIFIED_CONTACTS_CTE_SQL},
    DuplicateEmailsCross AS (
        SELECT NormalizedEmail
        FROM ClassifiedContacts
        WHERE ContactCategory = 'EMAIL' AND TypeValue IS NOT NULL AND LTRIM(RTRIM(TypeValue)) <> ''
        GROUP BY NormalizedEmail
        HAVING COUNT(DISTINCT PersonID) > 1
    ),
    DuplicatePhonesCross AS (
        SELECT NormalizedPhone
        FROM ClassifiedContacts
        WHERE ContactCategory = 'PHONE' AND TypeValue IS NOT NULL AND LTRIM(RTRIM(TypeValue)) <> ''
        GROUP BY NormalizedPhone
        HAVING COUNT(DISTINCT PersonID) > 1
    ),
    CriticalPersons AS (
        {crit_union}
    ),
    WarningPersons AS (
        {warn_union}
    ),
    AllDefectPersons AS (
        SELECT PersonID FROM CriticalPersons
        UNION
        SELECT PersonID FROM WarningPersons
    )
    SELECT
        (SELECT COUNT_BIG(1) FROM CriticalPersons) AS persons_with_critical_issues,
        (SELECT COUNT_BIG(1) FROM WarningPersons) AS persons_with_warning_issues,
        (SELECT COUNT_BIG(1) FROM AllDefectPersons) AS persons_with_any_issue;
    """


def compile_drilldown_queries(
    rule: QualityRule,
    search: str | None = None,
    sort_by: str = "PersonID",
    sort_order: str = "desc",
) -> tuple[str, str, dict[str, Any]]:
    """
    Generates count_sql and paginated items_sql for standard (non-group) drilldowns and exports
    using the canonical issue relation defined on the QualityRule.
    """
    params: dict[str, Any] = {}
    search_clause = ""

    if search and search.strip():
        term = f"%{search.strip()}%"
        params["search"] = term
        if rule.target_entity == "CONTACT":
            search_clause = """
            AND (
                CAST(p.PersonID AS VARCHAR(20)) LIKE :search
                OR p.PersonFirstName LIKE :search
                OR p.PersonLastName LIKE :search
                OR c.TypeValue LIKE :search
            )
            """
        else:
            search_clause = """
            AND (
                CAST(p.PersonID AS VARCHAR(20)) LIKE :search
                OR p.PersonFirstName LIKE :search
                OR p.PersonLastName LIKE :search
            )
            """

    cte_prefix = (
        f"{CLASSIFIED_CONTACTS_CTE_SQL}\n"
        if rule.target_entity == "CONTACT"
        or "ClassifiedContacts" in rule.where_clause_sql
        or "ClassifiedContacts" in rule.from_clause_sql
        else ""
    )
    order_by = resolve_order_clause(sort_by, sort_order)

    if rule.code == ContactQualityIssueType.MULTIPLE_PRIMARY:
        count_sql = f"""
        {CLASSIFIED_CONTACTS_CTE_SQL}
        SELECT COUNT_BIG(1) AS total FROM (
            SELECT c.PersonID
            FROM ClassifiedContacts c
            JOIN dbo.DLPersonMst p ON c.PersonID = p.PersonID
            WHERE c.IsPrimary = 1 {search_clause}
            GROUP BY c.PersonID
            HAVING COUNT(1) > 1
        ) t;
        """
    else:
        count_sql = f"""
        {cte_prefix}
        SELECT COUNT_BIG(1) AS total
        FROM {rule.from_clause_sql}
        WHERE {rule.where_clause_sql} {search_clause};
        """

    items_sql = f"""
    {cte_prefix}
    SELECT
        {rule.select_columns_sql}
    FROM {rule.from_clause_sql}
    WHERE {rule.where_clause_sql} {search_clause}
    ORDER BY {order_by}
    OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
    """

    return count_sql, items_sql, params


def compile_group_queries(
    rule: QualityRule,
    search: str | None = None,
    sort_by: str = "PersonID",
    sort_order: str = "desc",
) -> tuple[str, str, str, dict[str, Any]]:
    """
    Generates count_sql, groups_sql, and members_sql for DUPLICATE_GROUP master-detail drilldowns.
    """
    params: dict[str, Any] = {}
    search_clause_contact = ""
    search_clause_person = ""

    if search and search.strip():
        term = f"%{search.strip()}%"
        params["search"] = term
        search_clause_contact = "AND (c.NormalizedEmail LIKE :search OR c.NormalizedPhone LIKE :search OR CAST(c.PersonID AS VARCHAR(20)) LIKE :search)"
        search_clause_person = (
            "AND (a.Street LIKE :search OR CAST(a.PersonID AS VARCHAR(20)) LIKE :search)"
        )

    pred = rule.predicate_sql
    group_key = rule.group_key_sql or "c.NormalizedEmail"
    group_label = rule.group_label_sql or "c.NormalizedEmail"
    rec_count = rule.group_records_count_sql or "COUNT_BIG(1)"
    pers_count = rule.group_persons_count_sql or "COUNT(DISTINCT c.PersonID)"

    if rule.target_entity == "CONTACT":
        count_sql = f"""
        {CLASSIFIED_CONTACTS_CTE_SQL}
        SELECT COUNT_BIG(1) AS total FROM (
            SELECT {group_key} AS GroupKey
            FROM ClassifiedContacts c
            JOIN dbo.DLPersonMst p ON c.PersonID = p.PersonID
            WHERE {pred} {search_clause_contact}
            GROUP BY {group_key}
        ) t;
        """

        groups_sql = f"""
        {CLASSIFIED_CONTACTS_CTE_SQL}
        SELECT
            {group_key} AS GroupKey,
            MIN({group_label}) AS GroupLabel,
            {pers_count} AS AffectedPersonsCount,
            {rec_count} AS AffectedRecordsCount
        FROM ClassifiedContacts c
        JOIN dbo.DLPersonMst p ON c.PersonID = p.PersonID
        WHERE {pred} {search_clause_contact}
        GROUP BY {group_key}
        ORDER BY AffectedRecordsCount DESC, GroupKey ASC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """

        members_sql = f"""
        {CLASSIFIED_CONTACTS_CTE_SQL}
        SELECT
            {group_key} AS GroupKey,
            c.PersonID,
            {PERSON_NAME_SQL} AS PersonName,
            c.PersonPhoneID AS ContactID,
            c.ContactCategory AS ContactType,
            c.LabelName AS LabelName,
            c.TypeValue AS CurrentValue,
            '{rule.code.value}' AS IssueCode,
            '{rule.description}' AS IssueDescription,
            '{rule.severity}' AS Severity,
            c.IsVerified AS IsVerified,
            c.IsPrimary AS IsPrimary,
            p.PersonIsActive AS IsActive
        FROM ClassifiedContacts c
        JOIN dbo.DLPersonMst p ON c.PersonID = p.PersonID
        WHERE {pred}
          AND {group_key} IN (:group_keys)
        ORDER BY {group_key} ASC, c.PersonID ASC;
        """

    elif rule.target_entity == "ADDRESS":
        count_sql = f"""
        SELECT COUNT_BIG(1) AS total FROM (
            SELECT {group_key} AS GroupKey
            FROM dbo.DLPersonAddressDet a
            JOIN dbo.DLPersonMst p ON a.PersonID = p.PersonID
            WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred} {search_clause_person}
            GROUP BY {group_key}
        ) t;
        """

        groups_sql = f"""
        SELECT
            {group_key} AS GroupKey,
            MIN({group_label}) AS GroupLabel,
            {pers_count} AS AffectedPersonsCount,
            {rec_count} AS AffectedRecordsCount
        FROM dbo.DLPersonAddressDet a
        JOIN dbo.DLPersonMst p ON a.PersonID = p.PersonID
        WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred} {search_clause_person}
        GROUP BY {group_key}
        ORDER BY AffectedRecordsCount DESC, GroupKey ASC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """

        members_sql = f"""
        SELECT
            {group_key} AS GroupKey,
            a.PersonID,
            {PERSON_NAME_SQL} AS PersonName,
            a.PersonAddID AS ContactID,
            'ADDRESS' AS ContactType,
            a.AddressTypeName AS LabelName,
            a.Street AS CurrentValue,
            '{rule.code.value}' AS IssueCode,
            '{rule.description}' AS IssueDescription,
            '{rule.severity}' AS Severity,
            NULL AS IsVerified,
            NULL AS IsPrimary,
            p.PersonIsActive AS IsActive
        FROM dbo.DLPersonAddressDet a
        JOIN dbo.DLPersonMst p ON a.PersonID = p.PersonID
        WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
          AND {group_key} IN (:group_keys)
        ORDER BY {group_key} ASC, a.PersonID ASC;
        """

    elif rule.target_entity == "COMPANY_LINK":
        count_sql = f"""
        SELECT COUNT_BIG(1) AS total FROM (
            SELECT {group_key} AS GroupKey
            FROM dbo.DLPersonCompanyLinkDet l
            JOIN dbo.DLPersonMst p ON l.PersonID = p.PersonID
            WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
            GROUP BY {group_key}
        ) t;
        """

        groups_sql = f"""
        SELECT
            {group_key} AS GroupKey,
            MIN({group_label}) AS GroupLabel,
            {pers_count} AS AffectedPersonsCount,
            {rec_count} AS AffectedRecordsCount
        FROM dbo.DLPersonCompanyLinkDet l
        JOIN dbo.DLPersonMst p ON l.PersonID = p.PersonID
        WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
        GROUP BY {group_key}
        ORDER BY AffectedRecordsCount DESC, GroupKey ASC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """

        members_sql = f"""
        SELECT
            {group_key} AS GroupKey,
            l.PersonID,
            {PERSON_NAME_SQL} AS PersonName,
            l.PersonLinkID AS ContactID,
            'COMPANY_LINK' AS ContactType,
            'Company Link' AS LabelName,
            'Company #' + CAST(l.DLCompID AS VARCHAR(20)) AS CurrentValue,
            '{rule.code.value}' AS IssueCode,
            '{rule.description}' AS IssueDescription,
            '{rule.severity}' AS Severity,
            NULL AS IsVerified,
            NULL AS IsPrimary,
            p.PersonIsActive AS IsActive
        FROM dbo.DLPersonCompanyLinkDet l
        JOIN dbo.DLPersonMst p ON l.PersonID = p.PersonID
        WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
          AND {group_key} IN (:group_keys)
        ORDER BY {group_key} ASC, l.PersonID ASC;
        """

    else:  # EXTRA_FIELD
        count_sql = f"""
        SELECT COUNT_BIG(1) AS total FROM (
            SELECT {group_key} AS GroupKey
            FROM dbo.DLPersonExtraFieldValueDet e
            JOIN dbo.DLPersonMst p ON e.PersonID = p.PersonID
            WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
            GROUP BY {group_key}
        ) t;
        """

        groups_sql = f"""
        SELECT
            {group_key} AS GroupKey,
            MIN({group_label}) AS GroupLabel,
            {pers_count} AS AffectedPersonsCount,
            {rec_count} AS AffectedRecordsCount
        FROM dbo.DLPersonExtraFieldValueDet e
        JOIN dbo.DLPersonMst p ON e.PersonID = p.PersonID
        WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
        GROUP BY {group_key}
        ORDER BY AffectedRecordsCount DESC, GroupKey ASC
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """

        members_sql = f"""
        SELECT
            {group_key} AS GroupKey,
            e.PersonID,
            {PERSON_NAME_SQL} AS PersonName,
            e.PersonExtraFieldValueID AS ContactID,
            'CUSTOM_FIELD' AS ContactType,
            'Field ID ' + CAST(e.ExtraFieldID AS VARCHAR(20)) AS LabelName,
            e.ExtraFieldValue AS CurrentValue,
            '{rule.code.value}' AS IssueCode,
            '{rule.description}' AS IssueDescription,
            '{rule.severity}' AS Severity,
            NULL AS IsVerified,
            NULL AS IsPrimary,
            p.PersonIsActive AS IsActive
        FROM dbo.DLPersonExtraFieldValueDet e
        JOIN dbo.DLPersonMst p ON e.PersonID = p.PersonID
        WHERE {ACTIVE_PERSON_WHERE_SQL} AND {pred}
          AND {group_key} IN (:group_keys)
        ORDER BY {group_key} ASC, e.PersonID ASC;
        """

    return count_sql, groups_sql, members_sql, params


__all__ = [
    "PERSON_NAME_SQL",
    "compile_address_rules_query",
    "compile_base_counts_query",
    "compile_contact_rules_query",
    "compile_defect_persons_query",
    "compile_drilldown_queries",
    "compile_entity_link_rules_query",
    "compile_group_queries",
    "compile_person_rules_query",
    "compile_summary_query",
    "resolve_order_clause",
]
