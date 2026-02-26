"""Help dialog for LocalMeetingTranscriber — bilingual EN / 繁體中文."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
)

# ---------------------------------------------------------------------------
# Shared CSS injected into both HTML documents
# ---------------------------------------------------------------------------
_CSS = """
<style>
  body  { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
          font-size: 13px; color: #1a1a1a; margin: 14px 18px; line-height: 1.55; }
  h2    { font-size: 16px; margin-bottom: 4px; color: #0a4a8a; }
  h3    { font-size: 14px; font-weight: bold; margin-top: 20px; margin-bottom: 4px;
          border-bottom: 1px solid #ccd; padding-bottom: 3px; color: #909090; }
  h4    { font-size: 13px; margin-top: 12px; margin-bottom: 2px; }
  p     { margin: 6px 0; }
  code  { background: #f0f0f0; border-radius: 3px; padding: 1px 4px;
          font-family: "Menlo", "Monaco", monospace; font-size: 12px; }
  table { border-collapse: collapse; width: 100%; margin: 8px 0; }
  th    { background: #505050; color: #ffffff; text-align: left; padding: 5px 8px;
          font-size: 12px; border: 1px solid #3a3a3a; }
  td    { background: #b0b0b0; color: #111111; padding: 4px 8px; border: 1px solid #888888; vertical-align: top; }
  tr:nth-child(even) td { background: #a4a4a4; color: #111111; }
  .note { border-left: 3px solid #e8a800; padding: 4px 10px; margin: 8px 0; }
  .warn { border-left: 3px solid #d44; padding: 4px 10px; margin: 8px 0; }
  ul    { margin: 4px 0; padding-left: 20px; }
  li    { margin: 2px 0; }
</style>
"""

# ---------------------------------------------------------------------------
# English help content
# ---------------------------------------------------------------------------
_EN_HTML = (
    _CSS
    + """
<h2>LocalMeetingTranscriber — Help</h2>
<p>Converts meeting recordings (local files or video URLs) into formatted Word documents
using <b>whisper.cpp</b> for speech-to-text, with optional AI polishing via <b>Ollama</b>.</p>

<h3>Input Files</h3>
<table>
  <tr><th>Control</th><th>Description</th></tr>
  <tr><td><b>Add Files…</b></td>
      <td>Select one or more <code>.m4a</code> audio files from your disk.</td></tr>
  <tr><td><b>Add URL…</b></td>
      <td>Paste a YouTube, Vimeo, Bilibili, or direct video/audio URL.
          Audio is downloaded automatically to <code>downloaded_audio/</code>
          inside the app folder and added to the queue.</td></tr>
  <tr><td><b>Remove Selected</b></td>
      <td>Remove the highlighted row(s) from the processing queue.</td></tr>
</table>

<h3>Meeting Metadata (editable)</h3>
<p>Each queued file has three metadata columns:</p>
<table>
  <tr><th>Column</th><th>Meaning</th><th>Editable?</th></tr>
  <tr><td><b>File</b></td>
      <td>File name of the audio source (read-only).</td>
      <td>No</td></tr>
  <tr><td><b>Title</b></td>
      <td>Used as the output <code>.docx</code> filename and the document heading.
          Auto-filled from the video title (URL) or the audio file stem.
          Edit it to any text you like.</td>
      <td>Yes — double-click</td></tr>
  <tr><td><b>Date</b></td>
      <td>Meeting date written into the document header.
          Defaults to the file's modification date (or today for URL downloads).
          Format: <code>YYYY-MM-DD</code>.</td>
      <td>Yes — double-click</td></tr>
</table>

<h3>Output</h3>
<table>
  <tr><th>Field</th><th>What to fill in</th></tr>
  <tr><td><b>Output Folder</b></td>
      <td>Directory where finished <code>.docx</code> files are saved.
          Click <i>Browse…</i> to change it.
          Default: <code>&lt;app folder&gt;/output_docx/</code></td></tr>
  <tr><td><b>Mode</b></td>
      <td>Controls what the output document contains (see <i>Processing Modes</i> below).</td></tr>
</table>

<h3>Processing Modes</h3>
<table>
  <tr><th>#</th><th>Name</th><th>Description</th><th>Ollama required?</th></tr>
  <tr><td><b>1</b></td><td>Full transcript with timestamps</td>
      <td>Every sentence with its time code (<code>[00:01:23]</code>).
          Best for reference or searchability.</td><td>No</td></tr>
  <tr><td><b>2</b></td><td>Clean transcript</td>
      <td>Same text as Mode 1 but with all time codes stripped.
          Easier to read as continuous prose.</td><td>No</td></tr>
  <tr><td><b>3</b></td><td>Polished transcript (Ollama)</td>
      <td>The raw transcript is sent to Ollama for grammar correction,
          punctuation, and readability improvements.
          Output is the AI-polished version only.</td><td><b>Yes</b></td></tr>
  <tr><td><b>4</b></td><td>Polished + raw appendix (Ollama)</td>
      <td>Same as Mode 3, but the original unedited transcript is appended
          at the end of the document for reference.</td><td><b>Yes</b></td></tr>
</table>
<div class="note">
  <b>Tip:</b> Use Mode 1 or 2 for a quick turnaround without Ollama.
  Use Mode 3 or 4 when you need a clean, polished document.
</div>

<h3>Dependencies</h3>
<table>
  <tr><th>Field</th><th>What to fill in</th></tr>
  <tr><td><b>ffmpeg</b></td>
      <td>Path to the <code>ffmpeg</code> executable.
          Common locations:<br>
          &nbsp;• <code>/usr/local/bin/ffmpeg</code><br>
          &nbsp;• <code>/opt/homebrew/bin/ffmpeg</code><br>
          If <code>ffmpeg</code> is on your PATH, just type <code>ffmpeg</code>.</td></tr>
  <tr><td><b>whisper.cpp binary</b></td>
      <td>Path to the <b>whisper.cpp</b> executable.
          Homebrew installs it as <code>/usr/local/bin/whisper-cli</code>.<br>
          Use the Setup Wizard (re-launch app after removing the binary path)
          to locate it.<br>
          <b>⚠ Must be whisper.cpp, not the Python openai-whisper package.</b></td></tr>
  <tr><td><b>Whisper model</b></td>
      <td>Path to a <code>.bin</code> model file, e.g.
          <code>/Users/you/models/ggml-small.bin</code>.
          Download one via the Setup Wizard.</td></tr>
  <tr><td><b>Ollama model</b></td>
      <td>Name of the Ollama model used for transcript polishing, e.g.
          <code>llama3</code>, <code>qwen2.5:7b-instruct-q4_K_M</code>.
          Only required for Modes 3 &amp; 4. Ollama must be running.</td></tr>
</table>
<div class="warn">
  <b>Requirement:</b> The whisper.cpp binary must be the C++ version, not
  <code>pip install openai-whisper</code>.
  The app will detect the wrong binary and show an error before processing starts.
</div>

<h3>Whisper Models — Comparison</h3>
<p>All models output Chinese and automatically convert Simplified → Traditional Chinese (Taiwan).</p>
<table>
  <tr><th>Model</th><th>File</th><th>Size</th><th>Speed</th><th>Accuracy</th><th>Best for</th></tr>
  <tr><td>Tiny</td><td><code>ggml-tiny.bin</code></td>
      <td>~75 MB</td><td>Fastest</td><td>Basic</td>
      <td>Quick drafts, testing</td></tr>
  <tr><td>Base</td><td><code>ggml-base.bin</code></td>
      <td>~142 MB</td><td>Fast</td><td>Fair</td>
      <td>Short informal meetings</td></tr>
  <tr><td><b>Small ★</b></td><td><code>ggml-small.bin</code></td>
      <td>~466 MB</td><td>Moderate</td><td>Good</td>
      <td><b>Default — best balance for most meetings</b></td></tr>
  <tr><td>Medium</td><td><code>ggml-medium.bin</code></td>
      <td>~1.5 GB</td><td>Slow</td><td>High</td>
      <td>Important meetings with mixed accents</td></tr>
  <tr><td>Large-v3 Q5</td><td><code>ggml-large-v3-q5_0.bin</code></td>
      <td>~1.1 GB</td><td>Slowest</td><td>Best</td>
      <td>Maximum accuracy (quantised, smaller than full large)</td></tr>
</table>
<div class="note">
  <b>Recommendation:</b> Start with <b>Small</b> for everyday use.
  Upgrade to Large-v3 Q5 when accuracy is critical.
</div>

<h3>Input / Output Locations</h3>
<table>
  <tr><th>Type</th><th>Default Location</th></tr>
  <tr><td>Local audio (<code>.m4a</code>)</td>
      <td>Wherever the file lives on your disk — no copying needed.</td></tr>
  <tr><td>URL-downloaded audio</td>
      <td><code>&lt;app folder&gt;/downloaded_audio/</code><br>
          Files are named after the video title.</td></tr>
  <tr><td>Temporary SRT transcript</td>
      <td>Written next to the audio file during processing;
          not cleaned up automatically (useful for debugging).</td></tr>
  <tr><td>Output documents (<code>.docx</code>)</td>
      <td>The <b>Output Folder</b> you configured.<br>
          Default: <code>&lt;app folder&gt;/output_docx/</code></td></tr>
</table>
"""
)

# ---------------------------------------------------------------------------
# Traditional Chinese help content
# ---------------------------------------------------------------------------
_ZH_HTML = (
    _CSS
    + """
<h2>本地會議轉錄器 — 使用說明</h2>
<p>將會議錄音（本機檔案或影片網址）轉換為格式化 Word 文件，
使用 <b>whisper.cpp</b> 進行語音辨識，可選搭配 <b>Ollama</b> 進行 AI 潤飾。</p>

<h3>輸入檔案</h3>
<table>
  <tr><th>控制項</th><th>說明</th></tr>
  <tr><td><b>新增檔案…</b></td>
      <td>從硬碟選取一個或多個 <code>.m4a</code> 音訊檔案。</td></tr>
  <tr><td><b>新增網址…</b></td>
      <td>貼上 YouTube、Vimeo、Bilibili 或直接影片／音訊網址。
          系統會自動下載音訊至 App 資料夾內的 <code>downloaded_audio/</code>，
          並加入處理佇列。</td></tr>
  <tr><td><b>移除選取</b></td>
      <td>將所選的列從處理佇列中移除。</td></tr>
</table>

<h3>會議資訊（可編輯）</h3>
<p>每個已加入的檔案有三欄中繼資料：</p>
<table>
  <tr><th>欄位</th><th>意義</th><th>可編輯？</th></tr>
  <tr><td><b>檔案</b></td>
      <td>音訊來源的檔案名稱（唯讀）。</td>
      <td>否</td></tr>
  <tr><td><b>標題</b></td>
      <td>作為輸出 <code>.docx</code> 的檔名與文件標題。
          從影片標題（網址）或音訊檔名自動填入。
          可自行修改為任意文字。</td>
      <td>是 — 雙擊編輯</td></tr>
  <tr><td><b>日期</b></td>
      <td>寫入文件頁首的會議日期。
          預設為檔案修改日期（網址下載則為今日）。
          格式：<code>YYYY-MM-DD</code>。</td>
      <td>是 — 雙擊編輯</td></tr>
</table>

<h3>輸出設定</h3>
<table>
  <tr><th>欄位</th><th>填寫內容</th></tr>
  <tr><td><b>輸出資料夾</b></td>
      <td>儲存完成的 <code>.docx</code> 檔案的目錄。
          點擊<i>瀏覽…</i>可更換位置。
          預設：<code>&lt;App 資料夾&gt;/output_docx/</code></td></tr>
  <tr><td><b>模式</b></td>
      <td>決定輸出文件的內容（詳見下方「處理模式」）。</td></tr>
</table>

<h3>處理模式</h3>
<table>
  <tr><th>#</th><th>名稱</th><th>說明</th><th>需要 Ollama？</th></tr>
  <tr><td><b>1</b></td><td>完整轉錄（含時間戳記）</td>
      <td>每句話附帶時間碼（如 <code>[00:01:23]</code>）。
          適合查找特定片段或作為參考原稿。</td><td>否</td></tr>
  <tr><td><b>2</b></td><td>純淨轉錄（不含時間戳記）</td>
      <td>與模式 1 相同，但去除所有時間碼，
          讀起來更像連續文章。</td><td>否</td></tr>
  <tr><td><b>3</b></td><td>潤飾轉錄（Ollama）</td>
      <td>將原始逐字稿傳送給 Ollama，進行語法校正、
          標點補全與可讀性改善。
          輸出為 AI 潤飾後的版本。</td><td><b>是</b></td></tr>
  <tr><td><b>4</b></td><td>潤飾轉錄＋原始附錄（Ollama）</td>
      <td>同模式 3，但在文件末尾附加未經編輯的
          原始逐字稿以供對照。</td><td><b>是</b></td></tr>
</table>
<div class="note">
  <b>提示：</b>不需要 Ollama 時請使用模式 1 或 2 快速產出。
  需要整潔可讀文件時使用模式 3 或 4。
</div>

<h3>相依性設定</h3>
<table>
  <tr><th>欄位</th><th>填寫內容</th></tr>
  <tr><td><b>ffmpeg</b></td>
      <td>ffmpeg 執行檔路徑。常見位置：<br>
          &nbsp;• <code>/usr/local/bin/ffmpeg</code><br>
          &nbsp;• <code>/opt/homebrew/bin/ffmpeg</code><br>
          若 <code>ffmpeg</code> 已在 PATH 中，直接填 <code>ffmpeg</code> 即可。</td></tr>
  <tr><td><b>whisper.cpp 執行檔</b></td>
      <td>whisper.cpp 執行檔路徑。
          Homebrew 安裝後通常為 <code>/usr/local/bin/whisper-cli</code>。<br>
          可透過設定精靈重新指定（移除路徑後重新啟動 App）。<br>
          <b>⚠ 必須是 whisper.cpp，不可使用 Python 版 openai-whisper。</b></td></tr>
  <tr><td><b>Whisper 模型</b></td>
      <td>模型 <code>.bin</code> 檔案路徑，例如
          <code>/Users/you/models/ggml-small.bin</code>。
          可透過設定精靈下載。</td></tr>
  <tr><td><b>Ollama 模型</b></td>
      <td>用於潤飾逐字稿的 Ollama 模型名稱，例如
          <code>llama3</code>、<code>qwen2.5:7b-instruct-q4_K_M</code>。
          僅模式 3 和 4 需要，且 Ollama 服務必須正在執行。</td></tr>
</table>
<div class="warn">
  <b>注意：</b>whisper.cpp 執行檔必須是 C++ 版本，
  不可使用 <code>pip install openai-whisper</code> 安裝的版本。
  App 啟動時會自動偵測並在處理前顯示錯誤。
</div>

<h3>Whisper 模型比較</h3>
<p>所有模型均輸出中文，並自動將簡體中文轉換為繁體中文（台灣標準）。</p>
<table>
  <tr><th>模型</th><th>檔案名稱</th><th>大小</th><th>速度</th><th>準確度</th><th>適用情境</th></tr>
  <tr><td>Tiny</td><td><code>ggml-tiny.bin</code></td>
      <td>~75 MB</td><td>最快</td><td>基本</td>
      <td>快速草稿、測試用</td></tr>
  <tr><td>Base</td><td><code>ggml-base.bin</code></td>
      <td>~142 MB</td><td>快</td><td>尚可</td>
      <td>短會議、非正式場合</td></tr>
  <tr><td><b>Small ★</b></td><td><code>ggml-small.bin</code></td>
      <td>~466 MB</td><td>中等</td><td>良好</td>
      <td><b>預設值 — 大多數會議的最佳平衡點</b></td></tr>
  <tr><td>Medium</td><td><code>ggml-medium.bin</code></td>
      <td>~1.5 GB</td><td>慢</td><td>高</td>
      <td>重要會議、多種口音</td></tr>
  <tr><td>Large-v3 Q5</td><td><code>ggml-large-v3-q5_0.bin</code></td>
      <td>~1.1 GB</td><td>最慢</td><td>最佳</td>
      <td>最高準確度（量化版，比完整 large 更小）</td></tr>
</table>
<div class="note">
  <b>建議：</b>日常使用以 <b>Small</b> 為主。
  準確度要求高時升級為 Large-v3 Q5。
</div>

<h3>輸入／輸出位置</h3>
<table>
  <tr><th>類型</th><th>預設位置</th></tr>
  <tr><td>本機音訊（<code>.m4a</code>）</td>
      <td>檔案原本所在位置，無需複製。</td></tr>
  <tr><td>網址下載的音訊</td>
      <td><code>&lt;App 資料夾&gt;/downloaded_audio/</code><br>
          檔名以影片標題命名。</td></tr>
  <tr><td>暫存 SRT 逐字稿</td>
      <td>處理期間寫入音訊檔旁邊，
          處理完成後不會自動刪除（方便除錯）。</td></tr>
  <tr><td>輸出文件（<code>.docx</code>）</td>
      <td>您設定的<b>輸出資料夾</b>。<br>
          預設：<code>&lt;App 資料夾&gt;/output_docx/</code></td></tr>
</table>
"""
)


# ---------------------------------------------------------------------------
# Dialog class
# ---------------------------------------------------------------------------

class HelpDialog(QDialog):
    """Bilingual help dialog with English and Traditional Chinese tabs."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Help / 使用說明")
        self.resize(720, 580)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        tabs = QTabWidget()

        en_browser = QTextBrowser()
        en_browser.setHtml(_EN_HTML)
        en_browser.setOpenExternalLinks(True)
        tabs.addTab(en_browser, "English")

        zh_browser = QTextBrowser()
        zh_browser.setHtml(_ZH_HTML)
        zh_browser.setOpenExternalLinks(True)
        tabs.addTab(zh_browser, "繁體中文")

        close_btn = QPushButton("Close / 關閉")
        close_btn.setFixedWidth(140)
        close_btn.clicked.connect(self.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addLayout(btn_row)
