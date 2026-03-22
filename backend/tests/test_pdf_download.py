import uuid

from fastapi.testclient import TestClient

from app.api.routes.jobs import repository
from app.main import app


def test_download_optimized_pdf() -> None:
    client = TestClient(app)
    job_id = f"test-pdf-download-{uuid.uuid4()}"
    repository.create_job(
        job_id,
        {
            "mode": "general",
            "job_description": "",
            "target_role": "",
            "notes": "",
            "original_filename": "resume.pdf",
        },
    )
    repository.save_result(
        job_id,
        {
            "job_id": job_id,
            "input": {
                "mode": "general",
                "target_role": "",
                "original_filename": "resume.pdf",
            },
            "parsed_resume": {
                "basics": {"name": "张三", "phone": "", "email": "", "location": "", "links": []},
                "summary": "",
                "experience": [],
                "education": [],
                "projects": [],
                "skills": [],
            },
            "optimized_resume": {
                "basics": {"name": "张三", "phone": "", "email": "", "location": "", "links": []},
                "summary": "这是优化后的摘要。",
                "experience": [],
                "education": [],
                "projects": [],
                "skills": [],
            },
            "change_summary": ["优化了摘要表达。"],
            "diff_blocks": [],
            "meta": {"processing_ms": 10, "parser_warning": None, "model_name": "mock-llm"},
        },
    )

    response = client.get(f"/api/jobs/{job_id}/optimized-pdf")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
