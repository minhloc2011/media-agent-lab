from pathlib import Path

from media_agent_lab_api.models import JobStatus, TrackAnalysis, VocalAnalysis
from media_agent_lab_api.pipeline import AudioPipeline
from media_agent_lab_api.stem_separator import StemPaths
from media_agent_lab_api.store import JobStore


def test_audio_pipeline_runs_convert_separate_analyze_and_writes_result(tmp_path: Path):
    store = JobStore(tmp_path / "app.db", tmp_path / "jobs")
    job = store.create_job("song.mp3")
    original = store.save_upload(job.id, "song.mp3", b"mp3")

    class FakeConverter:
        def convert_to_wav(self, source: Path, target: Path) -> Path:
            assert source == original
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"wav")
            return target

    class FakeSeparator:
        def separate(self, wav_path: Path, stems_dir: Path, work_dir: Path) -> StemPaths:
            assert wav_path.name == "input.wav"
            stems_dir.mkdir(parents=True, exist_ok=True)
            paths = {name: stems_dir / f"{name}.wav" for name in ["vocals", "drums", "bass", "other"]}
            for name, path in paths.items():
                path.write_bytes(name.encode())
            return StemPaths(**paths)

    def fake_analyzer(wav_path: Path) -> TrackAnalysis:
        assert wav_path.name == "input.wav"
        return TrackAnalysis(
            bpm=96,
            tempo_bucket="vua",
            key="C",
            scale="major",
            key_vi="Do truong",
            energy="vua",
            brightness="sang",
            instrumentation=["full mix reference", "stems da tach"],
            confidence={"bpm": 0.8, "key": 0.45, "instrumentation": 0.5},
        )

    def fake_vocal_analyzer(vocal_path: Path) -> VocalAnalysis:
        assert vocal_path.name in {"vocals.wav", "vocals.mp3"}
        return VocalAnalysis(
            median_pitch_hz=220.0,
            range_bucket="trung-cao",
            voice_descriptor="giọng trung-cao sáng vừa",
            brightness="sang",
            power="cao",
            density="can bang",
            phrasing="câu hát có khoảng thở tự nhiên",
            presence="noi bat",
            confidence={"pitch": 0.7, "range": 0.7, "voice_descriptor": 0.65},
        )

    def fake_structure_analyzer(wav_path: Path) -> dict[str, str]:
        assert wav_path.name == "input.wav"
        return {
            "energy_curve": "tang dan",
            "section_hint": "verse tối giản, điệp khúc mở rộng",
            "chorus_lift": "manh",
        }

    pipeline = AudioPipeline(
        converter=FakeConverter(),
        separator=FakeSeparator(),
        mix_analyzer=fake_analyzer,
        vocal_analyzer=fake_vocal_analyzer,
        structure_analyzer=fake_structure_analyzer,
    )

    result = pipeline.run(store, job.id)
    loaded = store.get_job(job.id)

    assert loaded is not None
    assert loaded.status == JobStatus.COMPLETED
    assert result.track.bpm == 96
    assert result.vocal.voice_descriptor == "giọng trung-cao sáng vừa"
    assert "tempo vừa 96 BPM" in result.prompt.tags_vi
    assert "phối khí" in result.prompt.tags_vi.lower()
    assert "giọng trung-cao sáng vừa" in result.prompt.tags_vi
    assert "lời mới" in result.prompt.tags_vi
    metadata_path = store.job_dir(job.id) / "metadata" / "result.json"
    assert metadata_path.exists()
    metadata_text = metadata_path.read_text(encoding="utf-8")
    assert "giọng trung-cao sáng vừa" in metadata_text
    assert "Đường cong năng lượng" in metadata_text
