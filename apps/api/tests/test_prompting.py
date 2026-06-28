from media_agent_lab_api.models import AnalysisResult, PromptResult, TrackAnalysis, VocalAnalysis
from media_agent_lab_api.prompting import build_mock_analysis_result


def test_analysis_result_serializes_prompt_contract():
    result = AnalysisResult(
        track=TrackAnalysis(
            bpm=82,
            tempo_bucket="cham",
            key="A",
            scale="minor",
            key_vi="La thu",
            energy="thap",
            brightness="sang",
            instrumentation=["piano chu dao", "trong nhe", "bass mem"],
            confidence={"bpm": 0.86, "key": 0.62, "instrumentation": 0.45},
        ),
        vocal=VocalAnalysis(
            median_pitch_hz=220.0,
            range_bucket="cao",
            voice_descriptor="giong cao sang",
            brightness="sang",
            power="nhe",
            confidence={"pitch": 0.78, "range": 0.7, "voice_descriptor": 0.55},
        ),
        prompt=PromptResult(
            tags_vi="nhac pop ballad Viet Nam, tempo cham 82 BPM",
            omitted_fields=["chords"],
            warnings=["genre la heuristic co confidence trung binh"],
        ),
    )

    payload = result.model_dump()

    assert payload["track"]["key_vi"] == "La thu"
    assert payload["vocal"]["voice_descriptor"] == "giong cao sang"
    assert payload["prompt"]["omitted_fields"] == ["chords"]


def test_build_mock_analysis_result_includes_confident_fields():
    result = build_mock_analysis_result()

    assert result.prompt.tags_vi == (
        "nhac pop ballad Viet Nam, tempo cham 82 BPM, tong La thu, "
        "giong cao sang, am sac sang va tinh cam, piano chu dao, "
        "trong nhe, bass mem, khong khi cam xuc cho diep khuc tru tinh"
    )
    assert result.prompt.omitted_fields == ["chords"]
    assert "confidence trung binh" in result.prompt.warnings[0]


def test_build_mock_analysis_result_avoids_biometric_claims():
    result = build_mock_analysis_result()
    prompt_without_market = result.prompt.tags_vi.lower().replace("viet nam", "")

    assert "nam" not in prompt_without_market
    assert "nu" not in prompt_without_market
    assert "ca si" not in prompt_without_market
