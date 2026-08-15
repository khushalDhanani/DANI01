import logging
import time
from typing import Any

from app.db.mssql import execute_readonly_query
from app.discovery.metadata import MetadataDiscovery
from app.modules.definitions.person import PersonModuleDefinition
from app.modules.person.queries import (
    build_child_table_counts_query,
    build_person_metrics_query,
)
from app.modules.person.schemas import (
    PersonMetricsSummary,
    PersonModuleMetricsResponse,
)

logger = logging.getLogger(__name__)


def safe_percent(numerator: int | None, denominator: int | None) -> float | None:
    """Safely calculates percentage with division-by-zero protection."""
    if numerator is None or denominator is None or denominator <= 0:
        return 0.0 if numerator is not None and denominator == 0 else None
    return round((numerator / denominator) * 100, 2)


class PersonMetricsService:
    """
    Computes domain aggregate metrics for the PERSON module using set-based MSSQL queries.
    """

    def __init__(self, discovery: MetadataDiscovery | None = None) -> None:
        self.discovery = discovery or MetadataDiscovery()

    async def calculate_metrics(self) -> PersonModuleMetricsResponse:
        start_time = time.perf_counter()
        warnings: list[str] = []

        definition = PersonModuleDefinition
        root_schema = definition.root_schema
        root_table = definition.root_table
        full_root_table = f"{root_schema}.{root_table}"

        # 1. Verify Root Table
        try:
            root_struct = self.discovery.get_table_structure(root_schema, root_table)
            root_cols = {c.name.lower() for c in root_struct.columns}
            has_active_col = "personisactive" in root_cols
            has_deleted_col = "personisdeleted" in root_cols
            has_temp_col = "personistemp" in root_cols
            has_blacklist_col = "personisblacklist" in root_cols
        except Exception as e:
            return PersonModuleMetricsResponse(
                module="PERSON",
                status="FAILED",
                root_entity=full_root_table,
                metrics=PersonMetricsSummary(total_persons=0),
                warnings=[f"Root entity '{full_root_table}' could not be accessed: {e}"],
                duration_ms=0.0,
            )

        # 2. Check Optional Child Tables
        tables_map = {t.table_name.lower(): t for t in definition.tables}

        def resolve_child_table(table_name: str) -> str | None:
            t_def = tables_map.get(table_name.lower())
            if not t_def:
                return None
            try:
                self.discovery.get_table_structure(t_def.schema_name, t_def.table_name)
                return f"{t_def.schema_name}.{t_def.table_name}"
            except Exception:
                warnings.append(f"Optional table '{t_def.schema_name}.{t_def.table_name}' is missing; corresponding metrics will be unavailable.")
                return None

        address_tbl = resolve_child_table("DLPersonAddressDet")
        contact_tbl = resolve_child_table("DLPersonPhoneEmailURLDet")
        company_link_tbl = resolve_child_table("DLPersonCompanyLinkDet")
        relation_tbl = resolve_child_table("DLPersonRelationDet")
        doc_tbl = resolve_child_table("DLPersonDocumentDet")
        extra_tbl = resolve_child_table("DLPersonExtraFieldValueDet")
        im_tbl = resolve_child_table("DLPersonIMDet")

        # 3. Build & Execute Person Aggregate Query
        agg_sql = build_person_metrics_query(
            root_table=full_root_table,
            root_key=definition.root_key,
            has_active_col=has_active_col,
            has_deleted_col=has_deleted_col,
            has_temp_col=has_temp_col,
            has_blacklist_col=has_blacklist_col,
            address_table=address_tbl,
            contact_table=contact_tbl,
            contact_person_key="PersionID",
            company_link_table=company_link_tbl,
            relation_table=relation_tbl,
            document_table=doc_tbl,
            extra_field_table=extra_tbl,
            im_table=im_tbl,
        )

        try:
            agg_results = execute_readonly_query(agg_sql)
            row: dict[str, Any] = agg_results[0] if agg_results else {}
        except Exception as e:
            logger.error(f"Error executing person aggregate query: {e}")
            return PersonModuleMetricsResponse(
                module="PERSON",
                status="FAILED",
                root_entity=full_root_table,
                metrics=PersonMetricsSummary(total_persons=0),
                warnings=[f"Database query failed: {e}"],
                duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
            )

        # 4. Fetch Child Table Counts (for total relations where query uses UNION)
        child_tables_dict: dict[str, str] = {}
        if relation_tbl:
            child_tables_dict["total_relationships"] = relation_tbl

        child_counts: dict[str, Any] = {}
        if child_tables_dict:
            try:
                child_sql = build_child_table_counts_query(child_tables_dict)
                c_res = execute_readonly_query(child_sql)
                if c_res:
                    child_counts = c_res[0]
            except Exception as e:
                warnings.append(f"Could not load total row counts for child tables: {e}")

        # 5. Process Metrics & Percentages
        total_persons = int(row.get("total_persons") or 0)
        active_persons = row.get("active_persons")
        inactive_persons = row.get("inactive_persons")
        deleted_persons = row.get("deleted_persons")
        temp_persons = row.get("temp_persons")
        blacklist_persons = row.get("blacklist_persons")

        active_cnt = int(active_persons) if active_persons is not None else None
        inactive_cnt = int(inactive_persons) if inactive_persons is not None else None
        deleted_cnt = int(deleted_persons) if deleted_persons is not None else None
        temp_cnt = int(temp_persons) if temp_persons is not None else None
        blacklist_cnt = int(blacklist_persons) if blacklist_persons is not None else None

        # Address metrics
        p_addr = row.get("persons_with_address")
        p_addr_cnt = int(p_addr) if p_addr is not None else None
        p_no_addr = total_persons - p_addr_cnt if p_addr_cnt is not None else None
        tot_addr = int(row.get("total_addresses") or 0) if address_tbl else None
        act_addr = int(row.get("active_addresses") or 0) if address_tbl else None
        geo_addr = int(row.get("geo_addresses") or 0) if address_tbl else None
        fmt_addr = int(row.get("formatted_addresses") or 0) if address_tbl else None
        post_addr = int(row.get("postal_addresses") or 0) if address_tbl else None

        # Contact metrics
        p_contact = row.get("persons_with_contact")
        p_contact_cnt = int(p_contact) if p_contact is not None else None
        p_no_contact = total_persons - p_contact_cnt if p_contact_cnt is not None else None
        tot_contact = int(row.get("total_contacts") or 0) if contact_tbl else None
        act_contact = int(row.get("active_contacts") or 0) if contact_tbl else None
        ver_contact = int(row.get("verified_contacts") or 0) if contact_tbl else None
        pri_contact = int(row.get("primary_contacts") or 0) if contact_tbl else None

        p_email = row.get("persons_with_email")
        p_email_cnt = int(p_email) if p_email is not None else None
        p_no_email = total_persons - p_email_cnt if p_email_cnt is not None else None

        p_phone = row.get("persons_with_phone")
        p_phone_cnt = int(p_phone) if p_phone is not None else None
        p_no_phone = total_persons - p_phone_cnt if p_phone_cnt is not None else None

        # Company link metrics
        p_comp = row.get("persons_with_company_link")
        p_comp_cnt = int(p_comp) if p_comp is not None else None
        p_no_comp = total_persons - p_comp_cnt if p_comp_cnt is not None else None
        tot_comp = int(row.get("total_company_links") or 0) if company_link_tbl else None

        # Relation metrics
        p_rel = row.get("persons_with_relationship")
        p_rel_cnt = int(p_rel) if p_rel is not None else None
        p_no_rel = total_persons - p_rel_cnt if p_rel_cnt is not None else None
        tot_rel = int(child_counts["total_relationships"]) if "total_relationships" in child_counts else None

        # Document metrics
        p_doc = row.get("persons_with_document")
        p_doc_cnt = int(p_doc) if p_doc is not None else None
        p_no_doc = total_persons - p_doc_cnt if p_doc_cnt is not None else None
        tot_doc = int(row.get("total_documents") or 0) if doc_tbl else None

        # Extra field metrics
        p_extra = row.get("persons_with_extra_field")
        p_extra_cnt = int(p_extra) if p_extra is not None else None
        p_no_extra = total_persons - p_extra_cnt if p_extra_cnt is not None else None
        tot_extra = int(row.get("total_extra_fields") or 0) if extra_tbl else None

        # IM metrics
        p_im = row.get("persons_with_im")
        p_im_cnt = int(p_im) if p_im is not None else None
        p_no_im = total_persons - p_im_cnt if p_im_cnt is not None else None
        tot_im = int(row.get("total_ims") or 0) if im_tbl else None

        summary = PersonMetricsSummary(
            total_persons=total_persons,
            active_persons=active_cnt,
            inactive_persons=inactive_cnt,
            active_percent=safe_percent(active_cnt, total_persons),
            inactive_percent=safe_percent(inactive_cnt, total_persons),
            deleted_persons=deleted_cnt,
            deleted_percent=safe_percent(deleted_cnt, total_persons),
            temp_persons=temp_cnt,
            temp_percent=safe_percent(temp_cnt, total_persons),
            blacklist_persons=blacklist_cnt,
            blacklist_percent=safe_percent(blacklist_cnt, total_persons),

            # Business Mappings: PersonIsVisitor_Contact (1=Visitor, 2=Contact)
            visitor_count=int(row.get("visitor_count") or 0),
            visitor_percent=safe_percent(int(row.get("visitor_count") or 0), total_persons),
            contact_entity_count=int(row.get("contact_entity_count") or 0),
            contact_entity_percent=safe_percent(int(row.get("contact_entity_count") or 0), total_persons),

            # Business Mappings: PersonIsShareContact (0=Private, 1=Public)
            public_count=int(row.get("public_count") or 0),
            public_percent=safe_percent(int(row.get("public_count") or 0), total_persons),
            private_count=int(row.get("private_count") or 0),
            private_percent=safe_percent(int(row.get("private_count") or 0), total_persons),

            # Address
            persons_with_address=p_addr_cnt,
            persons_without_address=p_no_addr,
            address_coverage_percent=safe_percent(p_addr_cnt, total_persons),
            total_addresses=tot_addr,

            # Contact
            persons_with_contact=p_contact_cnt,
            persons_without_contact=p_no_contact,
            contact_coverage_percent=safe_percent(p_contact_cnt, total_persons),
            total_contacts=tot_contact,

            # Email & Phone
            persons_with_email=p_email_cnt,
            persons_without_email=p_no_email,
            email_coverage_percent=safe_percent(p_email_cnt, total_persons),
            persons_with_phone=p_phone_cnt,
            persons_without_phone=p_no_phone,
            phone_coverage_percent=safe_percent(p_phone_cnt, total_persons),

            # Company Link
            persons_with_company_link=p_comp_cnt,
            persons_without_company_link=p_no_comp,
            company_link_coverage_percent=safe_percent(p_comp_cnt, total_persons),
            total_company_links=tot_comp,

            # Relationship
            persons_with_relationship=p_rel_cnt,
            persons_without_relationship=p_no_rel,
            relationship_coverage_percent=safe_percent(p_rel_cnt, total_persons),
            total_relationships=tot_rel,

            # Documents
            persons_with_document=p_doc_cnt,
            persons_without_document=p_no_doc,
            document_coverage_percent=safe_percent(p_doc_cnt, total_persons),
            total_documents=tot_doc,

            # Extra Fields
            persons_with_extra_field=p_extra_cnt,
            persons_without_extra_field=p_no_extra,
            extra_field_coverage_percent=safe_percent(p_extra_cnt, total_persons),
            total_extra_fields=tot_extra,

            # IM Handles
            persons_with_im=p_im_cnt,
            persons_without_im=p_no_im,
            im_coverage_percent=safe_percent(p_im_cnt, total_persons),
            total_ims=tot_im,

            # Contact Health
            active_contacts=act_contact,
            active_contacts_percent=safe_percent(act_contact, tot_contact),
            verified_contacts=ver_contact,
            verified_contacts_percent=safe_percent(ver_contact, tot_contact),
            primary_contacts=pri_contact,
            primary_contacts_percent=safe_percent(pri_contact, tot_contact),

            # Address Health
            active_addresses=act_addr,
            active_addresses_percent=safe_percent(act_addr, tot_addr),
            geo_addresses=geo_addr,
            geo_addresses_percent=safe_percent(geo_addr, tot_addr),
            formatted_addresses=fmt_addr,
            formatted_addresses_percent=safe_percent(fmt_addr, tot_addr),
            postal_addresses=post_addr,
            postal_addresses_percent=safe_percent(post_addr, tot_addr),
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        status = "DEGRADED" if warnings else "COMPLETED"

        return PersonModuleMetricsResponse(
            module="PERSON",
            status=status,
            root_entity=full_root_table,
            metrics=summary,
            warnings=warnings,
            duration_ms=round(duration_ms, 2),
        )
