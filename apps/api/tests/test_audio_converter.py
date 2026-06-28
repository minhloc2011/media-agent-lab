from pathlib import Path

from media_agent_lab_api.audio_converter import AudioConverter


def test_audio_converter_runs_ffmpeg_command(tmp_path: Path):
    calls: list[list[str]] = []
    input_path = tmp_path / "input.mp3"
    output_path = tmp_path / "audio" / "input.wav"
    input_path.write_bytes(b"fake mp3")

    def fake_runner(command: list[str]) -> None:
        calls.append(command)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake wav")

    converter = AudioConverter(ffmpeg_exe="ffmpeg-test", runner=fake_runner)

    converted = converter.convert_to_wav(input_path, output_path)

    assert converted == output_path
    assert output_path.read_bytes() == b"fake wav"
    assert calls == [
        [
            "ffmpeg-test",
            "-y",
            "-i",
            str(input_path),
            "-ar",
            "44100",
            "-ac",
            "2",
            str(output_path),
        ]
    ]
