from unittest.mock import patch

from app.modules.procedure_logic.procedure_logic_service import (
    BUSINESS_RULES_TAXONOMY,
    ProcedureLogicService,
)


def test_business_rules_taxonomy():
    assert len(BUSINESS_RULES_TAXONOMY) >= 7
    for rdef in BUSINESS_RULES_TAXONOMY:
        assert "code" in rdef
        assert "canonical" in rdef


@patch.object(ProcedureLogicService, "_fetch_all_sql_objects")
def test_get_procedure_logic_overview(mock_fetch):
    mock_fetch.return_value = [
        {
            "object_id": 101,
            "object_name": "usp_GetActiveEmployees",
            "object_type": "SQL_STORED_PROCEDURE",
            "definition": "CREATE PROCEDURE usp_GetActiveEmployees AS SELECT * FROM dbo.EmployeeMst WHERE EmpIsActive = 1;",
        },
        {
            "object_id": 102,
            "object_name": "fn_GetActiveEmpCount",
            "object_type": "SQL_SCALAR_FUNCTION",
            "definition": "CREATE FUNCTION fn_GetActiveEmpCount() RETURNS INT AS BEGIN RETURN (SELECT COUNT(*) FROM dbo.EmployeeMst WHERE EmpIsActive = 1 AND EmpIsDeleted = 0); END;",
        },
        {
            "object_id": 103,
            "object_name": "vw_OfficialAssign",
            "object_type": "VIEW",
            "definition": "CREATE VIEW vw_OfficialAssign AS SELECT * FROM dbo.EmployeeOfficialDet;",
        },
        {
            "object_id": 104,
            "object_name": "tr_UserAudit",
            "object_type": "SQL_TRIGGER",
            "definition": "CREATE TRIGGER tr_UserAudit ON dbo.SecurityUserMst FOR INSERT AS SELECT UserID FROM inserted;",
        },
    ]

    service = ProcedureLogicService()
    res = service.get_procedure_logic_overview()

    assert res.total_sql_objects == 4
    assert res.total_stored_procedures == 1
    assert res.total_functions == 1
    assert res.total_views == 1
    assert res.total_triggers == 1
    assert res.total_inconsistencies >= 1
    assert len(res.business_rules) >= 7


@patch.object(ProcedureLogicService, "_fetch_all_sql_objects")
def test_get_sql_objects_catalog(mock_fetch):
    mock_fetch.return_value = [
        {
            "object_id": 101,
            "object_name": "usp_GetActiveEmployees",
            "object_type": "SQL_STORED_PROCEDURE",
            "definition": "CREATE PROCEDURE usp_GetActiveEmployees AS SELECT * FROM dbo.EmployeeMst WHERE EmpIsActive = 1;",
        }
    ]

    service = ProcedureLogicService()
    res = service.get_sql_objects_catalog(search="Active")

    assert res.total == 1
    assert len(res.items) == 1
    assert res.items[0].object_name == "usp_GetActiveEmployees"
    assert "EmployeeMst" in res.items[0].used_tables


@patch.object(ProcedureLogicService, "_fetch_all_sql_objects")
def test_get_inconsistencies(mock_fetch):
    mock_fetch.return_value = [
        {
            "object_id": 101,
            "object_name": "usp_GetActiveEmployees",
            "object_type": "SQL_STORED_PROCEDURE",
            "definition": "CREATE PROCEDURE usp_GetActiveEmployees AS SELECT * FROM dbo.EmployeeMst WHERE EmpIsActive = 1;",
        }
    ]

    service = ProcedureLogicService()
    res = service.get_inconsistencies(severity="CRITICAL")

    assert res.total >= 1
    assert res.items[0].severity == "CRITICAL"


@patch.object(ProcedureLogicService, "_fetch_all_sql_objects")
@patch("app.modules.procedure_logic.procedure_logic_service.execute_readonly_query")
def test_get_sql_object_detail(mock_exec, mock_fetch):
    mock_fetch.return_value = [
        {
            "object_id": 101,
            "object_name": "usp_GetActiveEmployees",
            "object_type": "SQL_STORED_PROCEDURE",
            "definition": "CREATE PROCEDURE usp_GetActiveEmployees AS SELECT * FROM dbo.EmployeeMst WHERE EmpIsActive = 1;",
        }
    ]
    mock_exec.return_value = [
        {
            "object_id": 101,
            "object_name": "usp_GetActiveEmployees",
            "object_type": "SQL_STORED_PROCEDURE",
            "definition": "CREATE PROCEDURE usp_GetActiveEmployees AS SELECT * FROM dbo.EmployeeMst WHERE EmpIsActive = 1;",
        }
    ]

    service = ProcedureLogicService()
    detail = service.get_sql_object_detail(101)

    assert detail is not None
    assert detail.object_id == 101
    assert detail.object_name == "usp_GetActiveEmployees"


@patch.object(ProcedureLogicService, "_fetch_all_sql_objects")
def test_download_inconsistencies_export(mock_fetch):
    mock_fetch.return_value = [
        {
            "object_id": 101,
            "object_name": "usp_GetActiveEmployees",
            "object_type": "SQL_STORED_PROCEDURE",
            "definition": "CREATE PROCEDURE usp_GetActiveEmployees AS SELECT * FROM dbo.EmployeeMst WHERE EmpIsActive = 1;",
        }
    ]

    service = ProcedureLogicService()
    csv_bytes = service.download_inconsistencies_export()

    assert isinstance(csv_bytes, bytes)
    content = csv_bytes.decode("utf-8")
    assert "Inconsistency ID,Business Rule Code" in content
