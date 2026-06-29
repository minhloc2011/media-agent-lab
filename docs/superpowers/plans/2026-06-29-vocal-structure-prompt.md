# Vocal Structure Prompt Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add vocal-stem and structure heuristics so ACE prompts describe the reference vocal and energy arc instead of using generic fallback text.

**Architecture:** Keep analyzers as small independent modules. `vocal_analyzer.py` reads Demucs vocal stems and returns `VocalAnalysis`; `structure_analyzer.py` reads the full mix and returns structure fields merged into `TrackAnalysis`; `pipeline.py` orchestrates both before prompt generation.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, librosa, numpy, soundfile, pytest.

---

## File Map

- Create `apps/api/src/media_agent_lab_api/vocal_analyzer.py`: vocal stem heuristic analysis.
- Create `apps/api/src/media_agent_lab_api/structure_analyzer.py`: full-mix energy curve analysis.
- Modify `apps/api/src/media_agent_lab_api/models.py`: add backward-compatible optional fields to `TrackAnalysis` and `VocalAnalysis`.
- Modify `apps/api/src/media_agent_lab_api/pipeline.py`: inject and run vocal/structure analyzers.
- Modify `apps/api/src/media_agent_lab_api/prompting.py`: render real vocal and structure details into `prompt.tags_vi`.
- Create `apps/api/tests/test_vocal_analyzer.py`: test vocal heuristic output on synthetic signal.
- Create `apps/api/tests/test_structure_analyzer.py`: test rising energy curve on synthetic signal.
- Modify `apps/api/tests/test_pipeline.py`: test analyzer orchestration and metadata.
- Modify `apps/api/tests/test_prompting.py`: test prompt consumes real vocal/structure data.

### Task 1: Extend Models

**Files:**
- Modify: `apps/api/src/media_agent_lab_api/models.py`
- Test: `apps/api/tests/test_prompting.py`

- [ ] **Step 1: Write failing model/prompt test**

Add assertions in `test_build_analysis_result_returns_rich_vietnamese_ace_prompt()` that use these new fields:

```python
track = track.model_copy(update={
    "energy_curve": "tang dan",
    "section_hint": "verse tối giản, điệp khúc mở rộng",
    "chorus_lift": "manh",
})
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
assert "giọng trung-cao sáng vừa" in result.prompt.tags_vi
assert "câu hát có khoảng thở tự nhiên" in result.prompt.tags_vi
assert "Đường cong năng lượng" in result.prompt.tags_vi
assert "điệp khúc mở rộng" in result.prompt.tags_vi
assert "chưa phân tích chi tiết" not in result.prompt.tags_vi
```

- [ ] **Step 2: Run test to verify it fails**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_prompting.py -q`

Expected: FAIL because `VocalAnalysis` and `TrackAnalysis` do not accept the new fields.

- [ ] **Step 3: Add optional model fields**

In `models.py`, add defaults:

```python
class TrackAnalysis(BaseModel):
    ...
    energy_curve: str = "giu deu"
    section_hint: str = "verse tối giản, điệp khúc mở rộng"
    chorus_lift: str = "vua"

class VocalAnalysis(BaseModel):
    ...
    density: str = "can bang"
    phrasing: str = "câu hát có khoảng thở tự nhiên"
    presence: str = "can bang"
```

- [ ] **Step 4: Run prompt test**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_prompting.py -q`

Expected: The model construction issue is gone; prompt assertions may still fail until Task 4.

### Task 2: Vocal Analyzer

**Files:**
- Create: `apps/api/src/media_agent_lab_api/vocal_analyzer.py`
- Create: `apps/api/tests/test_vocal_analyzer.py`

- [ ] **Step 1: Write failing test**

Create `test_vocal_analyzer.py`:

```python
from pathlib import Path

import numpy as np
import soundfile as sf

from media_agent_lab_api.vocal_analyzer import analyze_vocal


def test_analyze_vocal_returns_prompt_safe_vocal_detail(tmp_path: Path):
    sr = 22050
    t = np.linspace(0, 2.0, sr * 2, endpoint=False)
    audio = 0.18 * np.sin(2 * np.pi * 220.0 * t)
    path = tmp_path / "vocals.wav"
    sf.write(path, audio, sr)

    result = analyze_vocal(path)

    assert result.median_pitch_hz > 150
    assert result.range_bucket in {"trung", "trung-cao", "cao"}
    assert "giọng" in result.voice_descriptor
    assert result.density in {"thoang", "can bang", "day"}
    assert "câu hát" in result.phrasing
    assert result.presence in {"lui", "can bang", "noi bat"}
    assert "ca sĩ" not in result.voice_descriptor.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_vocal_analyzer.py -q`

Expected: FAIL with `ModuleNotFoundError: media_agent_lab_api.vocal_analyzer`.

- [ ] **Step 3: Implement analyzer**

Implement `analyze_vocal(path: Path) -> VocalAnalysis` using librosa load, `librosa.pyin`, spectral centroid, RMS, voiced ratio, and small helper bucket functions.

- [ ] **Step 4: Run vocal analyzer test**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_vocal_analyzer.py -q`

Expected: PASS.

### Task 3: Structure Analyzer

**Files:**
- Create: `apps/api/src/media_agent_lab_api/structure_analyzer.py`
- Create: `apps/api/tests/test_structure_analyzer.py`

- [ ] **Step 1: Write failing test**

Create `test_structure_analyzer.py`:

```python
from pathlib import Path

import numpy as np
import soundfile as sf

from media_agent_lab_api.structure_analyzer import analyze_structure


def test_analyze_structure_detects_rising_energy_curve(tmp_path: Path):
    sr = 22050
    third = sr
    audio = np.concatenate([
        np.full(third, 0.02),
        np.full(third, 0.06),
        np.full(third, 0.18),
    ])
    path = tmp_path / "mix.wav"
    sf.write(path, audio, sr)

    result = analyze_structure(path)

    assert result["energy_curve"] == "tang dan"
    assert result["chorus_lift"] == "manh"
    assert "điệp khúc" in result["section_hint"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_structure_analyzer.py -q`

Expected: FAIL with `ModuleNotFoundError: media_agent_lab_api.structure_analyzer`.

- [ ] **Step 3: Implement analyzer**

Implement `analyze_structure(path: Path) -> dict[str, str]` using librosa RMS and three-region energy comparison.

- [ ] **Step 4: Run structure analyzer test**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_structure_analyzer.py -q`

Expected: PASS.

### Task 4: Prompt Rendering

**Files:**
- Modify: `apps/api/src/media_agent_lab_api/prompting.py`
- Test: `apps/api/tests/test_prompting.py`

- [ ] **Step 1: Run prompt test to verify current failure**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_prompting.py -q`

Expected: FAIL on missing real vocal/structure prompt text.

- [ ] **Step 2: Update prompt builder**

Update `_build_ace_prompt()` so the vocal section includes `voice_descriptor`, `phrasing`, `density`, and `presence`, and add a structure sentence using `energy_curve`, `section_hint`, and `chorus_lift`.

- [ ] **Step 3: Run prompt test**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_prompting.py -q`

Expected: PASS.

### Task 5: Pipeline Integration

**Files:**
- Modify: `apps/api/src/media_agent_lab_api/pipeline.py`
- Modify: `apps/api/tests/test_pipeline.py`

- [ ] **Step 1: Write failing pipeline test**

Extend the `AudioPipeline` test to inject:

```python
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
```

Pass them into `AudioPipeline(...)`, then assert metadata contains `"giọng trung-cao sáng vừa"` and `"Đường cong năng lượng"`.

- [ ] **Step 2: Run pipeline test to verify it fails**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_pipeline.py -q`

Expected: FAIL because `AudioPipeline.__init__` does not accept the new analyzers.

- [ ] **Step 3: Implement pipeline integration**

Add injected dependencies, call `store.update_status(job_id, JobStatus.ANALYZING_VOCAL)`, analyze vocals from `stems.vocals`, merge structure fields into `track`, and call `build_analysis_result(track, vocal=vocal)`.

- [ ] **Step 4: Run pipeline test**

Run: `..\..\.venv\Scripts\python.exe -m pytest tests\test_pipeline.py -q`

Expected: PASS.

### Task 6: Full Verification and Commit

**Files:**
- Verify all changed files

- [ ] **Step 1: Run API tests**

Run: `npm.cmd run api:test`

Expected: all tests pass.

- [ ] **Step 2: Run web build**

Run: `npm.cmd run web:build`

Expected: TypeScript and Vite build pass.

- [ ] **Step 3: Inspect sample prompt**

Run:

```powershell
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe -c "from media_agent_lab_api.prompting import build_mock_analysis_result; print(build_mock_analysis_result().prompt.tags_vi)"
```

Expected: prompt is Vietnamese with diacritics and includes vocal/structure guidance.

- [ ] **Step 4: Commit and push**

```powershell
git -c safe.directory=D:/Working/Projects/code-to-earns/media-agent-lab add apps/api/src/media_agent_lab_api apps/api/tests docs/superpowers/plans/2026-06-29-vocal-structure-prompt.md
git -c safe.directory=D:/Working/Projects/code-to-earns/media-agent-lab commit -m "feat: add vocal structure prompt analysis"
git -c safe.directory=D:/Working/Projects/code-to-earns/media-agent-lab push origin main
```
