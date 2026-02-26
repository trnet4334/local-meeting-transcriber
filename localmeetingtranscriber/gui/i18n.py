"""Translations for LocalMeetingTranscriber GUI.

Supported language codes:
  en    – English
  zh-TW – Traditional Chinese (繁體中文)
"""
from __future__ import annotations

LANGUAGES: dict[str, str] = {
    "en": "English",
    "zh-TW": "繁體中文",
}

DEFAULT_LANGUAGE = "en"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Window / app
        "window_title": "LocalMeetingTranscriber",
        "lang_label": "Language:",
        # Group boxes
        "group_input": "Input Files",
        "group_output": "Output",
        "group_deps": "Dependencies",
        "group_metadata": "Meeting Metadata (editable)",
        "group_progress": "Progress",
        "group_log": "Log",
        # Buttons
        "btn_add": "Add Files…",
        "btn_remove": "Remove Selected",
        "btn_browse": "Browse…",
        "btn_start": "Start Processing",
        "btn_cancel": "Cancel",
        # Form labels
        "lbl_mode": "Mode:",
        "lbl_output_folder": "Output Folder:",
        "lbl_ffmpeg": "ffmpeg:",
        "lbl_whisper_bin": "whisper.cpp binary:",
        "lbl_whisper_model": "Whisper model:",
        "lbl_ollama_model": "Ollama model:",
        "lbl_overall": "Overall:",
        "lbl_current_step": "Current step:",
        "lbl_done": "Done",
        "lbl_error": "Error",
        # Table columns
        "col_file": "File",
        "col_title": "Title",
        "col_date": "Date",
        # Mode descriptions
        "mode_1": "1. Full transcript with timestamps",
        "mode_2": "2. Clean transcript without timestamps",
        "mode_3": "3. Polished transcript (Ollama)",
        "mode_4": "4. Polished transcript + raw appendix (Ollama)",
        # Dialogs
        "dlg_dep_error_title": "Dependency Error",
        "dlg_done_title": "Done",
        "dlg_done_body": "All files processed successfully.",
        "dlg_pipeline_error_title": "Pipeline Error",
        "dlg_select_audio": "Select .m4a Audio Files",
        "dlg_select_output_folder": "Select Output Folder",
        "dlg_select_whisper_bin": "Select whisper.cpp Binary",
        "dlg_select_whisper_model": "Select whisper.cpp Model (.bin)",
        "dlg_model_filter": "Model Files (*.bin);;All Files (*)",
        "dlg_audio_filter": "Audio Files (*.m4a)",
        # Log messages
        "log_processing": "Processing",
        "log_cancel": "Cancellation requested",
        "log_saved": "Saved",
        "log_all_done": "All files processed successfully.",
        "log_error": "Error",
        # ── Setup Wizard ────────────────────────────────────────────────
        "wizard_title": "Setup Wizard",
        # Welcome page
        "wizard_welcome_title": "Welcome to LocalMeetingTranscriber",
        "wizard_welcome_subtitle": "Let's configure the required tools",
        "wizard_welcome_body": (
            "This wizard will help you set up:\n\n"
            "  • whisper.cpp — the speech-to-text engine\n"
            "  • Whisper model — the AI model file\n"
            "  • Ollama — optional, needed for polished transcript modes (3 & 4)\n\n"
            "Click Next to begin."
        ),
        # whisper.cpp binary page
        "wizard_binary_title": "whisper.cpp Binary",
        "wizard_binary_subtitle": "Locate the whisper.cpp executable",
        "wizard_binary_status_ok": "✓  Binary found",
        "wizard_binary_status_missing": "Binary not found — please browse to the whisper.cpp executable",
        "wizard_binary_path_label": "Path:",
        "wizard_binary_placeholder": "/path/to/whisper.cpp/main",
        # Model download page
        "wizard_model_title": "Whisper Model",
        "wizard_model_subtitle": "Download or locate a whisper.cpp model file",
        "wizard_model_status_ok": "✓  Model found",
        "wizard_model_status_missing": "Model not found — download below or locate an existing .bin file",
        "wizard_model_select_label": "Model:",
        "wizard_model_save_to_label": "Download to:",
        "wizard_model_btn_download": "Download",
        "wizard_model_btn_locate": "Locate existing…",
        "wizard_model_downloading": "Downloading…",
        "wizard_model_cancel": "Cancel",
        "wizard_model_dl_error_title": "Download Error",
        "wizard_model_dl_dir_title": "Select Download Folder",
        # Ollama page
        "wizard_ollama_title": "Ollama (Optional)",
        "wizard_ollama_subtitle": "Required only for modes 3 and 4",
        "wizard_ollama_status_ok": "✓  Ollama is running",
        "wizard_ollama_status_missing": "Ollama not detected",
        "wizard_ollama_note": (
            "Ollama is only needed for polished transcript modes (3 & 4).\n"
            "You can install it later — click Next to continue."
        ),
        "wizard_ollama_btn_check": "Check again",
        "wizard_ollama_btn_open": "Open ollama.ai",
        # Finish page
        "wizard_finish_title": "Setup Complete",
        "wizard_finish_subtitle": "You're ready to start transcribing",
        "wizard_finish_body": (
            "All required components are configured.\n\n"
            "Click Finish to open the main window."
        ),
    },
    "zh-TW": {
        # Window / app
        "window_title": "本地會議轉錄器",
        "lang_label": "語言：",
        # Group boxes
        "group_input": "輸入檔案",
        "group_output": "輸出設定",
        "group_deps": "相依性設定",
        "group_metadata": "會議資訊（可編輯）",
        "group_progress": "進度",
        "group_log": "日誌",
        # Buttons
        "btn_add": "新增檔案…",
        "btn_remove": "移除選取",
        "btn_browse": "瀏覽…",
        "btn_start": "開始處理",
        "btn_cancel": "取消",
        # Form labels
        "lbl_mode": "模式：",
        "lbl_output_folder": "輸出資料夾：",
        "lbl_ffmpeg": "ffmpeg：",
        "lbl_whisper_bin": "whisper.cpp 執行檔：",
        "lbl_whisper_model": "Whisper 模型：",
        "lbl_ollama_model": "Ollama 模型：",
        "lbl_overall": "整體進度：",
        "lbl_current_step": "目前步驟：",
        "lbl_done": "完成",
        "lbl_error": "錯誤",
        # Table columns
        "col_file": "檔案",
        "col_title": "標題",
        "col_date": "日期",
        # Mode descriptions
        "mode_1": "1. 完整轉錄（含時間戳記）",
        "mode_2": "2. 純淨轉錄（不含時間戳記）",
        "mode_3": "3. 潤飾轉錄（Ollama）",
        "mode_4": "4. 潤飾轉錄＋原始附錄（Ollama）",
        # Dialogs
        "dlg_dep_error_title": "相依性錯誤",
        "dlg_done_title": "完成",
        "dlg_done_body": "所有檔案處理完成。",
        "dlg_pipeline_error_title": "流程錯誤",
        "dlg_select_audio": "選取 .m4a 音訊檔案",
        "dlg_select_output_folder": "選取輸出資料夾",
        "dlg_select_whisper_bin": "選取 whisper.cpp 執行檔",
        "dlg_select_whisper_model": "選取 whisper.cpp 模型（.bin）",
        "dlg_model_filter": "模型檔案 (*.bin);;所有檔案 (*)",
        "dlg_audio_filter": "Audio Files (*.m4a)",
        # Log messages
        "log_processing": "處理中",
        "log_cancel": "已請求取消",
        "log_saved": "已儲存",
        "log_all_done": "所有檔案處理完成。",
        "log_error": "錯誤",
        # ── 設定精靈 ─────────────────────────────────────────────────────
        "wizard_title": "設定精靈",
        # 歡迎頁
        "wizard_welcome_title": "歡迎使用本地會議轉錄器",
        "wizard_welcome_subtitle": "讓我們設定所需工具",
        "wizard_welcome_body": (
            "此精靈將協助您設定：\n\n"
            "  • whisper.cpp — 語音轉文字引擎\n"
            "  • Whisper 模型 — AI 模型檔案\n"
            "  • Ollama — 選用，潤飾轉錄模式（3 & 4）需要\n\n"
            "點擊「下一步」開始。"
        ),
        # whisper.cpp 執行檔頁
        "wizard_binary_title": "whisper.cpp 執行檔",
        "wizard_binary_subtitle": "找到 whisper.cpp 執行檔位置",
        "wizard_binary_status_ok": "✓  已找到執行檔",
        "wizard_binary_status_missing": "找不到執行檔 — 請瀏覽找到 whisper.cpp 執行檔",
        "wizard_binary_path_label": "路徑：",
        "wizard_binary_placeholder": "/path/to/whisper.cpp/main",
        # 模型下載頁
        "wizard_model_title": "Whisper 模型",
        "wizard_model_subtitle": "下載或找到 whisper.cpp 模型檔案",
        "wizard_model_status_ok": "✓  已找到模型",
        "wizard_model_status_missing": "找不到模型 — 請從下方下載或找到現有 .bin 檔案",
        "wizard_model_select_label": "模型：",
        "wizard_model_save_to_label": "下載至：",
        "wizard_model_btn_download": "下載",
        "wizard_model_btn_locate": "找到現有…",
        "wizard_model_downloading": "下載中…",
        "wizard_model_cancel": "取消",
        "wizard_model_dl_error_title": "下載錯誤",
        "wizard_model_dl_dir_title": "選取下載資料夾",
        # Ollama 頁
        "wizard_ollama_title": "Ollama（選用）",
        "wizard_ollama_subtitle": "僅模式 3 和 4 需要",
        "wizard_ollama_status_ok": "✓  Ollama 正在執行",
        "wizard_ollama_status_missing": "未偵測到 Ollama",
        "wizard_ollama_note": (
            "Ollama 僅在潤飾轉錄模式（3 & 4）時需要。\n"
            "可稍後安裝 — 點擊「下一步」繼續。"
        ),
        "wizard_ollama_btn_check": "重新檢查",
        "wizard_ollama_btn_open": "開啟 ollama.ai",
        # 完成頁
        "wizard_finish_title": "設定完成",
        "wizard_finish_subtitle": "您已準備好開始轉錄",
        "wizard_finish_body": (
            "所有必要元件均已設定完成。\n\n"
            "點擊「完成」以開啟主視窗。"
        ),
    },
}
