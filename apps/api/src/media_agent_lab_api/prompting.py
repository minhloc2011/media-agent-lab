from media_agent_lab_api.models import (
    AnalysisResult,
    LanguageAnalysis,
    PromptResult,
    TrackAnalysis,
    VocalAnalysis,
)

TEMPO_LABELS = {
    "cham": "chậm",
    "vua": "vừa",
    "nhanh": "nhanh",
}

ENERGY_LABELS = {
    "thap": "thấp",
    "vua": "vừa",
    "cao": "cao",
    "nhe": "nhẹ",
}

BRIGHTNESS_LABELS = {
    "am": "ấm",
    "toi": "tối",
    "sang": "sáng",
}

KEY_LABELS = {
    "Do truong": "Đô trưởng",
    "Do thang truong": "Đô thăng trưởng",
    "Re truong": "Rê trưởng",
    "Re thang truong": "Rê thăng trưởng",
    "Mi truong": "Mi trưởng",
    "Fa truong": "Fa trưởng",
    "Fa thang truong": "Fa thăng trưởng",
    "Sol truong": "Sol trưởng",
    "Sol thang truong": "Sol thăng trưởng",
    "La truong": "La trưởng",
    "La thang truong": "La thăng trưởng",
    "Si truong": "Si trưởng",
    "Do thu": "Đô thứ",
    "Do thang thu": "Đô thăng thứ",
    "Re thu": "Rê thứ",
    "Re thang thu": "Rê thăng thứ",
    "Mi thu": "Mi thứ",
    "Fa thu": "Fa thứ",
    "Fa thang thu": "Fa thăng thứ",
    "Sol thu": "Sol thứ",
    "Sol thang thu": "Sol thăng thứ",
    "La thu": "La thứ",
    "La thang thu": "La thăng thứ",
    "Si thu": "Si thứ",
}

INSTRUMENTATION_LABELS = {
    "piano chu dao": "piano chủ đạo",
    "trong nhe": "trống nhẹ",
    "trong da tach": "trống đã tách",
    "bass mem": "bass mềm",
    "full mix reference": "bản phối tham chiếu đầy đủ",
    "stems da tach": "stem đã tách",
    "vocals da tach": "vocal đã tách",
}

VOICE_LABELS = {
    "giong cao sang": "giọng cao sáng",
    "giong hat chua phan tach chi tiet": "giọng hát chưa phân tích chi tiết",
}


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
    return build_analysis_result(track, vocal=vocal, language=language)


def build_analysis_result(
    track: TrackAnalysis,
    vocal: VocalAnalysis | None = None,
    language: LanguageAnalysis | None = None,
) -> AnalysisResult:
    vocal = vocal or VocalAnalysis(
        median_pitch_hz=0.0,
        range_bucket="khong ro",
        voice_descriptor="giong hat chua phan tach chi tiet",
        brightness=track.brightness,
        power=track.energy,
        confidence={"pitch": 0.0, "range": 0.0, "voice_descriptor": 0.2},
    )
    language = language or LanguageAnalysis(
        detected=None,
        label_vi=None,
        confidence=0.0,
        used_in_prompt=False,
    )
    prompt_text = _build_ace_prompt(track, vocal, language)
    prompt = PromptResult(
        tags_vi=prompt_text,
        omitted_fields=["chords"],
        warnings=["Thể loại, tông nhạc và phối khí được suy luận bằng heuristic."],
    )
    return AnalysisResult(track=track, vocal=vocal, language=language, prompt=prompt)


def _build_ace_prompt(
    track: TrackAnalysis,
    vocal: VocalAnalysis,
    language: LanguageAnalysis,
) -> str:
    style = "nhạc pop ballad Việt Nam" if language.used_in_prompt else "nhạc pop ballad"
    tempo = _label(track.tempo_bucket, TEMPO_LABELS)
    key = _label(track.key_vi, KEY_LABELS)
    energy = _label(track.energy, ENERGY_LABELS)
    brightness = _label(track.brightness, BRIGHTNESS_LABELS)
    voice = _label(vocal.voice_descriptor, VOICE_LABELS)
    instruments = [_label(item, INSTRUMENTATION_LABELS) for item in track.instrumentation]
    arrangement = ", ".join(instruments) if instruments else "piano, bass mềm và trống tiết chế"

    sections = [
        (
            f"{style}, tempo {tempo} {track.bpm} BPM, tông {key}, "
            f"năng lượng {energy}, âm sắc {brightness} và giàu cảm xúc."
        ),
        (
            f"Phối khí lấy {arrangement} làm nền, giữ không gian rộng vừa phải, "
            "verse tối giản để lời nổi rõ, pre-chorus nâng dần bằng pad hoặc piano, "
            "điệp khúc mở hơn với trống chắc, bass ấm và lớp hòa âm mềm."
        ),
        (
            f"Giọng hát: {voice}; ưu tiên cách hát rõ chữ, gần gũi, có độ ngân ở cuối câu, "
            "không mô phỏng danh tính người biểu diễn cụ thể."
        ),
        (
            "Không khí tổng thể sâu lắng, lãng mạn, hiện đại, phù hợp lời mới bằng tiếng Việt. "
            "Giai điệu nên có hook dễ nhớ, câu hát tự nhiên theo thanh điệu tiếng Việt, "
            "có khoảng thở giữa các ý và tránh nhồi quá nhiều âm tiết."
        ),
        (
            "Khi tạo bản nhạc mới, giữ cảm giác tham chiếu về tempo, tông, độ sáng và đường cong cảm xúc; "
            "cho phép thay đổi melody để lời mới nghe tự nhiên, nhưng vẫn giữ điệp khúc giàu cao trào và dễ hát lại."
        ),
    ]
    return " ".join(sections)


def _label(value: str, mapping: dict[str, str]) -> str:
    return mapping.get(value, value)
