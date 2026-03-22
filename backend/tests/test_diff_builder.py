from app.schemas.resume import ResumeSchema
from app.services.diff_builder import DiffBuilder


def test_diff_builder_creates_summary_and_experience_blocks() -> None:
    original = ResumeSchema.model_validate(
        {
            "summary": "Product manager with startup experience",
            "experience": [
                {
                    "block_id": "exp_1",
                    "company": "Acme",
                    "title": "PM",
                    "bullets": ["Led roadmap planning"],
                }
            ],
        }
    )
    optimized = ResumeSchema.model_validate(
        {
            "summary": "Product manager with startup and growth experience",
            "experience": [
                {
                    "block_id": "exp_1",
                    "company": "Acme",
                    "title": "PM",
                    "bullets": ["Delivered roadmap planning with clearer scope and impact."],
                }
            ],
        }
    )
    result = DiffBuilder().build(original, optimized)
    assert len(result) >= 2
