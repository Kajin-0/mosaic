from mosaic_engine.app import create_app
from mosaic_engine.config import Settings
from mosaic_engine.version import CONTRACT_VERSION


def test_openapi_surface_is_explicit_and_versioned() -> None:
    app = create_app(Settings(environment="test", log_level="CRITICAL"))
    schema = app.openapi()

    assert schema["info"]["version"] == CONTRACT_VERSION
    assert set(schema["paths"]) == {
        "/health",
        "/version",
        "/v1/calibration/next",
        "/v1/calibration/response",
        "/v1/matches/rank",
    }
    operation_ids = {
        operation["operationId"]
        for path_item in schema["paths"].values()
        for operation in path_item.values()
        if isinstance(operation, dict) and "operationId" in operation
    }
    assert operation_ids == {
        "getHealth",
        "getVersion",
        "getNextCalibrationTrial",
        "submitCalibrationResponse",
        "rankMatches",
    }
