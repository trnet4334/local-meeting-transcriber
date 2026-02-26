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
    },
}
