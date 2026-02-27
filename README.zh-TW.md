# LocalMeetingTranscriber（本地會議轉錄器）

> [English README](README.md)

在本機將 `.m4a` 會議錄音轉換成 Word（`.docx`）逐字稿的桌面應用程式 — 完全離線，資料不上傳雲端，保護隱私。

使用 Python + PySide6 開發。語音辨識採用 [whisper.cpp](https://github.com/ggerganov/whisper.cpp)；選用 [Ollama](https://ollama.ai) 進行 AI 潤飾。

---

## 功能特色

- **原生 macOS GUI**，可捲動介面，支援英文 / 繁體中文切換
- **首次啟動設定精靈** — 引導完成 whisper.cpp 設定、模型下載及 Ollama 狀態確認
- **四種輸出模式**：
  1. 完整轉錄（含時間戳記）
  2. 純淨轉錄（不含時間戳記）
  3. 潤飾轉錄（Ollama LLM）
  4. 潤飾轉錄＋原始附錄（Ollama LLM）
- **繁體中文輸出** — 透過 OpenCC `s2twp` 自動將 whisper 輸出的簡體字轉換為臺灣繁體，並處理詞彙慣用法（如「软件→軟體」「内存→記憶體」）
- 批次處理 — 一次加入多個 `.m4a` 檔案，可分別編輯標題與日期
- 匯出可直接分享的 `.docx` 檔案
- 設定自動儲存（`config.json`）
- 也提供 CLI 指令（`lmt`）

---

## 系統需求

| 相依套件 | 用途 | 安裝方式 |
|---|---|---|
| Python 3.11+ | 執行環境 | [python.org](https://www.python.org) |
| ffmpeg | 音訊格式轉換 | `brew install ffmpeg` |
| whisper.cpp | 語音辨識 | `brew install whisper-cpp` |
| Ollama | LLM 潤飾（僅模式 3、4 需要） | [ollama.ai](https://ollama.ai) |

> **注意：** 本應用程式需要 **whisper.cpp** 的執行檔（`whisper-cli`），不是 Python 的 `openai-whisper` 套件。設定精靈會自動偵測並在設定錯誤時警告。

---

## 快速開始

### 1. 安裝 Python 相依套件

```bash
git clone https://github.com/trnet4334/LocalMeetingTranscriber.git
cd LocalMeetingTranscriber
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 安裝系統相依套件

```bash
# macOS（Homebrew）
brew install ffmpeg whisper-cpp

# 下載 Ollama 模型（僅模式 3、4 需要）
ollama pull qwen2.5:7b-instruct-q4_K_M
```

### 3. 啟動 GUI

```bash
python -m localmeetingtranscriber.gui.app
```

或安裝後直接執行：

```bash
pip install -e ".[gui]"
lmt-gui
```

**首次啟動**會自動顯示設定精靈，協助您：
- 找到 `whisper-cli` 執行檔位置
- 下載 Whisper 模型（預設：Small，約 466 MB）
- 確認 Ollama 執行狀態

---

## Whisper 模型選擇

精靈提供五個模型供選擇，模型越大越精確但速度較慢：

| 模型 | 大小 | 精確度 | 適用情境 |
|---|---|---|---|
| Tiny | ~75 MB | 基礎 | 快速草稿 |
| Base | ~142 MB | 普通 | 短會議 |
| **Small** | **~466 MB** | **良好** | **預設 — 速度與精確度平衡** |
| Medium | ~1.5 GB | 較好 | 較長會議 |
| Large-v3 Q5 | ~1.1 GB | 最好 | 高精確度需求 |

透過 Homebrew 安裝時，執行檔位於 `/usr/local/bin/whisper-cli`。

---

## 介面說明

```
┌────────────────────────────────────────────┐  語言：[繁體中文 ▼]
│  輸入檔案                                  │
│  ┌──────────────────────────────────────┐  │
│  │  會議錄音_2026-03-01.m4a             │  │
│  └──────────────────────────────────────┘  │
│  [新增檔案…]  [移除選取]                  │
│                                            │
│  輸出設定                                  │
│  模式：         [1. 完整轉錄（含時…） ▼]  │
│  輸出資料夾：   /Users/…/Downloads [瀏覽] │
│                                            │
│  相依性設定                                │
│  ffmpeg：        ffmpeg                    │
│  whisper.cpp 執行檔：/usr/local/bin/…     │
│  Whisper 模型：  …/models/ggml-small.bin  │
│  Ollama 模型：   qwen2.5:7b-instruct-…   │
│                                            │
│  會議資訊（可編輯）                        │
│  ┌──────┬────────────────────┬──────────┐  │
│  │ 檔案 │ 標題               │ 日期     │  │
│  └──────┴────────────────────┴──────────┘  │
│                                            │
│                     [開始處理]  [取消]    │
│  進度 ─────────────────────────────────── │
│  日誌 ─────────────────────────────────── │
└────────────────────────────────────────────┘
```

---

## CLI 使用方式

也提供文字介面（CLI）供無 GUI 環境或進階使用：

```bash
# 互動式執行
python -m localmeetingtranscriber.main

# 或透過安裝的指令
lmt
```

CLI 會依序詢問：檔案選擇、輸出模式、會議標題、日期。

---

## 專案結構

```
LocalMeetingTranscriber/
├── localmeetingtranscriber/
│   ├── gui/
│   │   ├── app.py           # 進入點 — 設定精靈 + 主視窗
│   │   ├── main_window.py   # 主 GUI 視窗
│   │   ├── worker.py        # QThread 流程工作執行緒
│   │   ├── setup_wizard.py  # 首次啟動精靈
│   │   ├── downloader.py    # 模型下載執行緒
│   │   └── i18n.py          # 英文 / 繁體中文翻譯
│   ├── pipeline.py          # 共用流程（CLI + GUI）
│   ├── transcriber.py       # whisper.cpp 包裝器 + 二進位偵測
│   ├── converter.py         # ffmpeg WAV 轉換
│   ├── postprocess.py       # SRT 解析
│   ├── exporter.py          # DOCX 匯出
│   ├── llm_polisher.py      # Ollama 整合
│   ├── config.py            # 設定讀寫
│   └── main.py              # CLI 進入點
├── models/                  # 下載的 Whisper 模型檔案
├── tests/
├── config.json
├── requirements.txt
├── pyproject.toml
├── README.md
└── README.zh-TW.md
```

---

## 設定檔說明（`config.json`）

```json
{
  "ffmpeg_path": "ffmpeg",
  "whisper_cpp_path": "/usr/local/bin/whisper-cli",
  "whisper_model_path": "./models/ggml-small.bin",
  "ollama_model": "qwen2.5:7b-instruct-q4_K_M",
  "output_dir": "./output_docx",
  "last_mode": 1,
  "language": "zh-TW"
}
```

所有欄位均可在 GUI 的「相依性設定」和「輸出設定」中修改，關閉時自動儲存。

---

## 疑難排解

| 問題現象 | 解決方式 |
|---|---|
| `找不到 ffmpeg` | `brew install ffmpeg` 或在設定中更新 `ffmpeg_path` |
| 精靈顯示「openai-whisper」警告 | 安裝 whisper.cpp：`brew install whisper-cpp` |
| 找不到 `whisper-cli` | 在 GUI 或 config.json 中設定為 `/usr/local/bin/whisper-cli` |
| 找不到模型檔案 | 重新執行精靈下載，或在 config 中更新 `whisper_model_path` |
| 輸出仍是簡體中文 | 請更新至最新版本 — 已自動套用 OpenCC 轉換 |
| Ollama 相關錯誤 | 先執行 `ollama serve`，再 `ollama pull qwen2.5:7b-instruct-q4_K_M` |
| 中文被誤識別為日文 | 已修正 — 最新版本固定傳入 `-l zh` 參數 |

---

## 執行測試

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

共 55 個測試，涵蓋流程邏輯、GUI 元件、設定精靈及模型下載器。

---

## 授權

MIT
