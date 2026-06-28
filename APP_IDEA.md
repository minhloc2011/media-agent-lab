# Idea: Audio Intelligence Prompt Builder

## Muc tieu

Xay dung ung dung phan tich file nhac dau vao va tu dong sinh prompt chat luong cao cho ACE-Step. Ung dung nhan file MP3 tu nguoi dung, tach cac thanh phan am thanh, trich xuat dac trung am nhac, phan tich vocal, sau do tong hop thanh mot prompt co the dung de tai tao hoac remix phong cach bai hat.

Vi du output prompt:

```text
Vietnamese pop ballad, male high tenor vocal, bright timbre, 82 BPM, A minor, piano, soft drums, emotional chorus
```

## Nguoi dung muc tieu

- Producer muon phan tich nhanh reference track.
- Nhac si muon bien mot bai hat mau thanh prompt tao nhac.
- Creator muon tao prompt nhac nhat quan tu file audio san co.
- Developer muon co pipeline metadata de ket noi voi ACE-Step hoac cac music generation model khac.

## Pipeline xu ly

1. User upload MP3
   - Nguoi dung tai len file `.mp3`.
   - He thong luu file vao storage tam thoi hoac object storage.
   - Kiem tra dung luong, duration, dinh dang, va loi decode co ban.

2. Convert MP3 sang WAV bang FFmpeg
   - Chuyen file dau vao ve WAV de cac cong cu phan tich xu ly on dinh hon.
   - De xuat format:

```bash
ffmpeg -i input.mp3 -ar 44100 -ac 2 output.wav
```

3. Tach stem bang Demucs
   - Chay Demucs tren file WAV full mix.
   - Output gom:
     - `vocals.wav`
     - `drums.wav`
     - `bass.wav`
     - `other.wav`
   - Cac stem nay dung cho phan tich rieng tung thanh phan, dac biet la vocal.

4. Phan tich full mix bang Essentia
   - Chay Essentia tren ban full mix de lay metadata tong the:
     - Key
     - Scale
     - BPM
     - Chords
     - Danceability
     - Mood
     - Genre
     - Voice/instrumental estimate
     - Timbre

5. Pitch detection tren vocal stem
   - Chay pitch detection tren `vocals.wav`.
   - Trich xuat cac dac trung vocal:
     - `vocal_range`
     - `median_pitch`
     - Gender-like estimate
     - Bright/dark estimate
     - Breathy/powerful estimate
   - Cac estimate nay chi nen xem la heuristic, khong phai ket luan sinh hoc hay nhan dang ca nhan.

6. Sinh prompt ACE-Step
   - Ket hop metadata tu full mix va vocal stem thanh prompt ngan, ro, co tinh am nhac.
   - Prompt nen gom:
     - Ngon ngu hoac thi truong am nhac neu suy luan duoc, vi du `Vietnamese`.
     - Genre, vi du `pop ballad`.
     - Vocal descriptor, vi du `male high tenor vocal`.
     - Timbre, vi du `bright timbre`.
     - BPM va key, vi du `82 BPM, A minor`.
     - Instrumentation, vi du `piano, soft drums`.
     - Mood/structure, vi du `emotional chorus`.

## Output mong muon

Ung dung nen tra ve 3 nhom ket qua:

### 1. Audio assets

- File WAV da convert.
- Stem vocals, drums, bass, other.
- Optional preview audio cho tung stem.

### 2. Metadata JSON

```json
{
  "track": {
    "bpm": 82,
    "key": "A",
    "scale": "minor",
    "chords": ["Am", "F", "C", "G"],
    "danceability": 0.42,
    "mood": ["emotional", "melancholic"],
    "genre": ["Vietnamese pop", "ballad"],
    "voice_instrumental": "voice",
    "timbre": "bright"
  },
  "vocal": {
    "vocal_range": "high tenor",
    "median_pitch_hz": 220.0,
    "gender_like_estimate": "male-like",
    "brightness": "bright",
    "power": "breathy"
  },
  "prompt": "Vietnamese pop ballad, male high tenor vocal, bright timbre, 82 BPM, A minor, piano, soft drums, emotional chorus"
}
```

### 3. ACE-Step prompt

Prompt cuoi cung can ngan gon, uu tien cac thong tin ACE-Step co kha nang dung tot:

```text
Vietnamese pop ballad, male high tenor vocal, bright timbre, 82 BPM, A minor, piano, soft drums, emotional chorus
```

## Kien truc de xuat

```text
Web UI
  -> Upload API
  -> Audio Job Queue
  -> FFmpeg Convert Worker
  -> Demucs Stem Worker
  -> Essentia Analysis Worker
  -> Vocal Pitch Analysis Worker
  -> Prompt Generator
  -> Result API
```

## Module chinh

- `upload-service`: nhan file, validate, tao job.
- `audio-converter`: goi FFmpeg de convert MP3 sang WAV.
- `stem-separator`: goi Demucs de tach vocals, drums, bass, other.
- `music-analyzer`: goi Essentia de lay metadata full mix.
- `vocal-analyzer`: chay pitch detection va heuristic vocal descriptors.
- `prompt-generator`: map metadata thanh ACE-Step prompt.
- `result-store`: luu asset path, metadata JSON, status job.

## Luong trang thai job

```text
uploaded
  -> converting
  -> separating_stems
  -> analyzing_mix
  -> analyzing_vocal
  -> generating_prompt
  -> completed
```

Trang thai loi de xuat:

```text
failed_validation
failed_convert
failed_demucs
failed_essentia
failed_pitch_detection
failed_prompt_generation
```

## Heuristic prompt mapping

| Input metadata | Prompt fragment |
| --- | --- |
| genre = Vietnamese pop, ballad | `Vietnamese pop ballad` |
| gender-like = male-like, range = high tenor | `male high tenor vocal` |
| timbre = bright | `bright timbre` |
| bpm = 82 | `82 BPM` |
| key = A, scale = minor | `A minor` |
| drums energy low | `soft drums` |
| mood = emotional | `emotional chorus` |

## Luu y ve heuristic vocal

`gender-like estimate`, `bright/dark`, va `breathy/powerful` chi la mo ta am hoc dua tren pitch, spectral centroid, harmonic/noise ratio, energy, va dynamic range. Ung dung khong nen trinh bay chung nhu nhan dang gioi tinh that cua ca si, ma nen hien thi la descriptor am thanh phuc vu prompt.

## MVP de xuat

1. Upload MP3 va convert sang WAV.
2. Chay Demucs de tao 4 stems.
3. Chay Essentia de lay BPM, key, scale, genre, mood, timbre.
4. Chay pitch detection co ban tren vocals.
5. Sinh metadata JSON va ACE-Step prompt.
6. Hien thi result page gom waveform/stems, metadata, va prompt co nut copy.

## Huong mo rong

- Cho phep user sua prompt truoc khi export.
- Sinh nhieu bien the prompt: faithful, remix, cinematic, acoustic.
- Them confidence score cho tung metadata field.
- Them cache theo audio fingerprint de tranh xu ly lai cung mot file.
- Export ket qua thanh JSON, Markdown, hoac job report.
- Ket noi truc tiep voi ACE-Step de tao audio moi tu prompt.
