from media_agent_lab_api.models import (
    AnalysisResult,
    LanguageAnalysis,
    PromptResult,
    TrackAnalysis,
    VocalAnalysis,
)


def build_mock_analysis_result() -> AnalysisResult:
    track = TrackAnalysis(
        bpm=82,
        tempo_bucket="cham",
        key="A",
        scale="minor",
        key_vi="La thu",
        energy="thap",
        brightness="sang",
        instrumentation=["piano chu dao", "trong nhe", "bass mem"],
        confidence={"bpm": 0.86, "key": 0.62, "instrumentation": 0.45},
    )
    vocal = VocalAnalysis(
        median_pitch_hz=220.0,
        range_bucket="cao",
        voice_descriptor="giong cao sang",
        brightness="sang",
        power="nhe",
        confidence={"pitch": 0.78, "range": 0.7, "voice_descriptor": 0.55},
    )
    language = LanguageAnalysis(
        detected="vi",
        label_vi="Viet Nam",
        confidence=0.74,
        used_in_prompt=True,
    )
    fragments = [
        "nhac pop ballad Viet Nam",
        f"tempo {track.tempo_bucket} {track.bpm} BPM",
        f"tong {track.key_vi}",
        vocal.voice_descriptor,
        "am sac sang va tinh cam",
        *track.instrumentation,
        "khong khi cam xuc cho diep khuc tru tinh",
    ]
    prompt = PromptResult(
        tags_vi=", ".join(fragments),
        omitted_fields=["chords"],
        warnings=["genre la heuristic co confidence trung binh"],
    )
    return AnalysisResult(track=track, vocal=vocal, language=language, prompt=prompt)
