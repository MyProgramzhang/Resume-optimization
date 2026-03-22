from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


def test_create_job_requires_pdf() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/jobs",
        data={"mode": "general"},
        files={"resume_file": ("resume.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400
