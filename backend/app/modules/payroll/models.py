from dataclasses import dataclass


@dataclass
class PayrollTableInfo:
    table_name: str
    table_type: str  # HEADER, DETAIL_EARNING, DETAIL_DEDUCTION, PAYSLIP_BANK, MASTER
    record_count: int
    primary_key: str
    foreign_keys: list[str]
