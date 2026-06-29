# Phase 3 Vocal and Structure Prompt Design

## Goal

Improve the ACE-ready prompt by replacing generic vocal fallback text with real vocal-stem analysis and adding lightweight structure/energy guidance derived from the reference mix.

## Context

The current Phase 2 pipeline can upload an MP3, convert it to WAV, split stems with Demucs, analyze the full mix with librosa, and generate a Vietnamese prompt with diacritics. Real testing showed the output is usable, but still contains a weak phrase:

> Giọng hát: giọng hát chưa phân tích chi tiết

This happens because the pipeline passes only `TrackAnalysis` into `build_analysis_result()`. `VocalAnalysis` exists in the model, but production code does not populate it from the Demucs vocal stem.

## Scope

Phase 3 will add local heuristic analysis using existing dependencies:

- Vocal stem analysis from `stems/vocals.mp3`
- Full-mix structure and energy hints from `audio/input.wav`
- Prompt sections that consume the new vocal and structure data

Phase 3 will not add faster-whisper yet. Language detection and lyric transcription remain later work because the immediate quality bottleneck is vocal/arrangement detail, not text transcription.

## User Outcome

After uploading the same MP3, the copied ACE prompt should describe:

- vocal register and energy without guessing singer identity or gender
- vocal brightness and presence
- phrasing density and amount of breathing space
- reference energy curve
- section guidance for verse, pre-chorus, and chorus
- how to adapt melody for new Vietnamese lyrics

The prompt should remain a single copyable Vietnamese string in `prompt.tags_vi`.

## Data Model

`VocalAnalysis` will be extended with optional descriptive fields:

- `density`: one of `thoang`, `can bang`, `day`
- `phrasing`: a Vietnamese phrase such as `câu hát có khoảng thở rõ`
- `presence`: one of `lui`, `can bang`, `noi bat`

`TrackAnalysis` will be extended with optional structure fields:

- `energy_curve`: one of `giu deu`, `tang dan`, `cao trao ro`, `giam dan`
- `section_hint`: a Vietnamese phrase describing the likely arrangement arc
- `chorus_lift`: one of `nhe`, `vua`, `manh`

The existing API response shape remains backward compatible because Pydantic models will provide defaults for the new fields.

## Vocal Analyzer

Create `apps/api/src/media_agent_lab_api/vocal_analyzer.py`.

The analyzer loads the vocal stem with librosa, mono, preserving sample rate. It computes:

- median pitch with `librosa.pyin` when voiced frames exist
- range bucket from voiced pitch spread
- brightness from spectral centroid
- power from RMS
- density from voiced-frame ratio and RMS activity
- presence from RMS and brightness
- phrasing from density

The analyzer must not infer gender, age, singer name, singer identity, or biometric identity. Output labels describe musical qualities only.

If pitch cannot be estimated, it returns a safe fallback descriptor that still reflects brightness/power/density when possible.

## Structure Analyzer

Create `apps/api/src/media_agent_lab_api/structure_analyzer.py`.

The analyzer loads the full mix and computes RMS over frames. It divides the track into three broad regions:

- early third
- middle third
- late third

It compares region energy to produce:

- `energy_curve`
- `chorus_lift`
- `section_hint`

This is not a full structural transcription. It is a heuristic prompt aid. The prompt should say "tham chiếu" or phrase the guidance musically, not claim exact section boundaries.

## Pipeline Flow

Current flow:

1. Convert upload to WAV
2. Separate stems
3. Analyze mix
4. Generate prompt

New flow:

1. Convert upload to WAV
2. Separate stems
3. Analyze mix
4. Analyze vocal stem
5. Analyze structure from full mix
6. Merge structure fields into `TrackAnalysis`
7. Generate prompt with both `track` and `vocal`

The pipeline should update status to `ANALYZING_VOCAL` before vocal analysis. Structure analysis can happen under the same status or immediately before prompt generation because there is no separate status enum today for structure.

## Prompt Behavior

The prompt builder will use the real `VocalAnalysis` when available.

The vocal section should change from:

> Giọng hát: giọng hát chưa phân tích chi tiết

to a richer phrase, for example:

> Giọng hát: giọng trung-cao, sáng vừa, lực hát rõ, hiện diện nổi bật; câu hát cân bằng, có khoảng thở tự nhiên, ưu tiên phát âm rõ chữ và ngân nhẹ ở cuối câu.

The structure section should add guidance like:

> Đường cong năng lượng tăng dần, verse giữ tối giản, pre-chorus nâng bằng pad hoặc piano, điệp khúc mở mạnh hơn với hook dễ nhớ.

The prompt must continue to avoid:

- named artist mimicry
- gender claims
- biometric identity claims
- overconfident exact structure claims

## Testing Requirements

Add tests before production code:

- `test_vocal_analyzer.py`: synthetic vocal-like sine signal returns non-generic vocal descriptor, density, phrasing, and presence.
- `test_structure_analyzer.py`: synthetic audio with louder final third returns rising energy curve and stronger chorus lift.
- `test_pipeline.py`: fake analyzers prove pipeline passes vocal analysis into prompt generation and writes it to metadata.
- `test_prompting.py`: prompt includes vocal detail and structure detail, and no longer includes the generic "chưa phân tích chi tiết" phrase when real vocal data exists.

All existing API and web verification commands must still pass:

- `npm.cmd run api:test`
- `npm.cmd run web:build`

## Acceptance Criteria

- Uploading a real MP3 produces a prompt with a specific vocal section.
- Prompt includes energy/structure guidance.
- Prompt remains Vietnamese with diacritics.
- Prompt remains safe: no identity, no gender, no artist mimicry.
- Existing API response contract remains usable by the current frontend.
- Full test suite passes.
