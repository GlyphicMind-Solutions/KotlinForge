# /KotlinForge/gui/kotlinforge_window.py
# KotlinForge GUI Window (Tabbed IDE Layout)
# Created By: David Kistner (Unconditional Love) at GlyphicMind Solutions LLC.


# system imports
import re
from datetime import datetime
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QTabWidget,
)

# local imports
from engine.deep_analysis import DeepAnalysisEngine
from engine.forge_writer import ForgeWriter
from prompt.prompt_builder import PromptBuilder


# =======================================
# KOTLIN FORGE WINDOW CLASS
# =======================================
class KotlinForgeWindow(QMainWindow):
    """
    KotlinForge GUI (Tabbed IDE Layout)

    Tabs:
    - Topic / Corrections
    - Raw LLM Output
    - Extracted Code
    - Master Code
    - Deep Analysis Log

    Global controls:
    - Generate
    - Re-run with Corrections
    - Deep Analysis
    - Open File
    - Save File
    - Forge → Pending
    - Clear (New Session)
    """

    # ------------------
    # Initialize
    # ------------------
    def __init__(self, llm_engine, storage_root: Path, parent=None):
        super().__init__(parent)

        #llm/prompt/forge writer
        self.llm = llm_engine
        self.prompt_builder = PromptBuilder()
        self.forge_writer = ForgeWriter(storage_root)

        #window title/size
        self.setWindowTitle("KotlinForge — Kotlin Code Forge")
        self.resize(1100, 800)

        #fields
        self._last_topic = ""
        self._last_model_key = ""
        self.recent_block = ""
        self.memory_block = ""

        #widgets/fields/layout
        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)

        #build UI/populate models
        self._build_ui()
        self._populate_models()

    # -------------------------
    # UI
    # -------------------------
    def _build_ui(self):
        layout = self.layout

        ##--- Model selector ---##
        model_row = QHBoxLayout()
        model_label = QLabel("Model:")
        self.model_select = QComboBox()
        model_row.addWidget(model_label)
        model_row.addWidget(self.model_select)
        layout.addLayout(model_row)

        ###--- Tabs ---###
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, stretch=4)

        #--- Tab 1: Topic / Corrections ---#
        topic_widget = QWidget()
        topic_layout = QVBoxLayout(topic_widget)
        #topic window
        topic_label = QLabel("Forge Topic (Kotlin code or instructions):")
        self.topic_edit = QTextEdit()
        self.topic_edit.setPlaceholderText(
            "Describe what you want to forge, refactor, or enhance.\n"
            "You can paste full Kotlin code or package layout here as the topic."
        )
        #corrections window
        corrections_label = QLabel("Corrections / Guidance for Next Run:")
        self.corrections_edit = QTextEdit()
        self.corrections_edit.setPlaceholderText(
            "Write corrections, refinements, or additional requirements here."
        )
        #layout
        topic_layout.addWidget(topic_label)
        topic_layout.addWidget(self.topic_edit, stretch=3)
        topic_layout.addWidget(corrections_label)
        topic_layout.addWidget(self.corrections_edit, stretch=2)
        self.tabs.addTab(topic_widget, "Topic / Corrections")

        #--- Tab 2: Raw LLM Output ---#
        self.llm_output_edit = QTextEdit()
        self.llm_output_edit.setReadOnly(True)
        #RAW LLM output window
        self.llm_output_edit.setPlaceholderText("Raw LLM output will appear here.")
        self.tabs.addTab(self.llm_output_edit, "Raw LLM Output")

        #--- Tab 3: Extracted Code ---#
        self.extracted_code_edit = QTextEdit()
        #extracted code window
        self.extracted_code_edit.setPlaceholderText(
            "Extracted Kotlin code from LLM output and Deep Analysis will appear here.\n"
            "Use this as a staging area, then move curated code into 'Master Code'."
        )
        self.tabs.addTab(self.extracted_code_edit, "Extracted Code")

        #--- Tab 4: Master Code ---#
        self.master_code_edit = QTextEdit()
        self.master_code_edit.setPlaceholderText(
            "This is your primary working area.\n"
            "- Opened files load here.\n"
            "- Save writes from here.\n"
            "- You can organize, comment, and refine code here."
        )
        self.tabs.addTab(self.master_code_edit, "Master Code")

        #--- Tab 5: Deep Analysis Log ---#
        self.deep_log_edit = QTextEdit()
        self.deep_log_edit.setReadOnly(True)
        #deep analysis log window
        self.deep_log_edit.setPlaceholderText("Deep Analysis v2 event log will appear here.")
        self.tabs.addTab(self.deep_log_edit, "Deep Analysis Log")

        ###--- Global buttons ---###
        button_row = QHBoxLayout()
        #generate button
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self._on_generate_clicked)
        #rerun button
        self.rerun_button = QPushButton("Re-run with Corrections")
        self.rerun_button.clicked.connect(self._on_rerun_clicked)
        #deep analysis button
        self.deepanalyze_button = QPushButton("Deep Analysis")
        self.deepanalyze_button.clicked.connect(self._on_deep_analysis_clicked)
        #open file button
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self._on_open_clicked)
        #save file button
        self.save_button = QPushButton("Save File")
        self.save_button.clicked.connect(self._on_save_clicked)
        #forge to pending button
        self.approve_button = QPushButton("Forge → Pending")
        self.approve_button.clicked.connect(self._on_approve_clicked)
        #Clear ALL button
        self.clear_button = QPushButton("Clear (New Session)")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        #button layout
        button_row.addWidget(self.generate_button)
        button_row.addWidget(self.rerun_button)
        button_row.addWidget(self.deepanalyze_button)
        button_row.addWidget(self.open_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.approve_button)
        button_row.addWidget(self.clear_button)
        layout.addLayout(button_row)

        # Status
        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)

    # -------------------------
    # Populate models
    # -------------------------
    def _populate_models(self):
        models = self.llm.get_available_models()
        for m in models:
            key = m.get("key")
            if key:
                self.model_select.addItem(key)
        if self.model_select.count() > 0:
            self.model_select.setCurrentIndex(0)

# ==================================================================
# Events
# ==================================================================
    # -------------------------
    # On Generate Clicked
    # -------------------------
    def _on_generate_clicked(self):
        topic = self.topic_edit.toPlainText().strip()
        if not topic:
            QMessageBox.warning(self, "KotlinForge", "Please enter a forge topic.")
            return
        self._run_forge(topic, use_feedback=False)
    # -------------------------
    # On ReRun Clicked
    # -------------------------
    def _on_rerun_clicked(self):
        topic = self.topic_edit.toPlainText().strip()
        if not topic and not self._last_topic:
            QMessageBox.warning(self, "KotlinForge", "No topic available.")
            return

        if topic:
            self._last_topic = topic

        feedback = self.corrections_edit.toPlainText().strip()
        if feedback:
            self.memory_block += f"\n[Correction at {datetime.utcnow().isoformat()}Z]\n{feedback}\n"
            self.memory_block = self._trim_block(self.memory_block, 6000)

        self._run_forge(self._last_topic, use_feedback=True)

    # -------------------------
    # On Clear Clicked
    # -------------------------
    def _on_clear_clicked(self):
        self.topic_edit.clear()
        self.corrections_edit.clear()
        self.llm_output_edit.clear()
        self.extracted_code_edit.clear()
        self.master_code_edit.clear()
        self.deep_log_edit.clear()

        self._last_topic = ""
        self._last_model_key = ""
        self.recent_block = ""
        self.memory_block = ""

        self.status_label.setText("Cleared. New session.")

    # -------------------------
    # On Approve Clicked
    # -------------------------
    def _on_approve_clicked(self):
        code = self.master_code_edit.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "KotlinForge", "No code in Master Code.")
            return

        topic = self._last_topic or self.topic_edit.toPlainText().strip()
        if not topic:
            QMessageBox.warning(self, "KotlinForge", "No topic available.")
            return

        filename = self._infer_filename(topic)
        ok = self.forge_writer.forge_script(filename, code, purpose=topic)

        if ok:
            self.status_label.setText(f"Script '{filename}' forged to pending.")
        else:
            self.status_label.setText("Forge failed: write error.")

    # -------------------------
    # On Save Clicked
    # -------------------------
    def _on_save_clicked(self):
        code = self.master_code_edit.toPlainText()
        if not code.strip():
            QMessageBox.warning(self, "KotlinForge", "No code to save.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Kotlin File",
            "",
            "Kotlin Files (*.kt)",
        )
        if filename:
            Path(filename).write_text(code, encoding="utf-8")
            self.status_label.setText(f"Saved to {filename}")

    # -------------------------
    # On Open Clicked
    # -------------------------
    def _on_open_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Kotlin File",
            "",
            "Kotlin Files (*.kt)",
        )
        if not filename:
            return

        try:
            file_code = Path(filename).read_text(encoding="utf-8")
        except Exception as e:
            QMessageBox.critical(self, "KotlinForge", f"Failed to open file: {e}")
            return

        self.master_code_edit.setPlainText(file_code)
        self.status_label.setText(f"Loaded: {filename}")

    # -------------------------
    # On Deep Analysis Clicked
    # -------------------------
    def _on_deep_analysis_clicked(self):
        code = self.master_code_edit.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "KotlinForge", "No code to analyze.")
            return

        model_key = self.model_select.currentText().strip()
        engine = DeepAnalysisEngine(
            prompt_builder=self.prompt_builder,
            llm_engine=self.llm,
            model_fast=model_key,
            model_smart=model_key,
        )

        corrected = engine.run(code)

        # Log
        log_entries = engine.get_log()
        log_text = ""
        for entry in log_entries:
            stage = entry.get("stage", "unknown")
            msg = entry.get("message", "")
            extra = {k: v for k, v in entry.items() if k not in ("stage", "message")}
            log_text += f"[{stage}] {msg}\n"
            if extra:
                log_text += f"    {extra}\n"

        self.deep_log_edit.setPlainText(log_text.strip())

        if not corrected or not corrected.strip():
            QMessageBox.warning(self, "KotlinForge", "Deep Analysis produced no corrected code.")
            return

        existing = self.extracted_code_edit.toPlainText().strip()
        merged = (
            existing
            + "\n\n// --- Deep Analysis Correction Pass ---\n\n"
            + corrected
            if existing
            else "// --- Deep Analysis Correction Pass ---\n\n" + corrected
        )

        self.extracted_code_edit.setPlainText(merged)
        self.status_label.setText("Deep Analysis complete.")

    # -------------------------
    # Core forge logic
    # -------------------------
    def _run_forge(self, topic: str, use_feedback: bool):
        self.status_label.setText("Generating...")
        self.llm_output_edit.clear()

        model_key = self.model_select.currentText().strip()
        self._last_topic = topic
        self._last_model_key = model_key

        if use_feedback:
            full_topic = (
                f"{topic}\n\n"
                f"Previous code:\n{self.master_code_edit.toPlainText()}\n\n"
                f"Corrections:\n{self.corrections_edit.toPlainText()}\n"
            )
        else:
            full_topic = topic

        prompt = self.prompt_builder.build_prompt(full_topic, model_key)
        raw = self.llm.generate(prompt, model_key=model_key)

        self.llm_output_edit.setPlainText(raw)

        code = self._extract_code(raw)
        if not code:
            self.status_label.setText("No valid Kotlin code found.")
            QMessageBox.warning(self, "KotlinForge", "No valid Kotlin code found.")
            return

        existing = self.extracted_code_edit.toPlainText().strip()
        merged = (
            existing + "\n\n// --- Next Forge Pass ---\n\n" + code
            if existing
            else code
        )

        self.extracted_code_edit.setPlainText(merged)
        self.status_label.setText("Generation complete.")

# ================================================================
# Helpers
# ================================================================
    # -------------------------
    # Extract Code
    # -------------------------
    def _extract_code(self, raw: str):
        if not raw:
            return None

        # Kotlin anchors:
        match = re.search(
            r"^(package\s+[A-Za-z0-9_.]+|class\s+[A-Za-z0-9_]+|object\s+[A-Za-z0-9_]+|"
            r"interface\s+[A-Za-z0-9_]+|data\s+class\s+[A-Za-z0-9_]+|fun\s+[A-Za-z0-9_]+\s*\()",
            raw,
            flags=re.MULTILINE,
        )

        if not match:
            return raw.strip() if raw.strip().startswith("//") else None

        return raw[match.start():].strip()

    # -------------------------
    # Infer Filename
    # -------------------------
    def _infer_filename(self, topic: str) -> str:
        """
        Infer a Kotlin filename from the topic.
        """
        t = topic.lower()

        if "viewmodel" in t:
            return "MainViewModel.kt"
        if "repository" in t:
            return "MainRepository.kt"
        if "utils" in t:
            return "Utils.kt"

        return "Main.kt"

    # -------------------------
    # Trim Block
    # -------------------------
    def _trim_block(self, text: str, max_chars: int) -> str:
        return text if len(text) <= max_chars else text[-max_chars:]

