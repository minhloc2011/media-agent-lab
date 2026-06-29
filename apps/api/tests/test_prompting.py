from media_agent_lab_api.models import AnalysisResult, PromptResult, TrackAnalysis, VocalAnalysis
from media_agent_lab_api.prompting import build_analysis_result, build_mock_analysis_result


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
            tags_vi="nhạc pop ballad Việt Nam, tempo chậm 82 BPM",
            omitted_fields=["chords"],
            warnings=["Thể loại và tông nhạc được suy luận bằng heuristic."],
        ),
    )

    payload = result.model_dump()

    assert payload["track"]["key_vi"] == "La thu"
    assert payload["vocal"]["voice_descriptor"] == "giong cao sang"
    assert payload["prompt"]["omitted_fields"] == ["chords"]


def test_build_mock_analysis_result_includes_confident_fields():
    result = build_mock_analysis_result()

    assert "nhạc pop ballad Việt Nam" in result.prompt.tags_vi
    assert "tempo chậm 82 BPM" in result.prompt.tags_vi
    assert "tông La thứ" in result.prompt.tags_vi
    assert "giọng cao sáng" in result.prompt.tags_vi
    assert "piano chủ đạo" in result.prompt.tags_vi
    assert result.prompt.omitted_fields == ["chords"]
    assert "heuristic" in result.prompt.warnings[0]


def test_build_mock_analysis_result_avoids_biometric_claims():
    result = build_mock_analysis_result()
    prompt_without_market = result.prompt.tags_vi.lower().replace("việt nam", "")

    assert "nam" not in prompt_without_market
    assert "nữ" not in prompt_without_market
    assert "ca sĩ" not in prompt_without_market


def test_build_analysis_result_returns_rich_vietnamese_ace_prompt():
    track = TrackAnalysis(
        bpm=89,
        tempo_bucket="cham",
        key="E",
        scale="minor",
        key_vi="Mi thu",
        energy="thap",
        brightness="am",
        instrumentation=["full mix reference", "vocals da tach", "trong da tach"],
        confidence={"bpm": 0.82, "key": 0.5, "instrumentation": 0.55},
    )
    track = track.model_copy(
        update={
            "energy_curve": "tang dan",
            "section_hint": "verse tối giản, điệp khúc mở rộng",
            "chorus_lift": "manh",
        }
    )
    vocal = VocalAnalysis(
        median_pitch_hz=220.0,
        range_bucket="trung-cao",
        voice_descriptor="giọng trung-cao sáng vừa",
        brightness="sang",
        power="cao",
        density="can bang",
        phrasing="câu hát có khoảng thở tự nhiên",
        presence="noi bat",
        confidence={"pitch": 0.72, "range": 0.68, "voice_descriptor": 0.62},
    )

    result = build_analysis_result(track, vocal=vocal)
    prompt = result.prompt.tags_vi
    prompt_lower = prompt.lower()

    assert "nhạc pop ballad" in prompt_lower
    assert "tempo chậm 89 bpm" in prompt_lower
    assert "tông mi thứ" in prompt_lower
    assert "phối khí" in prompt_lower
    assert "giọng hát" in prompt_lower
    assert "giọng trung-cao sáng vừa" in prompt
    assert "câu hát có khoảng thở tự nhiên" in prompt
    assert "lời mới" in prompt_lower
    assert "điệp khúc" in prompt_lower
    assert "không khí" in prompt_lower
    assert "Đường cong năng lượng" in prompt
    assert "điệp khúc mở rộng" in prompt
    assert len(prompt) > 450
    assert "nhac " not in prompt
    assert " khong " not in prompt
    assert "giong " not in prompt
    assert "chưa phân tích chi tiết" not in prompt
