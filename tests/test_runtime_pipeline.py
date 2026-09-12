from pathlib import Path

from src.app import rank_uploaded_inputs


class UploadedFile:
    def __init__(self, name: str, content: bytes) -> None:
        self.name = name
        self._content = content

    def getvalue(self) -> bytes:
        return self._content


def test_uploaded_jd_and_multiple_resumes_are_ranked() -> None:
    fixture_root = Path("data/dummy_resumes/Dummy Resumes")
    resume_paths = [
        fixture_root / "App_Developer_Resume_1_Siddharth_Rao.xml",
        fixture_root / "App_Developer_Resume_2_Kavya_Menon.xml",
    ]
    jd = UploadedFile(
        "job.txt",
        b"Junior developer\nRequired: JavaScript and React\nPreferred: Git",
    )
    resumes = [UploadedFile(path.name, path.read_bytes()) for path in resume_paths]

    rankings = rank_uploaded_inputs(jd, resumes)

    assert len(rankings) == 2
    assert [item["rank"] for item in rankings] == [1, 2]
    assert all(item["candidate_id"] for item in rankings)
    assert all(item["requirement_results"] for item in rankings)
