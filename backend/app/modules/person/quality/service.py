"""
service.py

High-performance data quality engine for Daylite PERSON domain records.
Evaluates 37 comprehensive quality metrics, provides paginated drilldowns
with master-detail grouping for duplicate anomalies, and exports findings.
"""

import asyncio
import logging
import time
from datetime import UTC, datetime
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.person.quality.compiler import (
    PERSON_NAME_SQL,
    compile_address_rules_query,
    compile_base_counts_query,
    compile_contact_rules_query,
    compile_defect_persons_query,
    compile_drilldown_queries,
    compile_entity_link_rules_query,
    compile_group_queries,
    compile_person_rules_query,
    compile_summary_query,
    resolve_order_clause,
)
from app.modules.person.quality.exports import (
    export_issues_dataset,
    export_summary_report,
)
from app.modules.person.quality.models import (
    ContactQualityGroupItem,
    ContactQualityGroupMember,
    ContactQualityIssueItem,
    ContactQualityIssuesResponse,
    ContactQualityIssueType,
    ContactQualitySummaryResponse,
    IssueCountUnit,
    QualityRule,
)
from app.modules.person.quality.registry import (
    ACTIVE_EMP_MISSING_TITLE_WHERE_SQL,
    ACTIVE_PERSON_WHERE_SQL,
    ADDR_CITY_WITHOUT_STATE_WHERE_SQL,
    ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL,
    ADDR_INVALID_PIN_FORMAT_WHERE_SQL,
    ADDR_MISSING_GEOCODES_WHERE_SQL,
    ADDR_MISSING_POSTAL_CODE_WHERE_SQL,
    ADDR_STREET_WITHOUT_CITY_WHERE_SQL,
    AUDIT_DEL_BEFORE_ENT_WHERE_SQL,
    BLACKLIST_MISSING_DETAILS_WHERE_SQL,
    BLACKLIST_UNAPPROVED_WHERE_SQL,
    CLASSIFIED_CONTACTS_CTE_SQL,
    COMPANY_DUPLICATE_LINKS_WHERE_SQL,
    COMPANY_MISSING_ROLE_WHERE_SQL,
    COMPANY_ORPHAN_LINKS_WHERE_SQL,
    DELETED_MISSING_DEL_DATE_WHERE_SQL,
    DUPLICATE_EMAIL_CROSS_WHERE_SQL,
    DUPLICATE_EMAIL_SAME_WHERE_SQL,
    DUPLICATE_PHONE_CROSS_WHERE_SQL,
    DUPLICATE_PHONE_SAME_WHERE_SQL,
    EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL,
    EXTRA_FIELD_ORPHAN_ID_WHERE_SQL,
    INACTIVE_WITH_EMPID_WHERE_SQL,
    INVALID_EMAIL_WHERE_SQL,
    INVALID_PHONE_WHERE_SQL,
    INVALID_URL_WHERE_SQL,
    MULTIPLE_PRIMARY_WHERE_SQL,
    PERSON_ANNIVERSARY_BEFORE_BIRTH_WHERE_SQL,
    PERSON_BIRTH_DATE_ANCIENT_WHERE_SQL,
    PERSON_INVALID_BIRTH_DATE_WHERE_SQL,
    PERSON_MISSING_LASTNAME_ONLY_WHERE_SQL,
    PERSON_SUSPICIOUS_DUMMY_NAMES_WHERE_SQL,
    PRIMARY_INACTIVE_WHERE_SQL,
    QUALIFYING_EMAIL_EXISTS_SQL,
    QUALIFYING_PHONE_EXISTS_SQL,
    QUALITY_RULES_REGISTRY,
    STALE_TEMP_PERSONS_WHERE_SQL,
    STATUS_ACTIVE_AND_DELETED_WHERE_SQL,
    SYNC_ZIMBRA_MISSING_ID_WHERE_SQL,
    UNVERIFIED_CONTACT_WHERE_SQL,
    get_all_quality_rules,
    get_quality_rule,
)

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 300  # 5-minute memory cache for summary telemetry
MAX_PAGE_SIZE = 100
MAX_EXPORT_ROWS = 50000
EXPORT_BATCH_SIZE = 1000


# =====================================================================
# Backward Compatibility Query Builders
# =====================================================================


def _build_issue_queries(
    issue: str = "INVALID_EMAIL",
    search: str | None = None,
    sort_by: str = "PersonID",
    sort_order: str = "desc",
) -> tuple[str, str, dict[str, Any]]:
    rule = get_quality_rule(issue)
    if not rule:
        rule = QUALITY_RULES_REGISTRY[ContactQualityIssueType.INVALID_EMAIL]
    return compile_drilldown_queries(rule, search=search, sort_by=sort_by, sort_order=sort_order)


def _build_group_queries(
    issue: str = "DUPLICATE_EMAIL_CROSS",
    search: str | None = None,
    sort_by: str = "PersonID",
    sort_order: str = "desc",
) -> tuple[str, str, dict[str, Any]]:
    rule = get_quality_rule(issue)
    if not rule:
        rule = QUALITY_RULES_REGISTRY[ContactQualityIssueType.DUPLICATE_EMAIL_CROSS]
    count_sql, groups_sql, _, params = compile_group_queries(
        rule, search=search, sort_by=sort_by, sort_order=sort_order
    )
    return count_sql, groups_sql, params


def _execute_query(query: str, params: dict | None = None) -> list[dict[str, Any]]:
    try:
        from app.modules.person import contact_quality_service

        return contact_quality_service.execute_readonly_query(query, params=params)
    except Exception:
        return execute_readonly_query(query, params=params)


# =====================================================================
# Contact Quality Service
# =====================================================================


class ContactQualityService:
    """
    Quality analyzer and compliance reporting engine for Daylite PERSON records.
    Evaluates 37 canonical data validation rules against MSSQL with in-memory caching.
    """

    def __init__(self) -> None:
        self._summary_cache: ContactQualitySummaryResponse | None = None
        self._cache_timestamp: float = 0.0

    def _is_cache_valid(self) -> bool:
        return (
            self._summary_cache is not None
            and (time.time() - self._cache_timestamp) < CACHE_TTL_SECONDS
        )

    def invalidate_cache(self) -> None:
        self._summary_cache = None
        self._cache_timestamp = 0.0

    async def get_contact_quality_summary(
        self, force_refresh: bool = False
    ) -> ContactQualitySummaryResponse:
        """
        Executes 6 parallel entity-grouped quality queries via asyncio.gather().
        Each query targets a specific entity type, avoiding monolithic CTE re-evaluation.
        Caches result in memory for 5 minutes.
        """
        if not force_refresh and self._is_cache_valid():
            logger.info("Serving Contact Quality summary from memory cache.")
            return self._summary_cache  # type: ignore

        start_time = time.time()

        # Compile 6 parallel query groups
        base_sql = compile_base_counts_query()
        contact_sql = compile_contact_rules_query()
        address_sql = compile_address_rules_query()
        person_sql = compile_person_rules_query()
        entity_sql = compile_entity_link_rules_query()
        defect_sql = compile_defect_persons_query()

        # Execute all 6 queries in parallel
        try:
            base_r, contact_r, address_r, person_r, entity_r, defect_r = await asyncio.gather(
                asyncio.to_thread(_execute_query, base_sql),
                asyncio.to_thread(_execute_query, contact_sql),
                asyncio.to_thread(_execute_query, address_sql),
                asyncio.to_thread(_execute_query, person_sql),
                asyncio.to_thread(_execute_query, entity_sql),
                asyncio.to_thread(_execute_query, defect_sql),
            )
        except Exception as e:
            logger.error("Failed to execute Contact Quality summary queries: %s", e)
            raise

        # Merge results from all 6 query groups into a single row dict
        row: dict[str, Any] = {}
        for result_set in [base_r, contact_r, address_r, person_r, entity_r, defect_r]:
            if result_set:
                row.update(result_set[0])

        # Dynamically map all 37 rule counts from registry
        metric_values: dict[str, int] = {}
        total_crit_findings = 0
        total_warn_findings = 0
        total_info_findings = 0

        for rule in QUALITY_RULES_REGISTRY.values():
            val = int(row.get(rule.summary_field) or 0)
            metric_values[rule.summary_field] = val
            if rule.severity == "CRITICAL":
                total_crit_findings += val
            elif rule.severity == "WARNING":
                total_warn_findings += val
            elif rule.severity == "INFO":
                total_info_findings += val

        tot_eval = int(row.get("total_persons_evaluated") or 0)
        tot_inact = int(row.get("total_inactive_persons") or 0)
        tot_del = int(row.get("total_deleted_persons") or 0)

        # Entity-level distinct defect counts
        pers_crit = int(row.get("persons_with_critical_issues") or 0)
        pers_warn = int(row.get("persons_with_warning_issues") or 0)
        pers_any = int(row.get("persons_with_any_issue") or 0)

        clean_persons = max(0, tot_eval - pers_any)
        health_pct = round((clean_persons / tot_eval * 100.0), 2) if tot_eval > 0 else 100.0

        duration_ms = (time.time() - start_time) * 1000.0

        summary = ContactQualitySummaryResponse(
            **metric_values,
            total_persons_evaluated=tot_eval,
            total_inactive_persons=tot_inact,
            total_deleted_persons=tot_del,
            related_tables_checked=8,
            calculated_at=datetime.now(UTC).isoformat(),
            duration_ms=round(duration_ms, 2),
            persons_with_critical_issues=pers_crit,
            persons_with_warning_issues=pers_warn,
            persons_with_any_issue=pers_any,
            total_clean_persons=clean_persons,
            health_score_pct=health_pct,
            total_critical_findings=total_crit_findings,
            total_warning_findings=total_warn_findings,
            total_info_findings=total_info_findings,
        )

        self._summary_cache = summary
        self._cache_timestamp = time.time()
        return summary

    async def _get_issue_count(self, rule: QualityRule, search: str | None = None) -> int:
        if rule.count_unit == IssueCountUnit.DUPLICATE_GROUP:
            count_sql, _, _, params = compile_group_queries(rule, search=search)
        else:
            count_sql, _, params = compile_drilldown_queries(rule, search=search)

        try:
            res = await asyncio.to_thread(_execute_query, count_sql, params)
            return int(res[0].get("total", 0)) if res else 0
        except Exception as e:
            logger.error("Failed to fetch count for %s: %s", rule.code.value, e)
            raise

    async def _fetch_issue_rows(
        self,
        rule: QualityRule,
        search: str | None = None,
        sort_by: str = "PersonID",
        sort_order: str = "desc",
        limit: int = 25,
        offset: int = 0,
    ) -> list[ContactQualityIssueItem]:
        _, items_sql, params = compile_drilldown_queries(
            rule, search=search, sort_by=sort_by, sort_order=sort_order
        )
        params["limit"] = limit
        params["offset"] = offset

        try:
            raw_items = await asyncio.to_thread(_execute_query, items_sql, params)
        except Exception as e:
            logger.error("Failed to execute drilldown query for %s: %s", rule.code.value, e)
            raise

        items: list[ContactQualityIssueItem] = []
        for r in raw_items:
            raw_val = r.get("CurrentValue")
            val_str = str(raw_val) if raw_val is not None else None
            items.append(
                ContactQualityIssueItem(
                    person_id=int(r["PersonID"]),
                    person_name=str(r.get("PersonName") or f"Person #{r['PersonID']}"),
                    contact_id=int(r["ContactID"]) if r.get("ContactID") is not None else None,
                    contact_type=str(r.get("ContactType") or rule.contact_type),
                    label_name=str(r["LabelName"]) if r.get("LabelName") else None,
                    current_value=val_str,
                    masked_value=val_str,
                    issue_code=str(r.get("IssueCode") or rule.code.value),
                    issue_description=str(r.get("IssueDescription") or rule.description),
                    severity=str(r.get("Severity") or rule.severity),
                    is_verified=bool(r["IsVerified"]) if r.get("IsVerified") is not None else None,
                    is_primary=bool(r["IsPrimary"]) if r.get("IsPrimary") is not None else None,
                    is_active=bool(r.get("IsActive", True)),
                )
            )
        return items

    async def _fetch_issue_groups(
        self,
        rule: QualityRule,
        search: str | None = None,
        sort_by: str = "PersonID",
        sort_order: str = "desc",
        limit: int = 25,
        offset: int = 0,
    ) -> list[ContactQualityGroupItem]:
        _, groups_sql, members_sql_template, params = compile_group_queries(
            rule, search=search, sort_by=sort_by, sort_order=sort_order
        )
        params["limit"] = limit
        params["offset"] = offset

        try:
            raw_groups = await asyncio.to_thread(_execute_query, groups_sql, params)
        except Exception as e:
            logger.error("Failed to execute group clusters query for %s: %s", rule.code.value, e)
            raise

        if not raw_groups:
            return []

        group_keys = [str(g["GroupKey"]) for g in raw_groups if g.get("GroupKey") is not None]
        if not group_keys:
            return []

        # Fetch nested member rows for the paginated cluster keys
        key_placeholders = [f":k_{i}" for i in range(len(group_keys))]
        members_params: dict[str, Any] = {f"k_{i}": k for i, k in enumerate(group_keys)}
        members_sql = members_sql_template.replace(":group_keys", ", ".join(key_placeholders))

        try:
            raw_members = await asyncio.to_thread(_execute_query, members_sql, members_params)
        except Exception as e:
            logger.error("Failed to execute group members query for %s: %s", rule.code.value, e)
            raise

        members_by_group: dict[str, list[ContactQualityGroupMember]] = {k: [] for k in group_keys}
        for m in raw_members:
            gk = str(m.get("GroupKey") or m.get("CurrentValue") or "")
            if gk not in members_by_group and len(group_keys) == 1:
                gk = group_keys[0]

            raw_val = m.get("CurrentValue")
            val_str = str(raw_val) if raw_val is not None else None
            member_item = ContactQualityGroupMember(
                person_id=int(m["PersonID"]),
                person_name=str(m.get("PersonName") or f"Person #{m['PersonID']}"),
                contact_id=int(m["ContactID"]) if m.get("ContactID") is not None else None,
                contact_type=str(m.get("ContactType") or rule.contact_type),
                label_name=str(m["LabelName"]) if m.get("LabelName") else None,
                current_value=val_str,
                masked_value=val_str,
                issue_code=str(m.get("IssueCode") or rule.code.value),
                issue_description=str(m.get("IssueDescription") or rule.description),
                severity=str(m.get("Severity") or rule.severity),
                is_verified=bool(m["IsVerified"]) if m.get("IsVerified") is not None else None,
                is_primary=bool(m["IsPrimary"]) if m.get("IsPrimary") is not None else None,
                is_active=bool(m.get("IsActive", True)),
            )
            if gk in members_by_group:
                members_by_group[gk].append(member_item)

        groups: list[ContactQualityGroupItem] = []
        for g in raw_groups:
            gk = str(g["GroupKey"])
            groups.append(
                ContactQualityGroupItem(
                    group_key=gk,
                    group_label=str(g.get("GroupLabel") or gk),
                    affected_persons_count=int(g.get("AffectedPersonsCount") or 1),
                    affected_records_count=int(g.get("AffectedRecordsCount") or 1),
                    members=members_by_group.get(gk, []),
                )
            )
        return groups

    async def get_contact_quality_issues(
        self,
        issue: str = "INVALID_EMAIL",
        search: str | None = None,
        sort_by: str = "PersonID",
        sort_order: str = "desc",
        limit: int = 25,
        offset: int = 0,
    ) -> ContactQualityIssuesResponse:
        """
        Paginated UI endpoint that strictly enforces MAX_PAGE_SIZE = 100.
        Returns groups when count_unit is DUPLICATE_GROUP, and flat items otherwise.
        """
        rule = get_quality_rule(issue)
        if not rule:
            rule = QUALITY_RULES_REGISTRY[ContactQualityIssueType.INVALID_EMAIL]

        norm_issue = rule.code.value
        page_limit = max(1, min(MAX_PAGE_SIZE, limit))
        page_offset = max(0, offset)

        total_count = await self._get_issue_count(rule, search=search)
        if total_count == 0:
            return ContactQualityIssuesResponse(
                issue=norm_issue,
                count_unit=rule.count_unit,
                unit_label_singular=rule.unit_label_singular,
                unit_label_plural=rule.unit_label_plural,
                total=0,
                limit=page_limit,
                offset=page_offset,
                items=[],
                groups=[],
            )

        if rule.count_unit == IssueCountUnit.DUPLICATE_GROUP:
            groups = await self._fetch_issue_groups(
                rule,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=page_limit,
                offset=page_offset,
            )
            return ContactQualityIssuesResponse(
                issue=norm_issue,
                count_unit=rule.count_unit,
                unit_label_singular=rule.unit_label_singular,
                unit_label_plural=rule.unit_label_plural,
                total=total_count,
                limit=page_limit,
                offset=page_offset,
                items=[],
                groups=groups,
            )
        else:
            items = await self._fetch_issue_rows(
                rule,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=page_limit,
                offset=page_offset,
            )
            return ContactQualityIssuesResponse(
                issue=norm_issue,
                count_unit=rule.count_unit,
                unit_label_singular=rule.unit_label_singular,
                unit_label_plural=rule.unit_label_plural,
                total=total_count,
                limit=page_limit,
                offset=page_offset,
                items=items,
                groups=[],
            )

    async def export_contact_quality_issues(
        self,
        issue: str = "INVALID_EMAIL",
        format: str = "xlsx",
        search: str | None = None,
        sort_by: str = "PersonID",
        sort_order: str = "desc",
    ) -> tuple[bytes, str, str]:
        """
        Exports all matching records for a quality issue as CSV or Excel.
        Batches through _fetch_issue_rows() up to MAX_EXPORT_ROWS (50,000) so large datasets are fully exported.
        """
        rule = get_quality_rule(issue)
        if not rule:
            rule = QUALITY_RULES_REGISTRY[ContactQualityIssueType.INVALID_EMAIL]

        items: list[ContactQualityIssueItem] = []
        offset = 0
        batch_size = EXPORT_BATCH_SIZE

        while len(items) < MAX_EXPORT_ROWS:
            batch_limit = min(batch_size, MAX_EXPORT_ROWS - len(items))
            batch = await self._fetch_issue_rows(
                rule,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=batch_limit,
                offset=offset,
            )
            if not batch:
                break
            items.extend(batch)
            offset += len(batch)
            if len(batch) < batch_limit:
                break

        return export_issues_dataset(items, rule.code.value, format=format)

    async def export_contact_quality_summary(self, format: str = "xlsx") -> tuple[bytes, str, str]:
        """
        Exports the 37-KPI quality summary report as CSV or Excel (.xlsx).
        """
        summary = await self.get_contact_quality_summary()
        return export_summary_report(summary, format=format)


__all__ = [
    "ACTIVE_EMP_MISSING_TITLE_WHERE_SQL",
    "ACTIVE_PERSON_WHERE_SQL",
    "ADDR_CITY_WITHOUT_STATE_WHERE_SQL",
    "ADDR_DUPLICATE_SAME_PERSON_WHERE_SQL",
    "ADDR_INVALID_PIN_FORMAT_WHERE_SQL",
    "ADDR_MISSING_GEOCODES_WHERE_SQL",
    "ADDR_MISSING_POSTAL_CODE_WHERE_SQL",
    "ADDR_STREET_WITHOUT_CITY_WHERE_SQL",
    "AUDIT_DEL_BEFORE_ENT_WHERE_SQL",
    "BLACKLIST_MISSING_DETAILS_WHERE_SQL",
    "BLACKLIST_UNAPPROVED_WHERE_SQL",
    "CLASSIFIED_CONTACTS_CTE_SQL",
    "COMPANY_DUPLICATE_LINKS_WHERE_SQL",
    "COMPANY_MISSING_ROLE_WHERE_SQL",
    "COMPANY_ORPHAN_LINKS_WHERE_SQL",
    "DELETED_MISSING_DEL_DATE_WHERE_SQL",
    "DUPLICATE_EMAIL_CROSS_WHERE_SQL",
    "DUPLICATE_EMAIL_SAME_WHERE_SQL",
    "DUPLICATE_PHONE_CROSS_WHERE_SQL",
    "DUPLICATE_PHONE_SAME_WHERE_SQL",
    "EXTRA_FIELD_DUPLICATE_ENTRIES_WHERE_SQL",
    "EXTRA_FIELD_ORPHAN_ID_WHERE_SQL",
    "INACTIVE_WITH_EMPID_WHERE_SQL",
    "INVALID_EMAIL_WHERE_SQL",
    "INVALID_PHONE_WHERE_SQL",
    "INVALID_URL_WHERE_SQL",
    "MULTIPLE_PRIMARY_WHERE_SQL",
    "PERSON_ANNIVERSARY_BEFORE_BIRTH_WHERE_SQL",
    "PERSON_BIRTH_DATE_ANCIENT_WHERE_SQL",
    "PERSON_INVALID_BIRTH_DATE_WHERE_SQL",
    "PERSON_MISSING_LASTNAME_ONLY_WHERE_SQL",
    "PERSON_NAME_SQL",
    "PERSON_SUSPICIOUS_DUMMY_NAMES_WHERE_SQL",
    "PRIMARY_INACTIVE_WHERE_SQL",
    "QUALIFYING_EMAIL_EXISTS_SQL",
    "QUALIFYING_PHONE_EXISTS_SQL",
    "QUALITY_RULES_REGISTRY",
    "STALE_TEMP_PERSONS_WHERE_SQL",
    "STATUS_ACTIVE_AND_DELETED_WHERE_SQL",
    "SYNC_ZIMBRA_MISSING_ID_WHERE_SQL",
    "UNVERIFIED_CONTACT_WHERE_SQL",
    "ContactQualityService",
    "QualityRule",
    "_build_group_queries",
    "_build_issue_queries",
    "compile_drilldown_queries",
    "compile_group_queries",
    "compile_summary_query",
    "get_all_quality_rules",
    "get_quality_rule",
    "resolve_order_clause",
]
