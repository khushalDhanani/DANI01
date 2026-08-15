from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.postgres import Base, get_db_session
from app.main import app
from app.persistence.models.analysis_run import AnalysisRunModel, AnalysisRunStatus
from app.persistence.models.column_profile import (
    AnalysisColumnClassificationModel,
    AnalysisColumnProfileModel,
)
from app.persistence.models.table_result import (
    AnalysisTableResultModel,
    AnalysisTableTimingModel,
)

from sqlalchemy.pool import StaticPool

# Test SQLite Engine with StaticPool to share connection across threads
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=test_engine)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


app.dependency_overrides[get_db_session] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


def test_create_analysis_run_endpoint_returns_202():
    with patch("app.api.routes.analysis_runs.run_database_analysis_task.delay") as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "mock-celery-task-123"
        mock_delay.return_value = mock_task

        response = client.post(
            "/api/v1/analysis-runs/",
            json={"analysis_type": "QUICK", "schema": "dbo"},
        )

        assert response.status_code == 202
        data = response.json()
        assert "run_id" in data
        assert data["database"] == "AIRIS_TEST"
        assert data["status"] == "QUEUED"
        assert data["analysis_type"] == "QUICK"
        mock_delay.assert_called_once_with(data["run_id"])


def test_get_analysis_run_detail_and_not_found():
    # 1. Test 404
    resp_404 = client.get("/api/v1/analysis-runs/non-existent-uuid")
    assert resp_404.status_code == 404

    # 2. Insert test run
    session = TestingSessionLocal()
    run = AnalysisRunModel(
        id="test-run-123",
        database_name="AIRIS_TEST",
        analysis_type="QUICK",
        status=AnalysisRunStatus.RUNNING.value,
        tables_total=970,
        tables_completed=400,
        tables_skipped=50,
        tables_failed=2,
        progress_percent=46.39,
    )
    session.add(run)
    session.commit()
    session.close()

    # 3. Fetch run detail
    response = client.get("/api/v1/analysis-runs/test-run-123")
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"] == "test-run-123"
    assert data["status"] == "RUNNING"
    assert data["tables_total"] == 970
    assert data["tables_completed"] == 400
    assert data["progress_percent"] == 46.39


def test_list_analysis_runs():
    session = TestingSessionLocal()
    run1 = AnalysisRunModel(id="run-1", database_name="AIRIS_TEST", status="COMPLETED")
    run2 = AnalysisRunModel(id="run-2", database_name="AIRIS_TEST", status="RUNNING")
    session.add_all([run1, run2])
    session.commit()
    session.close()

    response = client.get("/api/v1/analysis-runs/?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_get_analysis_run_tables_and_table_detail():
    session = TestingSessionLocal()
    run = AnalysisRunModel(id="run-detail-test", database_name="AIRIS_TEST", status="COMPLETED")
    session.add(run)
    session.flush()

    table_res = AnalysisTableResultModel(
        run_id="run-detail-test",
        schema_name="dbo",
        table_name="Customers",
        estimated_rows=10000,
        sample_size=1000,
        returned_rows=1000,
        column_count=5,
        profiled_columns=5,
        classified_columns=5,
        status="COMPLETED",
        duration_ms=250.0,
    )
    session.add(table_res)
    session.flush()

    timing = AnalysisTableTimingModel(
        table_result_id=table_res.id,
        structure_duration_ms=20.0,
        sampling_duration_ms=80.0,
        profiling_duration_ms=100.0,
        classification_duration_ms=50.0,
        total_duration_ms=250.0,
    )
    session.add(timing)

    prof = AnalysisColumnProfileModel(
        table_result_id=table_res.id,
        column_name="CustomerID",
        data_type="int",
        profile_type="numeric",
        null_count=0,
        null_percent=0.0,
        distinct_count=1000,
        distinct_percent=100.0,
    )
    session.add(prof)

    classification = AnalysisColumnClassificationModel(
        table_result_id=table_res.id,
        column_name="CustomerID",
        sql_type="int",
        semantic_type="IDENTIFIER",
        sensitivity="INTERNAL",
        expose_values=True,
        confidence=1.0,
    )
    session.add(classification)

    session.commit()
    session.close()

    # 1. Fetch tables list
    tables_resp = client.get("/api/v1/analysis-runs/run-detail-test/tables")
    assert tables_resp.status_code == 200
    tables_data = tables_resp.json()
    assert tables_data["total"] == 1
    assert tables_data["items"][0]["table"] == "Customers"

    # 2. Fetch single table detail
    detail_resp = client.get("/api/v1/analysis-runs/run-detail-test/tables/dbo/Customers")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["table"] == "Customers"
    assert detail_data["timings"]["total_duration_ms"] == 250.0
    assert len(detail_data["column_profiles"]) == 1
    assert detail_data["column_profiles"][0]["column_name"] == "CustomerID"
    assert len(detail_data["column_classifications"]) == 1
    assert detail_data["column_classifications"][0]["semantic_type"] == "IDENTIFIER"


def test_cancel_analysis_run():
    session = TestingSessionLocal()
    run = AnalysisRunModel(id="cancel-test-run", database_name="AIRIS_TEST", status="RUNNING")
    session.add(run)
    session.commit()
    session.close()

    cancel_resp = client.post("/api/v1/analysis-runs/cancel-test-run/cancel")
    assert cancel_resp.status_code == 200
    data = cancel_resp.json()
    assert data["status"] == "CANCELLING"

    # Attempt to cancel a completed run should fail
    session = TestingSessionLocal()
    completed_run = AnalysisRunModel(id="completed-run", database_name="AIRIS_TEST", status="COMPLETED")
    session.add(completed_run)
    session.commit()
    session.close()

    fail_cancel_resp = client.post("/api/v1/analysis-runs/completed-run/cancel")
    assert fail_cancel_resp.status_code == 400
